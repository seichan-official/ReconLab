from sqlmodel import Field, SQLModel


class DirResult(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    scan_id: int = Field(foreign_key="scan.id")
    path: str
    status_code: int
    size: int | None = None
