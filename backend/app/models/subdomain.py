from sqlmodel import Field, SQLModel
from datetime import datetime


class SubdomainResult(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    scan_id: int = Field(foreign_key="scan.id")
    domain: str
    source: str = ""
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
