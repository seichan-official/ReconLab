from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.db import init_db
from app.api.scan_router import router as scan_router
from app.api.target_router import router as target_router
from app.api.result_router import router as result_router

# 全モデルをインポートしてSQLModelのメタデータに登録する（テーブル自動生成のため）
import app.models.scan  # noqa: F401
import app.models.target  # noqa: F401
import app.models.port_result  # noqa: F401
import app.models.dir_result  # noqa: F401
import app.models.subdomain  # noqa: F401
import app.models.http_probe_result  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(target_router)
app.include_router(scan_router)
app.include_router(result_router)
