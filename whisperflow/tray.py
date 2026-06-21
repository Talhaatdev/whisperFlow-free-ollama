"""System tray icon (pystray) with a small menu.

Runs in its own thread. Menu callbacks are plain Python; anything touching
the GUI is delegated back to the app, which marshals onto the Tk thread.
"""

from __future__ import annotations

import threading
from typing import Callable

import pystray
from PIL import Image, ImageDraw


def _make_icon_image() -> Image.Image:
    """Draw a simple microphone glyph as the tray icon (64x64)."""
    img = Image.new("RGBA", (64, 64), (30, 30, 46, 0))
    d = ImageDraw.Draw(img)
    # Mic capsule
    d.rounded_rectangle([26, 12, 38, 40], radius=6, fill=(166, 227, 161, 255))
    # Mic stand arc
    d.arc([20, 26, 44, 50], start=20, end=160, width=3, fill=(166, 227, 161, 255))
    # Stem + base
    d.line([32, 50, 32, 56], width=3, fill=(166, 227, 161, 255))
    d.line([24, 56, 40, 56], width=3, fill=(166, 227, 161, 255))
    return img


class TrayIcon:
    """Wraps a pystray.Icon and exposes start/stop + notify."""

    def __init__(
        self,
        app_name: str,
        on_quit: Callable[[], None],
        on_show_history: Callable[[], None],
        on_toggle_autostart: Callable[[], None] | None = None,
        autostart_enabled: Callable[[], bool] | None = None,
        autostart_supported: bool = False,
    ) -> None:
        self._on_quit = on_quit
        self._on_show_history = on_show_history
        self._on_toggle_autostart = on_toggle_autostart
        self._autostart_enabled = autostart_enabled or (lambda: False)
        self._thread: threading.Thread | None = None

        menu_items = [
            pystray.MenuItem("WhisperFlow — Ctrl+Shift+Z to record", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Show history", lambda *_: self._on_show_history()),
        ]
        if autostart_supported and on_toggle_autostart is not None:
            menu_items.append(
                pystray.MenuItem(
                    "Start with Windows",
                    lambda *_: self._on_toggle_autostart(),
                    checked=lambda _item: self._autostart_enabled(),
                )
            )
        menu_items += [
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", lambda *_: self._on_quit()),
        ]

        self.icon = pystray.Icon(
            name=app_name,
            icon=_make_icon_image(),
            title=app_name,
            menu=pystray.Menu(*menu_items),
        )

    def start(self) -> None:
        """Run the tray icon loop in a background thread."""
        self._thread = threading.Thread(target=self.icon.run, daemon=True)
        self._thread.start()

    def notify(self, message: str, title: str = "WhisperFlow") -> None:
        """Show a native balloon notification (best-effort)."""
        try:
            self.icon.notify(message, title)
        except Exception:
            # Many Linux tray backends don't support balloon notifications.
            # That's fine — the on-screen tkinter toast already showed the result.
            pass

    def stop(self) -> None:
        try:
            self.icon.stop()
        except Exception:
            pass
