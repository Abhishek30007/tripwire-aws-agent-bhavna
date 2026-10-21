"""TEST-ONLY rule-based stand-in for Decider so unit tests run without the model.
Not part of the shipped package; never used by the demo, agent or benchmark."""
import re

from tripwire_pattern import Assessment

VAGUE = ("box", "server", "that one", "the old", " it", "database", "thing", "the api")


def _mentions(text, value):
    return bool(re.search(rf"(?<![\w-]){re.escape(str(value).lower())}(?![\w-])", text.lower()))


class RuleStub:
    def assess(self, user_text, tool_output, tool, args):
        vals = list(args.values())
        in_user = [_mentions(user_text, v) for v in vals]
        in_tool = [_mentions(tool_output, v) for v in vals]
        if vals and all(in_user):
            return Assessment(0.96, 0.03, 0.1)
        if any(w in f" {user_text.lower()}" for w in VAGUE) and not any(in_tool):
            return Assessment(0.70, 0.05, 0.1)
        if any(in_tool):
            return Assessment(0.05, 0.90, 0.1)
        return Assessment(0.05, 0.10, 0.1)
