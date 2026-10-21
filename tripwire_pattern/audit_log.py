"""Append-only JSONL decision log (read by the dashboard)."""
from __future__ import annotations

import json
import os
import time

from .redact import sanitize


class AuditLog:
    def __init__(self, path: str = "logs/decisions.jsonl"):
        self.path = path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    def write(self, row: dict) -> None:
        row = {"ts": time.time(), **sanitize(row)}
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, default=str) + "\n")
