from pydantic import BaseModel


class HttpxOptions(BaseModel):
    source_scan_id: int | None = None
    timeout: int = 10
    threads: int = 50


class HttpProbeResultSchema(BaseModel):
    url: str
    status_code: int | None
    title: str | None
    content_length: int | None
    response_time_ms: float | None
    webserver: str | None

    class Config:
        from_attributes = True
