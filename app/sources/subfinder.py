from utils import get_logger
import shutil
import subprocess

def fetch_subfinder(domain: str):
    log = get_logger("Subfinder source")

    if not shutil.which("subfinder"):
        log.error("Subfinder binary not found in PATH. Please install it.")
        return

    try:
        cmd = ["subfinder", "-d", domain, "-all", "-silent"]

        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if process.returncode == 0 and process.stdout:
            for lines in process.stdout:
                sub = lines.strip().lower()
                if sub:
                    yield sub

    except Exception as e:
        log.error(f"Unexpected error in subfinder module: {e}")