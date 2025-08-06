# app/schemas.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class TicketBase(BaseModel):
    title: str
    description: str | None = None

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None

class TicketRead(TicketBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
