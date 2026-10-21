"""Scrub credentials from anything written to the audit log.

Adapted from the redaction helpers in Ayush Devani's Tripwire prototype
(github.com/AYUSHDEVANI/tripwire-aws-agent, MIT License); see NOTICE.
"""
from __future__ import annotations

import re
from typing import Any

PATTERNS = [
    (re.compile(r"(?i)\b(akia[0-9a-z]{16})\b"), "[REDACTED_AWS_KEY]"),
    (re.compile(r"(?i)\b(asia[0-9a-z]{16})\b"), "[REDACTED_AWS_KEY]"),
    (re.compile(r"(?i)(aws_secret_access_key\s*[:=]\s*['\"]?)([0-9a-zA-Z/+]{40})(['\"]?)"), r"\1[REDACTED_AWS_SECRET]\3"),
    (re.compile(r"(?i)(bearer\s+[a-zA-Z0-9_\-\.]{20,})"), "Bearer [REDACTED_TOKEN]"),
    (re.compile(r"(?i)(password\s*[:=]\s*['\"]?)([^'\";\s]+)(['\"]?)"), r"\1[REDACTED_PASSWORD]\3"),
    (re.compile(r"(?i)(token\s*[:=]\s*['\"]?)([a-zA-Z0-9_\-\.]{16,})(['\"]?)"), r"\1[REDACTED_TOKEN]\3"),
    (re.compile(r"(?i)(api[_-]?key\s*[:=]\s*['\"]?)([a-zA-Z0-9_\-]{16,})(['\"]?)"), r"\1[REDACTED_API_KEY]\3"),
]
SENSITIVE_KEYS = ("secret", "password", "token", "apikey", "api_key", "authorization")


def redact_string(text: str) -> str:
    for pattern, repl in PATTERNS:
        text = pattern.sub(repl, text)
    return text


def sanitize(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: "[REDACTED]" if any(t in k.lower() for t in SENSITIVE_KEYS) else sanitize(v)
                for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize(i) for i in obj]
    if isinstance(obj, str):
        return redact_string(obj)
    return obj
