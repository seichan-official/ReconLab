import subprocess
from sqlmodel import Session
from app.models.dir_result import DirResult


def run_gobuster(target_url: str, options: dict) -> list[dict]:
    wordlist = options.get("wordlist", "/usr/share/wordlists/dirb/common.txt")
    mode = options.get("mode", "dir")
    ext = options.get("extensions", "")
    threads = str(options.get("threads", 10))

    cmd = [
        "gobuster", mode,
        "-u", target_url,
        "-w", wordlist,
        "-t", threads,
        "--no-color",
    ]
    if ext:
        cmd += ["-x", ext]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return _parse_gobuster(result.stdout)


def _parse_gobuster(raw: str) -> list[dict]:
    results = []
    for line in raw.splitlines():
        # 例: /admin                (Status: 200) [Size: 1234]
        if not line.startswith("/"):
            continue
        parts = line.split()
        path = parts[0]
        status = 0
        size = None
        for i, p in enumerate(parts):
            if p == "(Status:":
                status = int(parts[i + 1].strip(")"))
            if p == "[Size:":
                size = int(parts[i + 1].strip("]"))
        results.append({"path": path, "status_code": status, "size": size})
    return results


def save_dir_results(scan_id: int, results: list[dict], db: Session):
    for r in results:
        db.add(DirResult(scan_id=scan_id, **r))
    db.commit()
