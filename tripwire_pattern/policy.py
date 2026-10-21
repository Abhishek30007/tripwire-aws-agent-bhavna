"""Deterministic policy layer that can only make Tripwire stricter.

Adapted from the policy engine in Ayush Devani's Tripwire prototype
(github.com/AYUSHDEVANI/tripwire-aws-agent), generalised to any resource naming.
It runs after Decider: if the cascade allows a call but a policy fails, the call is blocked.
"""
from __future__ import annotations

from dataclasses import dataclass, field

DEFAULT_MUTATING = frozenset({"start_instance", "stop_instance", "reboot_instance"})
DEFAULT_DESTRUCTIVE = frozenset({"delete_bucket", "terminate_instance", "delete_database"})
DEFAULT_READ_ONLY = frozenset({"list_instances", "read_logs", "describe_instance"})


@dataclass
class PolicyResult:
    passed: bool
    violations: list[str] = field(default_factory=list)


class PolicyEngine:
    def __init__(self, caller_role: str = "operator", allow_prod_mutations: bool = False,
                 mutating=DEFAULT_MUTATING, destructive=DEFAULT_DESTRUCTIVE,
                 read_only=DEFAULT_READ_ONLY, resource_env: dict | None = None):
        self.caller_role = caller_role
        self.allow_prod_mutations = allow_prod_mutations
        self.mutating, self.destructive, self.read_only = set(mutating), set(destructive), set(read_only)
        self.resource_env = resource_env or {}

    def environment_of(self, args: dict) -> str | None:
        """Environment of the target resource: explicit map first, then a name hint."""
        for v in args.values():
            s = str(v).lower()
            if s in self.resource_env:
                return self.resource_env[s]
            if "prod" in s:
                return "prod"
            if "staging" in s:
                return "staging"
        return None

    def evaluate(self, tool: str, args: dict, user_text: str) -> PolicyResult:
        violations: list[str] = []
        env = self.environment_of(args)
        said = user_text.lower()
        if tool in self.mutating | self.destructive:
            if self.caller_role == "viewer":
                violations.append(f"role 'viewer' may not run {tool}")
            if env == "prod" and not self.allow_prod_mutations and self.caller_role != "admin":
                violations.append(f"{tool} on a production resource is not allowed for role '{self.caller_role}'")
        if env == "prod" and "staging" in said and "prod" not in said:
            violations.append("environment confusion: the user asked about staging but the call targets production")
        return PolicyResult(not violations, violations)
