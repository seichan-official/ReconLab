from pydantic import BaseModel
from datetime import datetime


class ScanCreate(BaseModel):
    target_id: int
    tool: str = "nmap"


class ScanResponse(BaseModel):
    id: int
    target_id: int
    tool: str
    status: str
    error_message: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class ScanRequest(BaseModel):
    target_id: int
    tool: str = "nmap"
    options: dict = {}


class GobusterOptions(BaseModel):
    wordlist: str = "/usr/share/wordlists/dirb/common.txt"
    mode: str = "dir"
    extensions: str = ""
    threads: int = 10


class DirResultSchema(BaseModel):
    path: str
    status_code: int
    size: int | None

    class Config:
        from_attributes = True
