from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import subprocess

router = APIRouter()


class ScanRequest(BaseModel):
    target: str


@router.post("/scan")

# ターゲット入力
def start_scan(request: ScanRequest):

    raw = run_nmap(request.target)

    ports = parse_nmap(raw)

    return {
        "target": request.target,
        "ports": ports
    }

# スキャン開始
def run_nmap(target: str):
  try:
    result = subprocess.run(
        ["nmap", "-F", "-sV", "-sC", target],
        capture_output=True,
        text=True,
        timeout=120
    )
  # タイムアウトエラー
  except subprocess.TimeoutExpired:
    raise HTTPException(
        status_code=504,
        detail="nmap scan timeout"
    )
  # スキャン失敗
  if result.returncode != 0:
    raise HTTPException(
    status_code=500,
    detail="nmap scan failed"
  )

# json形式に変換
def parse_nmap(output: str):

    ports = []

    for line in output.splitlines():

        if "/tcp" in line or "/udp" in line:

            parts = line.split()
            
            if len(parts) < 3:
              continue
            
            port_proto = parts[0]
            state = parts[1]
            service = parts[2]

            port = int(port_proto.split("/")[0])
            proto = port_proto.split("/")[1]

            version = " ".join(parts[3:]) if len(parts) > 3 else ""

            ports.append({
                "port": port,
                "protocol": proto,
                "state": state,
                "service": service,
                "version": version
            })

    return ports