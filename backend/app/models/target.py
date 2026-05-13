from sqlmodel import Field, SQLModel
from datetime import datetime


class Target(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
