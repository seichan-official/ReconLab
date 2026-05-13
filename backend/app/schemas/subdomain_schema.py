from pydantic import BaseModel


class SubfinderOptions(BaseModel):
    timeout: int = 30
    threads: int = 10


class SubdomainResultSchema(BaseModel):
    domain: str
    source: str

    class Config:
        from_attributes = True
