import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .config import settings
from .schemas import LeadCreate, LeadRecord, PriceCategory


DATA_DIR = Path(settings.data_dir)
PRICES_PATH = DATA_DIR / "prices.json"
LEADS_PATH = DATA_DIR / "leads.json"


def _ensure_data_files() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not LEADS_PATH.exists():
        LEADS_PATH.write_text("[]", encoding="utf-8")


def read_prices() -> list[PriceCategory]:
    _ensure_data_files()
    raw = json.loads(PRICES_PATH.read_text(encoding="utf-8"))
    return [PriceCategory.model_validate(item) for item in raw]


def _read_leads_raw() -> list[dict]:
    _ensure_data_files()
    raw = json.loads(LEADS_PATH.read_text(encoding="utf-8"))
    normalized: list[dict] = []
    for item in raw:
        item.setdefault("status", "new")
        item.setdefault("done_at", None)
        item.setdefault("tg_message_id", None)
        normalized.append(item)
    return normalized


def _write_leads_raw(data: list[dict]) -> None:
    LEADS_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def append_lead(payload: LeadCreate) -> LeadRecord:
    data = _read_leads_raw()
    record = LeadRecord(
        id=str(uuid4()),
        created_at=datetime.now(timezone.utc),
        **payload.model_dump(),
    )
    data.append(record.model_dump(mode="json"))
    _write_leads_raw(data)
    return record


def set_tg_message_id(lead_id: str, message_id: int) -> LeadRecord | None:
    data = _read_leads_raw()
    updated: LeadRecord | None = None
    for item in data:
        if item.get("id") == lead_id:
            item["tg_message_id"] = message_id
            updated = LeadRecord.model_validate(item)
            break
    if updated is None:
        return None
    _write_leads_raw(data)
    return updated


def mark_lead_done(lead_id: str) -> LeadRecord | None:
    data = _read_leads_raw()
    updated: LeadRecord | None = None
    for item in data:
        if item.get("id") != lead_id:
            continue
        if item.get("status") == "done":
            updated = LeadRecord.model_validate(item)
            break
        item["status"] = "done"
        item["done_at"] = datetime.now(timezone.utc).isoformat()
        updated = LeadRecord.model_validate(item)
        break
    if updated is None:
        return None
    _write_leads_raw(data)
    return updated
