import subprocess
from pathlib import Path

from src.config import WORKDIR


def run_bash(command: str, cwd: Path = None,
             run_in_background: bool = False) -> str:
    try:
        r = subprocess.run(command, shell=True, cwd=cwd or WORKDIR,
                           capture_output=True, text=True, timeout=120)
        out = (r.stdout + r.stderr).strip()
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"