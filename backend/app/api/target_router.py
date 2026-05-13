from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session

from app.core.db import get_session
from app.schemas.target_schema import TargetCreate, TargetResponse
from app.services.target_service import create_target, get_target, list_targets, delete_target

router = APIRouter(prefix="/targets", tags=["targets"])


@router.post("", response_model=TargetResponse, status_code=201)
def create(body: TargetCreate, db: Session = Depends(get_session)):
    return create_target(body.url, db)


@router.get("", response_model=list[TargetResponse])
def list_all(db: Session = Depends(get_session)):
    return list_targets(db)


@router.get("/{target_id}", response_model=TargetResponse)
def get_one(target_id: int, db: Session = Depends(get_session)):
    target = get_target(target_id, db)
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    return target


@router.delete("/{target_id}", status_code=204)
def delete(target_id: int, db: Session = Depends(get_session)):
    if not delete_target(target_id, db):
        raise HTTPException(status_code=404, detail="Target not found")
