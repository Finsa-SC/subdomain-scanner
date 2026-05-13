from concurrent.futures import ThreadPoolExecutor
from utils import get_logger

log = get_logger("deep_scan")

PENDING  = "pending"
RUNNING  = "running"
DONE     = "done"
ERROR    = "error"

def _run_favicon(result: dict, timeout: float) -> dict:
    from utils import fetch_favicon
    return fetch_favicon(result, timeout)

def _run_tech_version(result: dict, timeout: float) -> dict:
    from .tech_version import detect_version
    return detect_version(result, timeout)

