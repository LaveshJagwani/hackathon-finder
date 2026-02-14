from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class HackathonResponse(BaseModel):
    id: int
    name: str
    url: str

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    registration_deadline: Optional[datetime] = None

    is_online: Optional[bool] = None
    participants_count: Optional[int] = None

    themes: Optional[str] = None

    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    location_text: Optional[str] = None

    source: Optional[str] = None

    class Config:
        from_attributes = True  # SQLAlchemy support
