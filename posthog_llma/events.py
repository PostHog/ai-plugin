"""PostHog $ai_* event builders.

Cost calculation ($ai_total_cost_usd etc.) is handled by PostHog's
ingestion pipeline automatically from $ai_model + token counts.
We do NOT need to calculate or send cost — just send model and tokens.
"""

import json
import uuid
from typing import Optional


def build_ai_generation(
    *,
    model: str,
    provider: str = "anthropic",
    input_tokens: int = 0,
    output_tokens: int = 0,
    cache_read_tokens: int = 0,
    cache_creation_tokens: int = 0,
    latency_seconds: Optional[float] = None,
    stop_reason: Optional[str] = None,
    is_error: bool = False,
    error_message: Optional[str] = None,
    trace_id: str,
    parent_id: Optional[str] = None,
    span_id: Optional[str] = None,
    session_id: str,
    input_messages: object = None,
    output_choices: object = None,
    user_prompt: Optional[str] = None,
    project_name: str = "",
    agent_name: str = "",
    git_properties: Optional[dict] = None,
    privacy_mode: bool = False,
    extra_properties: Optional[dict] = None,
    timestamp: Optional[str] = None,
    insert_id: Optional[str] = None,
) -> dict:
    """Build a $ai_generation event.

    Pass `insert_id` to set `$insert_id` for PostHog dedup. Use a
    deterministic value (e.g. derived from session_id + message_id) so
    re-sends of the same generation collapse into a single ingested event.
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
        "$ai_parent_id": parent_id,
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

    # Git context lets engineering analytics attribute token spend to PRs by
    # joining $ai_git_branch against a PR head ref. Already filtered to
    # truthy values by the caller, so this is a no-op when unknown.
    if git_properties:
        properties.update(git_properties)

    if extra_properties:
        properties.update(extra_properties)

    if insert_id:
        properties["$insert_id"] = insert_id

    result = {"event": "$ai_generation", "properties": properties}
    if insert_id:
        result["uuid"] = insert_id
    if timestamp:
        result["timestamp"] = timestamp
    return result


def build_ai_span(
    *,
    span_name: str,
    trace_id: str,
    parent_span_id: Optional[str] = None,
    span_id: Optional[str] = None,
    session_id: str,
    latency_seconds: Optional[float] = None,
    input_state: object = None,
    output_state: object = None,
    is_error: bool = False,
    error_message: Optional[str] = None,
    project_name: str = "",
    agent_name: str = "",
    git_properties: Optional[dict] = None,
    privacy_mode: bool = False,
    max_attribute_length: int = 12000,
    extra_properties: Optional[dict] = None,
    timestamp: Optional[str] = None,
    insert_id: Optional[str] = None,
) -> dict:
    """Build a $ai_span event for a tool execution.

    Pass `insert_id` to set `$insert_id` for PostHog dedup.
    """
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

    if git_properties:
        properties.update(git_properties)

    if extra_properties:
        properties.update(extra_properties)

    if insert_id:
        properties["$insert_id"] = insert_id

    result = {"event": "$ai_span", "properties": properties}
    if insert_id:
        result["uuid"] = insert_id
    if timestamp:
        result["timestamp"] = timestamp
    return result


def build_ai_trace(
    *,
    trace_id: str,
    session_id: str,
    trace_name: Optional[str] = None,
    latency_seconds: Optional[float] = None,
    total_input_tokens: int = 0,
    total_output_tokens: int = 0,
    is_error: bool = False,
    error_message: Optional[str] = None,
    project_name: str = "",
    agent_name: str = "",
    git_properties: Optional[dict] = None,
    extra_properties: Optional[dict] = None,
    timestamp: Optional[str] = None,
    insert_id: Optional[str] = None,
) -> dict:
    """Build a $ai_trace event for a complete prompt-to-response cycle.

    Pass `insert_id` to set `$insert_id` for PostHog dedup.
    """
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

    if git_properties:
        properties.update(git_properties)

    if extra_properties:
        properties.update(extra_properties)

    if insert_id:
        properties["$insert_id"] = insert_id

    result = {"event": "$ai_trace", "properties": properties}
    if insert_id:
        result["uuid"] = insert_id
    if timestamp:
        result["timestamp"] = timestamp
    return result
