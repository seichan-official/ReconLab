from fastapi import FastAPI
from app.api.scan_router import router as scan_router

app = FastAPI()

app.include_router(scan_router)