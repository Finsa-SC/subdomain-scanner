from pathlib import Path

import sys

from models.signatures import TITLE_IGNORE
from .logger import get_logger
import platform, os, subprocess

log = get_logger("screenshotter")

screenshot_dir = Path("results") / "screenshots"

def can_screenshot(result: dict) -> tuple[bool, str]:
    http = result.get("http", {})
    https = result.get("https", {})

    h_status = http.get("status")
    s_status = https.get("status")
    h_size = http.get("size")
    s_size = https.get("size")
    h_title = (http.get("title") or "").lower().strip()
    s_title = (https.get("title") or "").lower().strip()

    if h_status != 200 and s_status != 200:
        return False, f"Not a live host (HTTP: {h_status}, HTTPS: {s_status})"

    size = h_size if h_status == 200 else s_size
    if not size or size <= 100:
        return False, f"Response is too small ({size} bytes)"

    title = h_title if h_status == 200 else s_title
    for junk in TITLE_IGNORE:
        if junk in title:
            return False, f"Title generic: '{title}'"

    return True, ""

def _pick_url(result: dict) -> str:
    subdomain = result.get("subdomain", "")
    if result.get("https", {}).get("status") == 200:
        return f"https://{subdomain}"
    return f"http://{subdomain}"

def take_screenshot(result: dict, open_image: bool = False):
    ok, reason = can_screenshot(result)
    if not ok:
        return False, reason

    subdomain = result.get("subdomain", "")
    url = _pick_url(result)

    save_name = subdomain.replace(".", "_").replace("/", "_")
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    out_path = screenshot_dir / f"{save_name}.png"

    try:
        p, browser = ensure_chromium()

        page = browser.new_page()
        page.goto(url, timeout=15000, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        page.screenshot(path=str(out_path), full_page=True)

        browser.close()
        p.stop()

        if open_image:
            open_image_popup(str(out_path))

        return True, str(out_path)

    except Exception as e:
        return False, str(e)

def open_image_popup(path: str):
    if platform.system() == 'Linux':
        subprocess.Popen(["xdg-open", path])
    elif platform.system() == 'Darwin':
        subprocess.run(["open", path])
    elif platform.system() == 'Windows':
        os.startfile(path)

def ensure_chromium():
    from playwright.sync_api import sync_playwright
    try:
        play = sync_playwright().start()
        browser = play.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        return play, browser
    except Exception:
        log.error("Chromium not found! Installing...")
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True
        )
        log.info("Chromium installed!")
        play = sync_playwright().start()
        browser = play.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        return play, browser