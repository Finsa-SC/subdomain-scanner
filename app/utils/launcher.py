import subprocess, platform, os, shutil
from dotenv import load_dotenv
from .logger import get_logger

log = get_logger("Launcher")
load_dotenv()
DEBUG = os.getenv("DEBUG", '').lower().strip() == 'true'

COMMAND_TEMPLATES = {
    "nmap_quick": "nmap -T4 -F {target}",
    "nmap_full": "nmap -sV -sC -p- {target}",
    "ffuf_dir": "ffuf -u https://{target}/FUZZ -w /usr/share/wordlists/dirb/common.txt",
    "ffuf_json": "ffuf -u https://{target} -X POST -H 'Content-Type: application/json' -d 'FUZZ'",
    "sqlmap": "sqlmap -u https://{target} --batch --banner",
    "whois": "whois {target}",
    "dig": "dig any {target} +short",
    "curl_head": "curl -I https://{target}"
}

def launch_terminal(action_key: str, target: str, custom_cmd: str = None):
    system = platform.system()
    if custom_cmd:
        full_cmd = custom_cmd
    else:
        template = COMMAND_TEMPLATES.get(action_key, "{target}")
        full_cmd = template.format(target=target)

    if system == 'Windows':
        return _launch_windows(full_cmd)
    elif system == 'Darwin':
        return _launch_macos(full_cmd)
    elif system == 'Linux':
        return _launch_linux(full_cmd)
    else:
        log.error(f"Unsupported platform: {system}")
        return False

def _launch_windows(cmd: str) -> bool:
    try:
        subprocess.Popen(
            ["cmd", "/k", cmd],
            shell=True)
        return True
    except Exception as e:
        log.error(f"Windows launch Failed: {e}")
        return False

def _launch_macos(cmd: str) -> bool:
    try:
        script = f'tell application "Terminal" to do script "{cmd}"'
        subprocess.Popen(["osascript", "-e", script])
        return True
    except Exception as e:
        log.error(f"macOs launch failed: {e}")
        return False

def _launch_linux(cmd: str) -> bool:
    shell = "fish" if shutil.which("fish") else "bash"
    terminals = [
        ["alacritty", "-e", shell, "-c", f"{cmd}; read"],
        ["konsole", "--noclose", "-e", shell, "-c", cmd],
        ["kitty", shell, "-c", f"{cmd}; read"],
        ["wezterm", "start", "--", shell, "-c", f"{cmd}; read"],
        ["terminator", "-e", f"{shell} -c '{cmd}; read'"],
        ["xfce4-terminal", "--hold", "-e", f"{shell} -c '{cmd}'"],
        ["xterm", "-hold", "-e", f"{shell} -c '{cmd}'"],
        ["st", "-e", shell, "-c", f"{cmd}; read"],
        ["foot", shell, "-c", f"{cmd}; read"],
    ]

    for term in terminals:
        try:
            subprocess.Popen(
                term,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            if DEBUG:
                log.debug(f"Launched with {term[0]}")
            return True
        except FileNotFoundError:
            continue
        except Exception as e:
            log.error(f"Failed with {term[0]}: {e}")
            continue
    return False