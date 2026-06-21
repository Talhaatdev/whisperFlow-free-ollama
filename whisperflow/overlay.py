"""A small frameless floating microphone overlay drawn with tkinter.

Shows a pulsing mic indicator while recording, switches to a "thinking"
state while transcribing/enhancing, then hides. All tkinter calls must
happen on the main (GUI) thread; the app marshals calls via root.after().
"""

from __future__ import annotations

import tkinter as tk


class MicOverlay:
    """A borderless, always-on-top floating widget."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self._win: tk.Toplevel | None = None
        self._canvas: tk.Canvas | None = None
        self._label: tk.Label | None = None
        self._pulse_job: str | None = None
        self._pulse_grow = True
        self._pulse_r = 14

    # -- lifecycle ----------------------------------------------------------
    def _build(self) -> None:
        win = tk.Toplevel(self.root)
        win.overrideredirect(True)  # no title bar / borders
        win.attributes("-topmost", True)
        try:
            win.attributes("-alpha", 0.92)  # slight transparency
        except tk.TclError:
            pass  # not supported on every platform
        win.configure(bg="#1e1e2e")

        # Position: bottom-center of the primary screen.
        win.update_idletasks()
        w, h = 220, 70
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        x = (sw - w) // 2
        y = sh - h - 80
        win.geometry(f"{w}x{h}+{x}+{y}")

        # Pulsing red dot drawn on a canvas.
        canvas = tk.Canvas(
            win, width=44, height=h, bg="#1e1e2e", highlightthickness=0
        )
        canvas.pack(side="left", padx=(14, 6))

        label = tk.Label(
            win,
            text="Recording…",
            fg="#f5f5f5",
            bg="#1e1e2e",
            font=("Segoe UI", 12, "bold"),
        )
        label.pack(side="left", expand=True)

        self._win = win
        self._canvas = canvas
        self._label = label

    def show_recording(self) -> None:
        """Display the overlay in the recording state."""
        if self._win is None:
            self._build()
        assert self._win and self._label
        self._win.deiconify()
        self._label.config(text="🎤  Recording…")
        self._start_pulse()

    def show_processing(self) -> None:
        """Switch the overlay to the transcribing/enhancing state."""
        if self._win is None:
            self._build()
        assert self._win and self._label
        self._stop_pulse()
        self._win.deiconify()
        self._label.config(text="✨  Enhancing…")
        if self._canvas:
            self._canvas.delete("all")
            self._canvas.create_oval(
                10, 22, 34, 46, fill="#f9e2af", outline=""
            )  # amber dot

    def hide(self) -> None:
        """Hide the overlay (kept alive for reuse)."""
        self._stop_pulse()
        if self._win is not None:
            self._win.withdraw()

    # -- pulsing animation --------------------------------------------------
    def _start_pulse(self) -> None:
        self._stop_pulse()
        self._pulse_r = 14
        self._pulse_grow = True
        self._animate()

    def _animate(self) -> None:
        if self._canvas is None:
            return
        self._canvas.delete("all")
        cx, cy = 22, 35
        r = self._pulse_r
        self._canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r, fill="#f38ba8", outline=""
        )  # red dot
        # Oscillate radius between 10 and 18.
        if self._pulse_grow:
            self._pulse_r += 1
            if self._pulse_r >= 18:
                self._pulse_grow = False
        else:
            self._pulse_r -= 1
            if self._pulse_r <= 10:
                self._pulse_grow = True
        self._pulse_job = self.root.after(70, self._animate)

    def _stop_pulse(self) -> None:
        if self._pulse_job is not None:
            try:
                self.root.after_cancel(self._pulse_job)
            except tk.TclError:
                pass
            self._pulse_job = None
