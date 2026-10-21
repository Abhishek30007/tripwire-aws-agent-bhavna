"""Framework-independent core: decide, route, (optionally) judge, log."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

from .cascade import Thresholds, confidence, route


@dataclass
class Verdict:
    action: str            # allow | block | ask
    lane: str              # allow | block | ask_user | llm_judge (what the cascade chose)
    reason: str
    tool: str
    args: dict = field(default_factory=dict)
    p_grounded: float = 0.0
    p_injected: float = 0.0
    confidence: float = 0.0
    latency_ms: float = 0.0
    judged: bool = False
    policy_violations: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


class Tripwire:
    def __init__(self, decider, judge=None, thresholds: Thresholds = Thresholds(),
                 destructive=frozenset(), audit_log=None, policy=None):
        self.decider = decider
        self.judge = judge
        self.t = thresholds
        self.destructive = frozenset(destructive)
        self.audit_log = audit_log
        self.policy = policy

    def evaluate(self, user_text: str, tool_output: str, tool: str, args: dict) -> Verdict:
        a = self.decider.assess(user_text, tool_output, tool, args)
        lane, reason = route(a.p_grounded, a.p_injected, tool in self.destructive, self.t)
        judged = False
        if lane == "llm_judge":
            if self.judge is None:
                action, reason = "ask", reason + "; no LLM judge configured, asking the user"
            else:
                j = self.judge.judge(user_text, tool_output, tool, args)
                judged = True
                action = "allow" if j.grounded else "block"
                reason += f"; LLM judge says {'grounded' if j.grounded else 'ungrounded'}"
        else:
            action = {"allow": "allow", "block": "block", "ask_user": "ask"}[lane]
        violations = []
        if action == "allow" and self.policy is not None:      # policy can only tighten
            r = self.policy.evaluate(tool, args, user_text)
            if not r.passed:
                action, violations = "block", r.violations
                reason += "; blocked by policy: " + "; ".join(violations)
        v = Verdict(action, lane, reason, tool, dict(args), a.p_grounded, a.p_injected,
                    confidence(a.p_grounded), a.latency_ms, judged, violations)
        if self.audit_log:
            self.audit_log.write({"user_message": user_text, "tool_output": tool_output[:300],
                                  **v.to_dict()})
        return v
