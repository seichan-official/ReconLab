from pydantic import BaseModel


class PortResultSchema(BaseModel):
    port: int
    protocol: str
    state: str
    service: str
    version: str

    class Config:
        from_attributes = True
