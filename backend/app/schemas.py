from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ServiceItem(BaseModel):
    title: str
    price_from: int = Field(ge=0)


class PriceCategory(BaseModel):
    key: str
    title: str
    accent: str
    items: list[ServiceItem]


class LeadCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=6, max_length=30)
    comment: str = Field(default="", max_length=1000)


class LeadRecord(LeadCreate):
    id: str
    created_at: datetime
    status: Literal["new", "done"] = "new"
    done_at: datetime | None = None
    tg_message_id: int | None = None
