from sqlmodel import Session, select
from app.models.scan import Scan
from app.services.recon_service import run_gobuster, save_dir_results
from app.services.subdomain_service import extract_domain, run_subfinder, save_subdomain_results
from app.services.http_probe_service import run_httpx, get_subdomains_for_scan, save_http_probe_results


def execute_gobuster_scan(scan_id: int, target_url: str, options: dict, db: Session):
    scan = db.exec(select(Scan).where(Scan.id == scan_id)).first()
    scan.status = "running"
    db.commit()

    try:
        results = run_gobuster(target_url, options)
        save_dir_results(scan_id, results, db)
        scan.status = "done"
    except Exception as e:
        scan.status = "error"
        scan.error_message = str(e)
    finally:
        db.commit()


def execute_subfinder_scan(scan_id: int, target_url: str, options: dict, db: Session):
    scan = db.exec(select(Scan).where(Scan.id == scan_id)).first()
    scan.status = "running"
    db.commit()

    try:
        domain = extract_domain(target_url)
        results = run_subfinder(domain, options)
        save_subdomain_results(scan_id, results, db)
        scan.status = "done"
    except Exception as e:
        scan.status = "error"
        scan.error_message = str(e)
    finally:
        db.commit()


def execute_httpx_scan(scan_id: int, target_url: str, options: dict, db: Session):
    scan = db.exec(select(Scan).where(Scan.id == scan_id)).first()
    scan.status = "running"
    db.commit()

    try:
        source_scan_id = options.get("source_scan_id")
        if source_scan_id:
            targets = get_subdomains_for_scan(source_scan_id, db)
        else:
            targets = [target_url]

        results = run_httpx(targets, options)
        save_http_probe_results(scan_id, results, db)
        scan.status = "done"
    except Exception as e:
        scan.status = "error"
        scan.error_message = str(e)
    finally:
        db.commit()
