"""A tiny self-dismissing toast notification built with tkinter.

Used to confirm "Prompt copied!" and to surface errors. Avoids extra
dependencies and works the same on every platform tkinter supports.
"""

from __future__ import annotations

import tkinter as tk


class Toast:
    """Shows a transient message near the bottom-right of the screen."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root

    def show(self, message: str, duration_ms: int = 2500, error: bool = False) -> None:
        """Pop a toast. Must be called on the GUI thread."""
        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        try:
            win.attributes("-alpha", 0.95)
        except tk.TclError:
            pass

        bg = "#f38ba8" if error else "#1e1e2e"
        fg = "#11111b" if error else "#a6e3a1"

        frame = tk.Frame(win, bg=bg, padx=18, pady=12)
        frame.pack()
        tk.Label(
            frame,
            text=message,
            bg=bg,
            fg=fg,
            font=("Segoe UI", 11, "bold"),
            justify="left",
            wraplength=320,
        ).pack()

        # Position bottom-right.
        win.update_idletasks()
        w = win.winfo_width()
        h = win.winfo_height()
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        win.geometry(f"+{sw - w - 24}+{sh - h - 60}")

        win.after(duration_ms, win.destroy)
