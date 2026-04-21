import json
from datetime import datetime, timedelta, timezone
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


def _parse_dt(value: str | None) -> datetime:
    if not value:
        return datetime.min.replace(tzinfo=timezone.utc)
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


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


def mark_lead_active(lead_id: str) -> LeadRecord | None:
    data = _read_leads_raw()
    updated: LeadRecord | None = None
    for item in data:
        if item.get("id") != lead_id:
            continue
        if item.get("status") != "done":
            updated = LeadRecord.model_validate(item)
            break
        item["status"] = "new"
        item["done_at"] = None
        updated = LeadRecord.model_validate(item)
        break
    if updated is None:
        return None
    _write_leads_raw(data)
    return updated


def list_active_leads() -> list[LeadRecord]:
    data = _read_leads_raw()
    active = [LeadRecord.model_validate(item) for item in data if item.get("status") != "done"]
    active.sort(key=lambda lead: lead.created_at, reverse=True)
    return active


def list_archived_leads() -> list[LeadRecord]:
    data = _read_leads_raw()
    archived = [LeadRecord.model_validate(item) for item in data if item.get("status") == "done"]
    archived.sort(
        key=lambda lead: lead.done_at or lead.created_at,
        reverse=True,
    )
    return archived


def cleanup_old_archived_leads() -> int:
    data = _read_leads_raw()
    threshold = datetime.now(timezone.utc) - timedelta(days=365)
    original_count = len(data)
    kept = []
    for item in data:
        if item.get("status") != "done":
            kept.append(item)
            continue
        done_at = _parse_dt(item.get("done_at"))
        if done_at >= threshold:
            kept.append(item)
    removed = original_count - len(kept)
    if removed > 0:
        _write_leads_raw(kept)
    return removed


def update_service_price(category_key: str, item_key: str, new_price: int) -> bool:
    _ensure_data_files()
    data = json.loads(PRICES_PATH.read_text(encoding="utf-8"))
    updated = False
    for category in data:
        if category.get("key") != category_key:
            continue
        for item in category.get("items", []):
            if item.get("key") == item_key:
                item["price_from"] = new_price
                updated = True
                break
        break
    if not updated:
        return False
    PRICES_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return True
