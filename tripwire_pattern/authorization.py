"""Single-use, parameter-bound confirmation tokens for the "ask the user" lane.

Adapted from the PendingActionManager in Ayush Devani's Tripwire prototype
(github.com/AYUSHDEVANI/tripwire-aws-agent), rewritten with dataclasses (no pydantic).
Not wired into the demo agent: use it when you build your own confirmation step.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass


@dataclass
class PendingAction:
    token: str
    tool: str
    args: dict
    question: str
    expires_at: float
    used: bool = False


class PendingActionManager:
    def __init__(self, ttl_seconds: float = 120.0):
        self.ttl = ttl_seconds
        self._pending: dict[str, PendingAction] = {}

    def create(self, tool: str, args: dict, question: str) -> PendingAction:
        p = PendingAction(str(uuid.uuid4()), tool, dict(args), question, time.time() + self.ttl)
        self._pending[p.token] = p
        return p

    def verify_and_consume(self, token: str, tool: str, args: dict) -> bool:
        """True only if the token exists, is unexpired, unused, and bound to exactly this call."""
        p = self._pending.get(token)
        if p is None or p.used or time.time() > p.expires_at:
            return False
        if p.tool != tool or p.args != args:
            return False
        p.used = True
        return True
