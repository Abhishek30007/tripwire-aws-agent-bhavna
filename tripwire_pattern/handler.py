"""Strands InterventionHandler that puts Tripwire in front of every tool call."""
from __future__ import annotations

from strands.interventions import Deny, Guide, InterventionHandler, Proceed

from .core import Tripwire
from .state import build_context


class TripwireHandler(InterventionHandler):
    name = "tripwire"

    def __init__(self, tripwire: Tripwire, guarded_tools=None, fail_closed: bool = True):
        self.tripwire = tripwire
        self.guarded_tools = set(guarded_tools) if guarded_tools else None  # None = all tools
        self._fail_closed = fail_closed

    @property
    def on_error(self):
        # If the Decider server is down, deny rather than silently skip the check.
        return "deny" if self._fail_closed else "throw"

    def before_tool_call(self, event, **kwargs):
        tool, args = event.tool_use["name"], event.tool_use.get("input", {}) or {}
        if self.guarded_tools is not None and tool not in self.guarded_tools:
            return Proceed(reason="tool not guarded")
        user_text, tool_output = build_context(event.agent.messages)
        v = self.tripwire.evaluate(user_text, tool_output, tool, args)
        if v.action == "allow":
            return Proceed(reason=v.reason)
        if v.action == "block":
            return Deny(reason=f"Tripwire blocked {tool}: {v.reason}")
        return Guide(feedback=(f"Tripwire could not confirm the arguments of {tool} from the user's "
                               f"request ({v.reason}). Ask the user to confirm the exact values "
                               f"{args} before calling it again."))
