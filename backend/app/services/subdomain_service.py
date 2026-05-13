import json
import subprocess
from urllib.parse import urlparse
from sqlmodel import Session
from app.models.subdomain import SubdomainResult


def extract_domain(url: str) -> str:
    parsed = urlparse(url)
    if parsed.netloc:
        return parsed.netloc
    # スキームなしのURL (例: example.com) はそのまま返す
    return url.split("/")[0]


def run_subfinder(domain: str, options: dict) -> list[dict]:
    timeout = str(options.get("timeout", 30))
    threads = str(options.get("threads", 10))

    cmd = [
        "subfinder", "-d", domain,
        "-oJ",
        "-silent",
        "-t", threads,
        "-timeout", timeout,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    return _parse_subfinder(result.stdout)


def _parse_subfinder(raw: str) -> list[dict]:
    results = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            results.append({
                "domain": obj.get("host", ""),
                "source": obj.get("source", ""),
            })
        except json.JSONDecodeError:
            # -oJ なしのプレーンテキスト出力にも対応
            results.append({"domain": line, "source": ""})
    return results


def save_subdomain_results(scan_id: int, results: list[dict], db: Session):
    for r in results:
        db.add(SubdomainResult(scan_id=scan_id, **r))
    db.commit()
