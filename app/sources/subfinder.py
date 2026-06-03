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

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if process.stdout:
            for line in process.stdout:
                sub = line.strip().lower()
                if sub:
                    yield sub

        process.wait()

    except Exception as e:
        log.error(f"Unexpected error in subfinder module: {e}")