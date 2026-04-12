"""Build PostHog events from parsed Claude Code session data."""

import os
import uuid
from datetime import datetime as dt

from posthog_llma.events import build_ai_generation, build_ai_span, build_ai_trace
from posthog_llma.trace_naming import find_trace_name


def build_events(parsed: dict, config: dict) -> list[dict]:
    """Convert parsed session data into PostHog $ai_* events.

    Supports two trace grouping modes (POSTHOG_LLMA_TRACE_GROUPING):
      - "session" (default): one $ai_trace per session
      - "message": one $ai_trace per user prompt
    """
    events = []
    session_id = parsed["session_id"]
    cwd = parsed["metadata"].get("cwd", "")
    project_name = os.path.basename(cwd) if cwd else ""
    privacy_mode = config.get("privacy_mode", False)
    trace_grouping = config.get("trace_grouping", "session")

    session_trace_id = session_id
    all_generations = parsed["generations"]
    all_tool_uses = parsed["tool_uses"]

    # In message mode, if prompt_id is missing we need a stable fallback
    # so a generation and its tool spans share the same trace_id.
    # Use span_id as the fallback — it's unique per generation but stable
    # across the generation and its child tool uses.
    fallback_trace_ids = {}  # span_id -> fallback trace_id

    # -- $ai_generation events --
    for gen in all_generations:
        if trace_grouping == "session":
            trace_id = session_trace_id
        else:
            prompt_id = gen.get("prompt_id")
            if prompt_id:
                trace_id = prompt_id
            else:
                # Use span_id as deterministic fallback
                trace_id = gen["span_id"]
                fallback_trace_ids[gen["span_id"]] = trace_id

        output_choices = None
        if not privacy_mode:
            content_blocks = []
            if gen["output_text"]:
                content_blocks.append({"type": "text", "text": gen["output_text"]})
            content_blocks.extend(gen.get("tool_use_blocks", []))
            if content_blocks:
                output_choices = [{"role": "assistant", "content": content_blocks}]

        user_prompt = None
        input_messages = None
        for p in parsed["prompts"]:
            if p["prompt_id"] == gen.get("prompt_id"):
                user_prompt = p.get("text")
                if user_prompt and not privacy_mode:
                    input_messages = [{"role": "user", "content": user_prompt}]
                break

        events.append(build_ai_generation(
            model=gen["model"],
            provider="anthropic",
            input_tokens=gen["input_tokens"],
            output_tokens=gen["output_tokens"],
            cache_read_tokens=gen["cache_read_tokens"],
            cache_creation_tokens=gen["cache_creation_tokens"],
            stop_reason=gen["stop_reason"],
            is_error=gen["is_error"],
            error_message=gen.get("error_message"),
            trace_id=trace_id,
            span_id=gen["span_id"],
            session_id=session_id,
            input_messages=input_messages,
            output_choices=output_choices,
            user_prompt=user_prompt,
            project_name=project_name,
            privacy_mode=privacy_mode,
            timestamp=gen.get("timestamp"),
        ))

    # -- $ai_span events --
    for tu in all_tool_uses:
        if trace_grouping == "session":
            trace_id = session_trace_id
        else:
            prompt_id = tu.get("prompt_id")
            if prompt_id:
                trace_id = prompt_id
            else:
                # Use the same fallback as the parent generation
                trace_id = fallback_trace_ids.get(tu.get("generation_span_id"), tu.get("generation_span_id", str(uuid.uuid4())))

        result = tu.get("result")
        is_error = False
        error_message = None
        output_state = None

        if result:
            if isinstance(result, dict):
                is_error = result.get("is_error", False) or result.get("isError", False)
                output_state = result.get("content", result)
                if is_error:
                    error_message = str(result.get("error", result.get("content", "")))[:500]
            else:
                output_state = result

        events.append(build_ai_span(
            span_name=tu["name"],
            trace_id=trace_id,
            parent_span_id=tu.get("generation_span_id"),
            session_id=session_id,
            input_state=tu.get("input") if not privacy_mode else None,
            output_state=output_state if not privacy_mode else None,
            is_error=is_error,
            error_message=error_message,
            project_name=project_name,
            privacy_mode=privacy_mode,
            max_attribute_length=config.get("max_attribute_length", 12000),
            timestamp=tu.get("timestamp"),
        ))

    # -- $ai_trace events --
    if trace_grouping == "session":
        _build_session_trace(events, parsed, all_generations, session_trace_id, session_id, project_name)
    else:
        _build_message_traces(events, parsed, all_generations, session_id, project_name)

    return events


def _compute_latency(timestamps: list[str]) -> float | None:
    """Calculate latency in seconds between first and last timestamp."""
    if len(timestamps) < 2:
        return None
    try:
        first = dt.fromisoformat(timestamps[0].replace("Z", "+00:00"))
        last = dt.fromisoformat(timestamps[-1].replace("Z", "+00:00"))
        return (last - first).total_seconds()
    except (ValueError, TypeError):
        return None


def _build_session_trace(events, parsed, all_generations, trace_id, session_id, project_name):
    total_input = sum(g["input_tokens"] for g in all_generations)
    total_output = sum(g["output_tokens"] for g in all_generations)
    has_error = any(g["is_error"] for g in all_generations)
    error_msg = next((g["error_message"] for g in all_generations if g.get("error_message")), None)

    timestamps = [g["timestamp"] for g in all_generations if g.get("timestamp")]
    trace_ts = timestamps[0] if timestamps else None
    trace_name = find_trace_name(parsed["prompts"])

    events.append(build_ai_trace(
        trace_id=trace_id,
        session_id=session_id,
        trace_name=trace_name,
        latency_seconds=_compute_latency(timestamps),
        total_input_tokens=total_input,
        total_output_tokens=total_output,
        is_error=has_error,
        error_message=error_msg,
        project_name=project_name,
        timestamp=trace_ts,
    ))


def _build_message_traces(events, parsed, all_generations, session_id, project_name):
    prompt_generations = {}
    for gen in all_generations:
        pid = gen.get("prompt_id", "")
        if pid:
            prompt_generations.setdefault(pid, []).append(gen)

    for prompt in parsed["prompts"]:
        pid = prompt["prompt_id"]
        gens = prompt_generations.get(pid, [])

        total_input = sum(g["input_tokens"] for g in gens)
        total_output = sum(g["output_tokens"] for g in gens)
        has_error = any(g["is_error"] for g in gens)
        error_msg = next((g["error_message"] for g in gens if g.get("error_message")), None)

        timestamps = [g["timestamp"] for g in gens if g.get("timestamp")]
        prompt_ts = timestamps[0] if timestamps else prompt.get("timestamp")
        trace_name = find_trace_name([prompt])

        events.append(build_ai_trace(
            trace_id=pid,
            session_id=session_id,
            trace_name=trace_name,
            latency_seconds=_compute_latency(timestamps),
            total_input_tokens=total_input,
            total_output_tokens=total_output,
            is_error=has_error,
            error_message=error_msg,
            project_name=project_name,
            timestamp=prompt_ts,
        ))
