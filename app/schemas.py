from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl


class LinkCreate(BaseModel):
    url: HttpUrl


class LinkCreated(BaseModel):
    code: str
    short_url: str


class LinkStats(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    target_url: str
    clicks: int
    created_at: datetime
