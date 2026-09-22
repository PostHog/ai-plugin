"""Trace name selection from user prompts."""

import re
from typing import Optional

# Prompts that are framework noise — skip when picking a trace name
_SKIP_PROMPTS = re.compile(
    r"^(/clear|/exit|/quit|/help|/compact|/reload|clear|exit|quit|"
    r"\[Request interrupted|\[Request cancelled)",
    re.IGNORECASE,
)


def clean_trace_name(text: str, max_len: int = 100) -> str:
    """Strip XML/HTML tags and truncate for use as a trace name."""
    cleaned = re.sub(r"<[^>]+>", "", text).strip()
    cleaned = " ".join(cleaned.split())
    return cleaned[:max_len] if cleaned else text[:max_len]


def find_trace_name(prompts: list[dict], max_len: int = 100) -> Optional[str]:
    """Find the first meaningful user prompt to use as a trace name.

    Skips framework noise like /clear, /exit, [Request interrupted] etc.
    Falls back to the first prompt if all are noisy.
    """
    for p in prompts:
        text = p.get("text", "")
        if not text:
            continue
        cleaned = clean_trace_name(text, max_len)
        if cleaned and not _SKIP_PROMPTS.match(cleaned):
            return cleaned
    # Fallback: use whatever the first prompt is, even if noisy
    if prompts and prompts[0].get("text"):
        return clean_trace_name(prompts[0]["text"], max_len)
    return None
