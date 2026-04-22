import asyncio

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .schemas import AppSettings, LeadCreate, LeadRecord, PriceCategory
from .storage import append_lead, read_contact_phone, read_prices
from .telegram_notifier import cleanup_archived_daily, close_bot, notify_owner, run_polling

app = FastAPI(title="ClearSpace API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.on_event("startup")
async def startup_event() -> None:
    app.state.polling_task = asyncio.create_task(run_polling())
    app.state.cleanup_task = asyncio.create_task(cleanup_archived_daily())


@app.on_event("shutdown")
async def shutdown_event() -> None:
    polling_task = getattr(app.state, "polling_task", None)
    if polling_task:
        polling_task.cancel()
    cleanup_task = getattr(app.state, "cleanup_task", None)
    if cleanup_task:
        cleanup_task.cancel()
    await close_bot()


@app.get("/api/prices", response_model=list[PriceCategory])
async def get_prices() -> list[PriceCategory]:
    try:
        return read_prices()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail="prices.json not found") from exc


@app.get("/api/settings", response_model=AppSettings)
async def get_settings() -> AppSettings:
    try:
        return AppSettings(contact_phone=read_contact_phone())
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="Failed to load settings") from exc


@app.post("/api/leads", response_model=LeadRecord)
async def create_lead(payload: LeadCreate, background_tasks: BackgroundTasks) -> LeadRecord:
    try:
        lead = append_lead(payload)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="Failed to save lead") from exc

    background_tasks.add_task(notify_owner, lead)
    return lead
