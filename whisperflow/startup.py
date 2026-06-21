"""Optional 'start with Windows' support via the HKCU Run registry key.

These functions are Windows-only and degrade gracefully elsewhere.
"""

from __future__ import annotations

import sys
from pathlib import Path

# winreg only exists on Windows.
try:
    import winreg  # type: ignore
except ImportError:  # pragma: no cover - non-Windows dev machines
    winreg = None  # type: ignore

_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_VALUE_NAME = "WhisperFlow"


def _launch_command() -> str:
    """Command Windows should run at login: pythonw.exe main.py (no console)."""
    project_root = Path(__file__).resolve().parent.parent
    main_py = project_root / "main.py"
    # Prefer pythonw.exe so no console window appears.
    py = Path(sys.executable)
    pyw = py.with_name("pythonw.exe")
    exe = pyw if pyw.exists() else py
    return f'"{exe}" "{main_py}"'


def is_supported() -> bool:
    return winreg is not None


def is_enabled() -> bool:
    if winreg is None:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY) as key:
            winreg.QueryValueEx(key, _VALUE_NAME)
            return True
    except FileNotFoundError:
        return False
    except OSError:
        return False


def enable() -> bool:
    """Register the app to start at login. Returns True on success."""
    if winreg is None:
        return False
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_SET_VALUE
        ) as key:
            winreg.SetValueEx(key, _VALUE_NAME, 0, winreg.REG_SZ, _launch_command())
        return True
    except OSError as exc:
        print(f"[startup] could not enable autostart: {exc}")
        return False


def disable() -> bool:
    """Remove the autostart entry. Returns True on success."""
    if winreg is None:
        return False
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_SET_VALUE
        ) as key:
            winreg.DeleteValue(key, _VALUE_NAME)
        return True
    except FileNotFoundError:
        return True  # already absent
    except OSError as exc:
        print(f"[startup] could not disable autostart: {exc}")
        return False
