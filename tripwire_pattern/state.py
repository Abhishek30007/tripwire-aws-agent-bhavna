"""Split a Strands message history into trusted user text and untrusted tool output."""
from __future__ import annotations


def build_context(messages: list[dict], max_user: int = 3, max_tool_chars: int = 2000) -> tuple[str, str]:
    user_texts, tool_texts = [], []
    for m in messages:
        for block in m.get("content", []):
            if m.get("role") == "user" and "text" in block:
                user_texts.append(block["text"])
            if "toolResult" in block:
                for part in block["toolResult"].get("content", []):
                    if "text" in part:
                        tool_texts.append(part["text"])
    return "\n".join(user_texts[-max_user:]), "\n".join(tool_texts)[-max_tool_chars:]
