"""Lightweight on-disk history of the last N enhanced prompts."""

from __future__ import annotations

import json
from collections import deque
from datetime import datetime
from pathlib import Path


class HistoryStore:
    """Keeps the most recent prompts, persisted to a JSON file."""

    def __init__(self, path: Path, max_items: int = 10) -> None:
        self.path = Path(path)
        self.max_items = max_items
        self._items: deque[dict] = deque(maxlen=max_items)
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            for entry in data[-self.max_items :]:
                self._items.append(entry)
        except (json.JSONDecodeError, OSError) as exc:
            print(f"[history] could not read {self.path}: {exc}")

    def add(self, original: str, enhanced: str) -> None:
        """Record a new (original, enhanced) pair and persist it."""
        self._items.append(
            {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "original": original,
                "enhanced": enhanced,
            }
        )
        self._save()

    def _save(self) -> None:
        try:
            self.path.write_text(
                json.dumps(list(self._items), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except OSError as exc:
            print(f"[history] could not write {self.path}: {exc}")

    def items(self) -> list[dict]:
        """Return history newest-last."""
        return list(self._items)
