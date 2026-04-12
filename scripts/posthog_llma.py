"""
PostHog LLM Analytics - Generic event builder and sender.

Builds $ai_generation, $ai_span, and $ai_trace events in PostHog's
LLM analytics format and sends them via the /batch capture endpoint.

This module is client-agnostic — it takes structured data and produces
PostHog events. Client-specific parsers (e.g. session-end-llma.py for
Claude Code) feed data into this module.

Zero dependencies — uses only Python stdlib.
"""

import json
import os
import urllib.request
import urllib.error
import uuid
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Event builders
#
# Note: cost calculation ($ai_total_cost_usd etc.) is handled by PostHog's
# ingestion pipeline automatically from $ai_model + token counts. We do NOT
# need to calculate or send cost — just send model and tokens.
# ---------------------------------------------------------------------------

def build_ai_generation(
    *,
    model: str,
    provider: str = "anthropic",
    input_tokens: int = 0,
    output_tokens: int = 0,
    cache_read_tokens: int = 0,
    cache_creation_tokens: int = 0,
    latency_seconds: float | None = None,
    stop_reason: str | None = None,
    is_error: bool = False,
    error_message: str | None = None,
    trace_id: str,
    span_id: str | None = None,
    session_id: str,
    input_messages: object = None,
    output_choices: object = None,
    user_prompt: str | None = None,
    project_name: str = "",
    agent_name: str = "",
    privacy_mode: bool = False,
    extra_properties: dict | None = None,
    timestamp: str | None = None,
) -> dict:
    """Build a $ai_generation event.

    Cost ($ai_total_cost_usd etc.) is calculated by PostHog's ingestion
    pipeline from $ai_model + token counts — we don't send it.
    """
    total_tokens = input_tokens + output_tokens

    # Map Claude Code stop reasons to PostHog's expected values
    stop_map = {"end_turn": "stop", "tool_use": "tool_calls", "max_tokens": "length"}
    mapped_stop = stop_map.get(stop_reason, stop_reason) if stop_reason else None

    properties = {
        "$ai_model": model,
        "$ai_provider": provider,
        "$ai_input_tokens": input_tokens,
        "$ai_output_tokens": output_tokens,
        "$ai_total_tokens": total_tokens,
        "$ai_latency": latency_seconds,
        "$ai_stop_reason": mapped_stop,
        "$ai_is_error": is_error,
        "$ai_error": error_message,
        "$ai_trace_id": trace_id,
        "$ai_span_id": span_id or str(uuid.uuid4()),
        "$ai_session_id": session_id,
        "$ai_input": None if privacy_mode else input_messages,
        "$ai_output_choices": None if privacy_mode else output_choices,
        "$ai_lib": "posthog-ai-plugin",
        "$ai_framework": "claude-code",
        "$ai_project_name": project_name,
        "$ai_agent_name": agent_name,
        "cache_read_input_tokens": cache_read_tokens,
        "cache_creation_input_tokens": cache_creation_tokens,
    }

    if user_prompt and not privacy_mode:
        properties["$ai_user_prompt"] = user_prompt

    if extra_properties:
        properties.update(extra_properties)

    result = {"event": "$ai_generation", "properties": properties}
    if timestamp:
        result["timestamp"] = timestamp
    return result


def build_ai_span(
    *,
    span_name: str,
    trace_id: str,
    parent_span_id: str | None = None,
    span_id: str | None = None,
    session_id: str,
    latency_seconds: float | None = None,
    input_state: object = None,
    output_state: object = None,
    is_error: bool = False,
    error_message: str | None = None,
    project_name: str = "",
    agent_name: str = "",
    privacy_mode: bool = False,
    max_attribute_length: int = 12000,
    timestamp: str | None = None,
) -> dict:
    """Build a $ai_span event for a tool execution."""
    def _truncate(val, max_len):
        if val is None:
            return None
        s = json.dumps(val) if not isinstance(val, str) else val
        return s[:max_len] if len(s) > max_len else s

    properties = {
        "$ai_span_name": span_name,
        "$ai_trace_id": trace_id,
        "$ai_span_id": span_id or str(uuid.uuid4()),
        "$ai_parent_id": parent_span_id,
        "$ai_session_id": session_id,
        "$ai_latency": latency_seconds,
        "$ai_input_state": None if privacy_mode else _truncate(input_state, max_attribute_length),
        "$ai_output_state": None if privacy_mode else _truncate(output_state, max_attribute_length),
        "$ai_is_error": is_error,
        "$ai_error": error_message,
        "$ai_lib": "posthog-ai-plugin",
        "$ai_framework": "claude-code",
        "$ai_project_name": project_name,
        "$ai_agent_name": agent_name,
    }

    result = {"event": "$ai_span", "properties": properties}
    if timestamp:
        result["timestamp"] = timestamp
    return result


def build_ai_trace(
    *,
    trace_id: str,
    session_id: str,
    trace_name: str | None = None,
    latency_seconds: float | None = None,
    total_input_tokens: int = 0,
    total_output_tokens: int = 0,
    is_error: bool = False,
    error_message: str | None = None,
    project_name: str = "",
    agent_name: str = "",
    timestamp: str | None = None,
) -> dict:
    """Build a $ai_trace event for a complete prompt→response cycle."""
    properties = {
        "$ai_trace_id": trace_id,
        "$ai_trace_name": trace_name,
        "$ai_session_id": session_id,
        "$ai_latency": latency_seconds,
        "$ai_total_input_tokens": total_input_tokens,
        "$ai_total_output_tokens": total_output_tokens,
        "$ai_is_error": is_error,
        "$ai_error": error_message,
        "$ai_lib": "posthog-ai-plugin",
        "$ai_framework": "claude-code",
        "$ai_project_name": project_name,
        "$ai_agent_name": agent_name,
    }

    result = {"event": "$ai_trace", "properties": properties}
    if timestamp:
        result["timestamp"] = timestamp
    return result


# ---------------------------------------------------------------------------
# Sender
# ---------------------------------------------------------------------------

DEFAULT_HOST = "https://us.i.posthog.com"


def send_batch(
    events: list[dict],
    *,
    api_key: str,
    host: str = DEFAULT_HOST,
    distinct_id: str,
) -> dict:
    """Send a batch of events to PostHog's /batch endpoint.

    Each event dict must have 'event' and 'properties' keys.
    Returns {"status": "ok", "sent": N} on success or {"status": "error", "error": str}.
    """
    if not events:
        return {"status": "ok", "sent": 0}

    batch = []
    fallback_ts = datetime.now(timezone.utc).isoformat()

    for ev in events:
        batch.append({
            "event": ev["event"],
            "properties": {
                **ev["properties"],
                "$lib": "posthog-ai-plugin",
            },
            "distinct_id": distinct_id,
            "timestamp": ev.get("timestamp") or fallback_ts,
        })

    payload = json.dumps({
        "api_key": api_key,
        "batch": batch,
    }).encode("utf-8")

    url = f"{host.rstrip('/')}/batch"

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "posthog-ai-plugin/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return {"status": "ok", "sent": len(batch), "response_code": resp.status}
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")[:500]
        except Exception:
            pass
        return {"status": "error", "error": f"HTTP {e.code}: {body}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ---------------------------------------------------------------------------
# Status file helpers
# ---------------------------------------------------------------------------

STATUS_FILE = os.path.expanduser("~/.claude/posthog-llma-status.json")


def write_status(status: dict) -> None:
    """Write last send status to a file for /posthog:llma-status to read."""
    status["timestamp"] = datetime.now(timezone.utc).isoformat()
    try:
        os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
        with open(STATUS_FILE, "w") as f:
            json.dump(status, f, indent=2)
    except OSError:
        pass


def read_status() -> dict | None:
    """Read last send status."""
    try:
        with open(STATUS_FILE) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
