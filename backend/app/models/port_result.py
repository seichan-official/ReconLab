from sqlmodel import Field, SQLModel


class PortResult(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    scan_id: int = Field(foreign_key="scan.id")
    port: int
    protocol: str
    state: str
    service: str
    version: str = ""
