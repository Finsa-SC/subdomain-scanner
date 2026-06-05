import os, subprocess, platform
from pathlib import Path
from .logger import get_logger
from models.scan_config import DARWIN_EDITOR, LINUX_EDITOR, WINDOWS_EDITOR

log = get_logger("Editor")

def open_in_editor(filepath: Path):
    if not filepath.exists():
        log.error("No such file found")
        print("No such file found")
        return

    system = platform.system().lower()

    if system == "linux":
        editor = LINUX_EDITOR
    elif system == "windows":
        editor = WINDOWS_EDITOR
    elif system == "darwin":
        editor = DARWIN_EDITOR
    else:
        log.error("No text editor found")
        print("No text editor found")
        return

    editor_cmd = editor.split()
    editor_cmd.append(str(filepath))

    try:
        subprocess.run(editor_cmd, check=True)
    except FileNotFoundError:
        log.error(f"Editor command '{editor_cmd[0]}' not found. Check your config.")
    except Exception as e:
        log.error(f"Failed to open editor: {e}")