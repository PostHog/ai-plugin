"""PostHog LLM Analytics — zero-dependency Python package.

Builds $ai_generation, $ai_span, and $ai_trace events and sends them
to PostHog. Client-specific adapters (e.g. Claude Code) live in the
hooks/ and scripts/ directories.
"""

from posthog_llma.events import build_ai_generation, build_ai_span, build_ai_trace
from posthog_llma.sender import DEFAULT_HOST, send_batch, write_status, read_status, STATUS_FILE
from posthog_llma.config import load_config
from posthog_llma.parser import parse_session, find_session_log
from posthog_llma.trace_naming import find_trace_name, clean_trace_name
from posthog_llma.event_builder import build_events

__all__ = [
    "build_ai_generation",
    "build_ai_span",
    "build_ai_trace",
    "send_batch",
    "write_status",
    "read_status",
    "STATUS_FILE",
    "DEFAULT_HOST",
    "load_config",
    "parse_session",
    "find_session_log",
    "find_trace_name",
    "clean_trace_name",
    "build_events",
]
