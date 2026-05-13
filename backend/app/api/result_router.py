from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

from app.core.db import get_session
from app.models.scan import Scan
from app.models.dir_result import DirResult
from app.models.port_result import PortResult
from app.schemas.scan_schema import DirResultSchema
from app.schemas.port_schema import PortResultSchema

router = APIRouter()


@router.get("/scans/{scan_id}/dirs", response_model=list[DirResultSchema])
def get_dir_results(scan_id: int, db: Session = Depends(get_session)):
    scan = db.exec(select(Scan).where(Scan.id == scan_id)).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return db.exec(select(DirResult).where(DirResult.scan_id == scan_id)).all()


@router.get("/scans/{scan_id}/ports", response_model=list[PortResultSchema])
def get_port_results(scan_id: int, db: Session = Depends(get_session)):
    scan = db.exec(select(Scan).where(Scan.id == scan_id)).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return db.exec(select(PortResult).where(PortResult.scan_id == scan_id)).all()
