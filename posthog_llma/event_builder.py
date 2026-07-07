"""Build PostHog events from parsed Claude Code session data."""

import json
import os
import subprocess
import uuid
from datetime import datetime as dt
from typing import Optional

from posthog_llma.events import build_ai_generation, build_ai_span, build_ai_trace
from posthog_llma.trace_naming import find_trace_name

# Stable namespace for deriving deterministic event UUIDs via uuid5.
# Don't change — would break dedup against previously ingested events.
_UUID_NAMESPACE = uuid.UUID("a3c3f6c2-9b8e-4a3e-b3a1-7e6b8e9a0f00")


def parse_git_remote_url(url: str) -> Optional[str]:
    """Extract `owner/name` from a git remote URL.

    Handles the two common forms Claude Code sessions run under:
      - ssh scp-like: `git@github.com:owner/name.git`
      - https: `https://github.com/owner/name.git`
    Returns None when the URL doesn't resolve to an `owner/name` pair.
    """
    url = (url or "").strip()
    if not url:
        return None
    if url.endswith(".git"):
        url = url[:-4]

    if "://" in url:
        # scheme://[user@]host/owner/name -> drop scheme + host
        rest = url.split("://", 1)[1]
        parts = rest.split("/", 1)
        url = parts[1] if len(parts) > 1 else ""
    elif ":" in url:
        # scp-like git@host:owner/name -> drop host
        url = url.split(":", 1)[1]

    segments = [s for s in url.split("/") if s]
    if len(segments) < 2:
        return None
    return "/".join(segments[-2:])


def _git_repo_for_cwd(cwd: str) -> Optional[str]:
    """Best-effort `owner/name` for the session's working directory.

    Shells out to `git remote get-url origin` and parses the result. The
    cwd may no longer exist by ingest time, so every failure is swallowed.
    """
    if not cwd:
        return None

    repo = None
    try:
        result = subprocess.run(
            ["git", "-C", cwd, "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=2,
        )
        if result.returncode == 0:
            repo = parse_git_remote_url(result.stdout)
    except Exception:
        repo = None

    return repo


def _insert_id(*parts: str) -> str:
    """Deterministic identifier for PostHog dedup.

    The SessionEnd hook re-reads the full JSONL on every fire (including
    after `claude --resume`), so the same generation/tool/trace gets
    re-built and re-sent with fresh random span IDs. A stable identifier
    derived from session-stable inputs (session_id + msg_id, etc.) lets
    PostHog dedupe re-sends.

    Returned as a UUIDv5. The PostHog `/batch` endpoint dedupes on the
    event's top-level `uuid` field (the `events` table is a ClickHouse
    ReplacingMergeTree keyed by uuid); `$insert_id` as a property is
    *not* a dedup signal on this path. We set both — uuid drives the
    actual dedup, the $insert_id property doubles as a debug marker.
    """
    key = "|".join(p or "" for p in parts)
    return str(uuid.uuid5(_UUID_NAMESPACE, key))


def _truncate_tool_blocks(blocks: list, max_len: int) -> list:
    """Truncate tool use input args to prevent oversized payloads."""
    result = []
    for block in blocks:
        try:
            if block.get("type") != "tool_use" or "input" not in block:
                result.append(block)
                continue
            inp = block["input"]
            serialized = json.dumps(inp) if not isinstance(inp, str) else inp
            if len(serialized) <= max_len:
                result.append(block)
            else:
                result.append({**block, "input": serialized[:max_len]})
        except Exception:
            result.append({"type": "tool_use", "name": block.get("name", "unknown")})
    return result


def build_events(parsed: dict, config: dict) -> list[dict]:
    """Convert parsed session data into PostHog $ai_* events.

    Supports two trace grouping modes (trace_grouping config):
      - "session" (default): one $ai_trace per session
      - "message": one $ai_trace per user prompt
    """
    events = []
    session_id = parsed["session_id"]
    cwd = parsed["metadata"].get("cwd", "")
    project_name = os.path.basename(cwd) if cwd else ""

    # Git context attached to every emitted event. Branch comes straight
    # from the transcript; repo is derived at ingest time via a single
    # `git remote get-url origin` shellout. Filtered to truthy values so
    # a single `properties.update(git_properties)` is a no-op when unknown.
    git_branch = parsed["metadata"].get("git_branch", "") or ""
    git_repo = _git_repo_for_cwd(cwd) or ""
    git_properties = {k: v for k, v in {"$ai_git_branch": git_branch, "$ai_git_repo": git_repo}.items() if v}

    privacy_mode = config.get("privacy_mode", False)
    trace_grouping = config.get("trace_grouping", "session")
    custom_properties = config.get("custom_properties") or None

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
            max_attr = config.get("max_attribute_length", 12000)
            content_blocks = []
            if gen["output_text"]:
                content_blocks.append({"type": "text", "text": gen["output_text"]})
            content_blocks.extend(_truncate_tool_blocks(gen.get("tool_use_blocks", []), max_attr))
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
            parent_id=trace_id,
            span_id=gen["span_id"],
            session_id=session_id,
            input_messages=input_messages,
            output_choices=output_choices,
            user_prompt=user_prompt,
            project_name=project_name,
            git_properties=git_properties,
            privacy_mode=privacy_mode,
            extra_properties=custom_properties,
            timestamp=gen.get("timestamp"),
            insert_id=_insert_id(
                "cc-gen", session_id,
                gen.get("msg_id") or gen["span_id"],
            ),
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
            git_properties=git_properties,
            privacy_mode=privacy_mode,
            max_attribute_length=config.get("max_attribute_length", 12000),
            extra_properties=custom_properties,
            timestamp=tu.get("timestamp"),
            insert_id=_insert_id(
                "cc-span", session_id,
                tu.get("tool_use_id") or "",
                tu.get("name") or "",
                tu.get("timestamp") or "",
            ),
        ))

    # -- $ai_trace events --
    if trace_grouping == "session":
        _build_session_trace(events, parsed, all_generations, session_trace_id, session_id, project_name, custom_properties, git_properties)
    else:
        _build_message_traces(events, parsed, all_generations, session_id, project_name, fallback_trace_ids, custom_properties, git_properties)

    return events


def _compute_latency(timestamps: list[str]) -> Optional[float]:
    """Calculate latency in seconds between first and last timestamp."""
    if len(timestamps) < 2:
        return None
    try:
        first = dt.fromisoformat(timestamps[0].replace("Z", "+00:00"))
        last = dt.fromisoformat(timestamps[-1].replace("Z", "+00:00"))
        return (last - first).total_seconds()
    except (ValueError, TypeError):
        return None


def _build_session_trace(events, parsed, all_generations, trace_id, session_id, project_name, custom_properties=None, git_properties=None):
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
        git_properties=git_properties,
        extra_properties=custom_properties,
        timestamp=trace_ts,
        insert_id=_insert_id("cc-trace-session", session_id),
    ))


def _build_message_traces(events, parsed, all_generations, session_id, project_name, fallback_trace_ids=None, custom_properties=None, git_properties=None):
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
            git_properties=git_properties,
            extra_properties=custom_properties,
            timestamp=prompt_ts,
            insert_id=_insert_id("cc-trace-msg", session_id, pid),
        ))

    # Emit root trace events for fallback (unresolved prompt) trace IDs
    if fallback_trace_ids:
        fallback_generations = {}
        for gen in all_generations:
            tid = fallback_trace_ids.get(gen["span_id"])
            if tid:
                fallback_generations.setdefault(tid, []).append(gen)

        for trace_id, gens in fallback_generations.items():
            total_input = sum(g["input_tokens"] for g in gens)
            total_output = sum(g["output_tokens"] for g in gens)
            has_error = any(g["is_error"] for g in gens)
            error_msg = next((g["error_message"] for g in gens if g.get("error_message")), None)
            timestamps = [g["timestamp"] for g in gens if g.get("timestamp")]

            events.append(build_ai_trace(
                trace_id=trace_id,
                session_id=session_id,
                trace_name="(unresolved prompt)",
                latency_seconds=_compute_latency(timestamps),
                total_input_tokens=total_input,
                total_output_tokens=total_output,
                is_error=has_error,
                error_message=error_msg,
                project_name=project_name,
                git_properties=git_properties,
                extra_properties=custom_properties,
                timestamp=timestamps[0] if timestamps else None,
                insert_id=_insert_id("cc-trace-fallback", session_id, trace_id),
            ))
