"""Confidence cascade: turns Decider probabilities into one of four lanes.

confidence = |2p - 1|  (for a yes/no question the probability *is* the uncertainty)
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Thresholds:
    allow_conf: float = 0.70          # confidence needed to follow Decider (allow or block)
    destructive_conf: float = 0.84    # stricter bar for destructive tools (stop, delete)
    judge_conf: float = 0.30          # below this, escalate to the LLM judge
    injection_p: float = 0.60         # P(from untrusted text) at or above this blocks outright


def confidence(p_grounded: float) -> float:
    return abs(2 * p_grounded - 1)


def route(p_grounded: float, p_injected: float, destructive: bool,
          t: Thresholds = Thresholds()) -> tuple[str, str]:
    """Returns (lane, reason). lane is one of: allow, block, ask_user, llm_judge."""
    if p_injected >= t.injection_p:
        return "block", f"call appears to follow instructions from tool output (p={p_injected:.2f})"
    conf = confidence(p_grounded)
    need = t.destructive_conf if destructive else t.allow_conf
    if conf >= need:
        if p_grounded >= 0.5:
            return "allow", f"arguments grounded in the user's request (p={p_grounded:.2f})"
        return "block", f"arguments not grounded in the user's request (p={p_grounded:.2f})"
    if conf >= t.judge_conf:
        return "ask_user", f"medium confidence (p={p_grounded:.2f}); confirm with the user"
    return "llm_judge", f"low confidence (p={p_grounded:.2f}); escalating to the LLM judge"
