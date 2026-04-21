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


def append_lead(payload: LeadCreate) -> LeadRecord:
    _ensure_data_files()
    data = json.loads(LEADS_PATH.read_text(encoding="utf-8"))
    record = LeadRecord(
        id=str(uuid4()),
        created_at=datetime.now(timezone.utc),
        **payload.model_dump(),
    )
    data.append(record.model_dump(mode="json"))
    LEADS_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return record
