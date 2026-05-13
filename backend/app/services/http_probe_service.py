import json
import subprocess
from sqlmodel import Session, select
from app.models.http_probe_result import HttpProbeResult
from app.models.subdomain import SubdomainResult


def run_httpx(targets: list[str], options: dict) -> list[dict]:
    timeout = str(options.get("timeout", 10))
    threads = str(options.get("threads", 50))

    cmd = [
        "httpx",
        "-json",
        "-silent",
        "-t", threads,
        "-timeout", timeout,
        "-title",
        "-web-server",
        "-content-length",
        "-response-time",
    ]

    input_data = "\n".join(targets)
    result = subprocess.run(
        cmd, input=input_data, capture_output=True, text=True, timeout=600
    )
    return _parse_httpx(result.stdout)


def _parse_httpx(raw: str) -> list[dict]:
    results = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            results.append({
                "url": obj.get("url", ""),
                "status_code": obj.get("status-code"),
                "title": obj.get("title"),
                "content_length": obj.get("content-length"),
                "response_time_ms": _parse_response_time(obj.get("response-time", "")),
                "webserver": obj.get("webserver"),
            })
        except json.JSONDecodeError:
            continue
    return results


def _parse_response_time(rt: str) -> float | None:
    if not rt:
        return None
    rt = rt.lower()
    try:
        if rt.endswith("ms"):
            return float(rt[:-2])
        if rt.endswith("s"):
            return float(rt[:-1]) * 1000
    except ValueError:
        pass
    return None


def get_subdomains_for_scan(scan_id: int, db: Session) -> list[str]:
    subdomains = db.exec(
        select(SubdomainResult).where(SubdomainResult.scan_id == scan_id)
    ).all()
    return [s.domain for s in subdomains]


def save_http_probe_results(scan_id: int, results: list[dict], db: Session):
    for r in results:
        db.add(HttpProbeResult(scan_id=scan_id, **r))
    db.commit()
