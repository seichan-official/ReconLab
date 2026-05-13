import subprocess
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.db import get_session
from app.models.scan import Scan
from app.models.target import Target
from app.models.subdomain import SubdomainResult
from app.models.http_probe_result import HttpProbeResult
from app.schemas.scan_schema import ScanCreate, ScanResponse, GobusterOptions
from app.schemas.subdomain_schema import SubfinderOptions, SubdomainResultSchema
from app.schemas.http_probe_schema import HttpxOptions, HttpProbeResultSchema
from app.services.scan_service import (
    execute_gobuster_scan,
    execute_subfinder_scan,
    execute_httpx_scan,
)

router = APIRouter()


class ScanRequest(BaseModel):
    target: str


# ── Scan CRUD ─────────────────────────────────────────────────────────────────

@router.post("/scans", response_model=ScanResponse, status_code=201)
def create_scan(body: ScanCreate, db: Session = Depends(get_session)):
    target = db.exec(select(Target).where(Target.id == body.target_id)).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    scan = Scan(target_id=body.target_id, tool=body.tool)
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan


@router.get("/scans/{scan_id}", response_model=ScanResponse)
def get_scan(scan_id: int, db: Session = Depends(get_session)):
    scan = db.exec(select(Scan).where(Scan.id == scan_id)).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


@router.get("/targets/{target_id}/scans", response_model=list[ScanResponse])
def list_scans_for_target(target_id: int, db: Session = Depends(get_session)):
    target = db.exec(select(Target).where(Target.id == target_id)).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    return db.exec(select(Scan).where(Scan.target_id == target_id)).all()


# ── Gobuster ──────────────────────────────────────────────────────────────────

@router.post("/scans/{scan_id}/gobuster")
def start_gobuster(
    scan_id: int,
    options: GobusterOptions,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_session),
):
    scan = db.exec(select(Scan).where(Scan.id == scan_id)).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    target = db.exec(select(Target).where(Target.id == scan.target_id)).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    background_tasks.add_task(
        execute_gobuster_scan,
        scan_id, target.url, options.model_dump(), db,
    )
    return {"message": "gobuster scan started", "scan_id": scan_id}


# ── Subfinder ─────────────────────────────────────────────────────────────────

@router.post("/scans/{scan_id}/subfinder")
def start_subfinder(
    scan_id: int,
    options: SubfinderOptions,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_session),
):
    scan = db.exec(select(Scan).where(Scan.id == scan_id)).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    target = db.exec(select(Target).where(Target.id == scan.target_id)).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    background_tasks.add_task(
        execute_subfinder_scan,
        scan_id, target.url, options.model_dump(), db,
    )
    return {"message": "subfinder scan started", "scan_id": scan_id}


@router.get("/scans/{scan_id}/subdomains", response_model=list[SubdomainResultSchema])
def get_subdomains(scan_id: int, db: Session = Depends(get_session)):
    scan = db.exec(select(Scan).where(Scan.id == scan_id)).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return db.exec(
        select(SubdomainResult).where(SubdomainResult.scan_id == scan_id)
    ).all()


# ── httpx ─────────────────────────────────────────────────────────────────────

@router.post("/scans/{scan_id}/httpx")
def start_httpx(
    scan_id: int,
    options: HttpxOptions,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_session),
):
    scan = db.exec(select(Scan).where(Scan.id == scan_id)).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    target = db.exec(select(Target).where(Target.id == scan.target_id)).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    background_tasks.add_task(
        execute_httpx_scan,
        scan_id, target.url, options.model_dump(), db,
    )
    return {"message": "httpx probe started", "scan_id": scan_id}


@router.get("/scans/{scan_id}/http-probes", response_model=list[HttpProbeResultSchema])
def get_http_probes(scan_id: int, db: Session = Depends(get_session)):
    scan = db.exec(select(Scan).where(Scan.id == scan_id)).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return db.exec(
        select(HttpProbeResult).where(HttpProbeResult.scan_id == scan_id)
    ).all()


# ── Nmap (legacy) ─────────────────────────────────────────────────────────────

@router.post("/scan")
def start_scan(request: ScanRequest):
    raw = run_nmap(request.target)
    ports = parse_nmap(raw)
    return {"target": request.target, "ports": ports}


def run_nmap(target: str) -> str:
    try:
        result = subprocess.run(
            ["nmap", "-F", "-sV", "-sC", target],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="nmap scan timeout")

    if result.returncode != 0:
        raise HTTPException(status_code=500, detail="nmap scan failed")
    return result.stdout


def parse_nmap(output: str) -> list[dict]:
    ports = []
    for line in output.splitlines():
        if "/tcp" not in line and "/udp" not in line:
            continue
        parts = line.split()
        if len(parts) < 3:
            continue
        port_num, proto = parts[0].split("/")
        ports.append({
            "port": int(port_num),
            "protocol": proto,
            "state": parts[1],
            "service": parts[2],
            "version": " ".join(parts[3:]) if len(parts) > 3 else "",
        })
    return ports
