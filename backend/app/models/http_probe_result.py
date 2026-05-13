from sqlmodel import Field, SQLModel
from datetime import datetime


class HttpProbeResult(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    scan_id: int = Field(foreign_key="scan.id")
    url: str
    status_code: int | None = None
    title: str | None = None
    content_length: int | None = None
    response_time_ms: float | None = None
    webserver: str | None = None
    probed_at: datetime = Field(default_factory=datetime.utcnow)
