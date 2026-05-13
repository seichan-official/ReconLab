from sqlmodel import Field, SQLModel
from datetime import datetime


class Scan(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    target_id: int = Field(foreign_key="target.id")
    tool: str = "nmap"
    status: str = "pending"
    error_message: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
