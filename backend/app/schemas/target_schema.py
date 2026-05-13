from pydantic import BaseModel
from datetime import datetime


class TargetCreate(BaseModel):
    url: str


class TargetResponse(BaseModel):
    id: int
    url: str
    created_at: datetime

    class Config:
        from_attributes = True
