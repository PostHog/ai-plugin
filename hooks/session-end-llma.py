#!/usr/bin/env python3
"""
Claude Code SessionEnd hook — parses session JSONL and sends
$ai_generation, $ai_span, $ai_trace events to PostHog LLM Analytics.

No-op if POSTHOG_API_KEY is not set.

This is the Claude Code specific adapter. The generic event building
and sending logic lives in scripts/posthog_llma.py.
"""

import json
import os
import sys
import uuid
from pathlib import Path

# Add scripts/ to path so we can import the generic module
PLUGIN_ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(PLUGIN_ROOT, "scripts"))

import posthog_llma  # noqa: E402


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_config() -> dict:
    """Load configuration from env vars and optional config file."""
    config = {
        "api_key": os.environ.get("POSTHOG_API_KEY", ""),
        "host": os.environ.get("POSTHOG_HOST", posthog_llma.DEFAULT_HOST),
        "privacy_mode": os.environ.get("POSTHOG_LLMA_PRIVACY_MODE", "false").lower() == "true",
        "enabled": os.environ.get("POSTHOG_LLMA_CC_ENABLED", "false").lower() == "true",
        "distinct_id": os.environ.get("POSTHOG_LLMA_DISTINCT_ID", ""),
        "max_attribute_length": int(os.environ.get("POSTHOG_LLMA_MAX_ATTRIBUTE_LENGTH", "12000")),
        "trace_grouping": os.environ.get("POSTHOG_LLMA_TRACE_GROUPING", "session"),  # "session" or "message"
    }

    # Try config file as fallback for missing values
    config_path = os.path.expanduser("~/.claude/posthog-llma.local.md")
    if os.path.isfile(config_path):
        try:
            with open(config_path) as f:
                content = f.read()
            # Parse YAML-like frontmatter
            if content.startswith("---"):
                end = content.find("---", 3)
                if end > 0:
                    for line in content[3:end].strip().splitlines():
                        if ":" in line:
                            key, val = line.split(":", 1)
                            key = key.strip()
                            val = val.strip().strip('"').strip("'")
                            if key == "api_key" and not config["api_key"]:
                                config["api_key"] = val
                            elif key == "host" and config["host"] == posthog_llma.DEFAULT_HOST:
                                config["host"] = val
                            elif key == "distinct_id" and not config["distinct_id"]:
                                config["distinct_id"] = val
                            elif key == "privacy_mode" and val.lower() == "true":
                                config["privacy_mode"] = True
        except OSError:
            pass

    return config


# ---------------------------------------------------------------------------
# JSONL parser
# ---------------------------------------------------------------------------

def find_session_log(session_id: str, cwd: str) -> str | None:
    """Find the JSONL session log file."""
    # Claude Code stores logs at ~/.claude/projects/{cwd-as-dashes}/{session_id}.jsonl
    project_dir_name = cwd.replace("/", "-")
    path = Path.home() / ".claude" / "projects" / project_dir_name / f"{session_id}.jsonl"
    if path.is_file():
        return str(path)
    return None


def parse_session(jsonl_path: str, config: dict) -> dict:
    """Parse a Claude Code session JSONL file into structured data.

    Returns:
        {
            "session_id": str,
            "generations": [...],  # assistant messages with usage
            "tool_uses": [...],    # tool calls with results
            "prompts": [...],      # user prompts (for trace grouping)
            "metadata": {...},     # session metadata
        }
    """
    generations_by_msg_id = {}  # msg_id -> (generation_dict, [tool_uses])
    generations_order = []  # preserve insertion order of msg_ids
    tool_results = {}  # tool_use_id -> result content
    prompts = []  # {prompt_id, timestamp, text}
    metadata = {}

    session_id = ""
    privacy_mode = config["privacy_mode"]

    # Maps for resolving promptId via parentUuid chains.
    # Assistant messages don't carry promptId directly — it lives on the
    # originating user message. We walk parentUuid up the chain to find it.
    uuid_to_prompt_id = {}  # uuid -> promptId (only user prompt entries)
    uuid_to_parent = {}     # uuid -> parentUuid (all entries)

    # First pass: build UUID maps
    with open(jsonl_path) as f:
        for line in f:
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            uid = entry.get("uuid", "")
            if uid:
                parent = entry.get("parentUuid", "")
                if parent:
                    uuid_to_parent[uid] = parent
                prompt_id = entry.get("promptId", "")
                if prompt_id:
                    uuid_to_prompt_id[uid] = prompt_id

    def resolve_prompt_id(entry_uuid: str) -> str:
        """Walk parentUuid chain to find the promptId."""
        current = entry_uuid
        for _ in range(30):
            if current in uuid_to_prompt_id:
                return uuid_to_prompt_id[current]
            parent = uuid_to_parent.get(current)
            if not parent:
                break
            current = parent
        return ""

    # No separate seen_message_ids needed — we use generations_by_msg_id
    # to deduplicate, keeping the last (most complete) version.

    # Second pass: extract data
    with open(jsonl_path) as f:
        for line in f:
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            entry_type = entry.get("type", "")

            # Session metadata
            if entry_type == "permission-mode":
                session_id = entry.get("sessionId", "")

            # User messages (prompts + tool results)
            if entry_type == "user":
                msg = entry.get("message", {})
                if msg.get("role") == "user":
                    prompt_id = entry.get("promptId", "")
                    timestamp = entry.get("timestamp", "")

                    # Check if this contains tool results.
                    # Tool results can appear in two places:
                    #   1. entry.toolUseResult + entry.sourceToolUseID (older format)
                    #   2. message.content[] items with type=tool_result and tool_use_id
                    tool_result_top = entry.get("toolUseResult")
                    has_tool_result = False

                    if tool_result_top:
                        source_tool_id = entry.get("sourceToolUseID", "")
                        if source_tool_id:
                            tool_results[source_tool_id] = tool_result_top
                            has_tool_result = True

                    # Also check content array for tool_result items
                    msg_content = msg.get("content", "")
                    if isinstance(msg_content, list):
                        for item in msg_content:
                            if isinstance(item, dict) and item.get("type") == "tool_result":
                                tool_use_id = item.get("tool_use_id", "")
                                if tool_use_id:
                                    tool_results[tool_use_id] = item
                                    has_tool_result = True

                    if not has_tool_result and not entry.get("isMeta"):
                        # It's a user prompt (or slash command invocation)
                        content = msg_content
                        if isinstance(content, list):
                            text_parts = []
                            for item in content:
                                if isinstance(item, dict) and item.get("type") == "text":
                                    text_parts.append(item.get("text", ""))
                            content = "\n".join(text_parts)
                        if isinstance(content, str) and content.strip():
                            # Use promptId if available, otherwise fall back
                            # to the entry's uuid so slash commands (which
                            # lack a promptId) still get captured.
                            effective_prompt_id = prompt_id or entry.get("uuid", str(uuid.uuid4()))
                            # Store in uuid_to_prompt_id so the parentUuid
                            # chain can resolve generations back to this prompt
                            entry_uuid = entry.get("uuid", "")
                            if entry_uuid and effective_prompt_id:
                                uuid_to_prompt_id[entry_uuid] = effective_prompt_id
                            prompts.append({
                                "prompt_id": effective_prompt_id,
                                "timestamp": timestamp,
                                "text": content if not privacy_mode else None,
                            })

            # Assistant messages (generations)
            # Session logs can have duplicate entries for the same message
            # (streaming updates). The later entry is more complete (has
            # tool_use blocks etc.), so we collect all entries and then
            # deduplicate by keeping the last occurrence per message ID.
            if entry_type == "assistant":
                msg = entry.get("message", {})
                if msg.get("role") != "assistant":
                    continue

                msg_id = msg.get("id", "")

                usage = msg.get("usage", {})
                model = msg.get("model", "unknown")
                stop_reason = msg.get("stop_reason")
                timestamp = entry.get("timestamp", "")
                entry_uuid = entry.get("uuid", "")
                prompt_id = resolve_prompt_id(entry_uuid)
                span_id = str(uuid.uuid4())

                # Extract text content, thinking blocks, and tool_use blocks
                content = msg.get("content", [])
                text_parts = []
                entry_tool_uses = []

                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict):
                            if item.get("type") == "text":
                                text_parts.append(item.get("text", ""))
                            elif item.get("type") == "thinking":
                                # Include thinking as output so responses
                                # that only think still show content
                                thinking_text = item.get("thinking", "")
                                if thinking_text:
                                    text_parts.append(thinking_text)
                            elif item.get("type") == "tool_use":
                                entry_tool_uses.append({
                                    "tool_use_id": item.get("id", ""),
                                    "name": item.get("name", "unknown"),
                                    "input": item.get("input"),
                                    "generation_span_id": span_id,
                                    "prompt_id": prompt_id,
                                    "timestamp": timestamp,
                                })

                output_text = "\n".join(text_parts) if text_parts else None

                # Build tool_use content blocks for $ai_output_choices
                # so PostHog's ingestion can extract $ai_tools_called
                tool_use_blocks = [
                    {"type": "tool_use", "name": tu["name"]}
                    for tu in entry_tool_uses
                ]

                generation = {
                    "model": model,
                    "input_tokens": usage.get("input_tokens", 0),
                    "output_tokens": usage.get("output_tokens", 0),
                    "cache_read_tokens": usage.get("cache_read_input_tokens", 0),
                    "cache_creation_tokens": usage.get("cache_creation_input_tokens", 0),
                    "stop_reason": stop_reason,
                    "timestamp": timestamp,
                    "prompt_id": prompt_id,
                    "span_id": span_id,
                    "output_text": output_text,
                    "tool_use_blocks": tool_use_blocks,
                    "is_error": stop_reason == "error",
                    "error_message": msg.get("error_message"),
                }

                # Overwrite earlier entries for the same msg_id (later
                # entries are more complete — they include tool_use blocks).
                key = msg_id or entry_uuid or str(uuid.uuid4())
                if key not in generations_by_msg_id:
                    generations_order.append(key)
                generations_by_msg_id[key] = (generation, entry_tool_uses)

            # Session summary
            if entry_type == "system" and entry.get("subtype") == "turn_duration":
                metadata["duration_ms"] = entry.get("durationMs")
                metadata["message_count"] = entry.get("messageCount")
                if not session_id:
                    session_id = entry.get("sessionId", "")

            # Capture metadata from any entry
            if not metadata.get("version"):
                metadata["version"] = entry.get("version", "")
            if not metadata.get("cwd"):
                metadata["cwd"] = entry.get("cwd", "")
            if not metadata.get("git_branch"):
                metadata["git_branch"] = entry.get("gitBranch", "")

    # Flatten deduplicated generations and tool uses
    generations = []
    tool_uses = []
    for key in generations_order:
        gen, tus = generations_by_msg_id[key]
        generations.append(gen)
        tool_uses.extend(tus)

    # Attach tool results to tool uses
    for tu in tool_uses:
        result = tool_results.get(tu["tool_use_id"])
        if result:
            tu["result"] = result

    return {
        "session_id": session_id,
        "generations": generations,
        "tool_uses": tool_uses,
        "prompts": prompts,
        "metadata": metadata,
    }


# ---------------------------------------------------------------------------
# Build PostHog events from parsed session
# ---------------------------------------------------------------------------

import re as _re

# Prompts that are framework noise — skip when picking a trace name
_SKIP_PROMPTS = _re.compile(
    r"^(/clear|/exit|/quit|/help|/compact|/reload|clear|exit|quit|"
    r"\[Request interrupted|\[Request cancelled)",
    _re.IGNORECASE,
)


def _clean_trace_name(text: str, max_len: int = 100) -> str:
    """Strip XML/HTML tags and truncate for use as a trace name."""
    cleaned = _re.sub(r"<[^>]+>", "", text).strip()
    # Collapse whitespace
    cleaned = " ".join(cleaned.split())
    return cleaned[:max_len] if cleaned else text[:max_len]


def _find_trace_name(prompts: list[dict], max_len: int = 100) -> str | None:
    """Find the first meaningful user prompt to use as a trace name."""
    for p in prompts:
        text = p.get("text", "")
        if not text:
            continue
        cleaned = _clean_trace_name(text, max_len)
        if cleaned and not _SKIP_PROMPTS.match(cleaned):
            return cleaned
    # Fallback: use whatever the first prompt is, even if noisy
    if prompts and prompts[0].get("text"):
        return _clean_trace_name(prompts[0]["text"], max_len)
    return None


def build_events(parsed: dict, config: dict) -> list[dict]:
    """Convert parsed session data into PostHog $ai_* events.

    Supports two trace grouping modes (POSTHOG_LLMA_TRACE_GROUPING):
      - "session" (default): one $ai_trace per session, all generations
        and spans grouped under it
      - "message": one $ai_trace per user prompt
    """
    events = []
    session_id = parsed["session_id"]
    cwd = parsed["metadata"].get("cwd", "")
    project_name = os.path.basename(cwd) if cwd else ""
    privacy_mode = config["privacy_mode"]
    trace_grouping = config.get("trace_grouping", "session")

    # In session mode, all events share one trace_id (the session_id).
    # In message mode, each prompt gets its own trace_id (the promptId).
    session_trace_id = session_id

    all_generations = parsed["generations"]
    all_tool_uses = parsed["tool_uses"]

    # Build $ai_generation events
    for gen in all_generations:
        trace_id = session_trace_id if trace_grouping == "session" else (gen.get("prompt_id") or str(uuid.uuid4()))

        output_choices = None
        if not privacy_mode:
            # Build output in Anthropic format so PostHog can extract
            # $ai_tools_called from content[].type="tool_use" blocks
            content_blocks = []
            if gen["output_text"]:
                content_blocks.append({"type": "text", "text": gen["output_text"]})
            content_blocks.extend(gen.get("tool_use_blocks", []))
            if content_blocks:
                output_choices = [{"role": "assistant", "content": content_blocks}]

        # Find the user prompt for this generation
        user_prompt = None
        input_messages = None
        for p in parsed["prompts"]:
            if p["prompt_id"] == gen.get("prompt_id"):
                user_prompt = p.get("text")
                if user_prompt and not privacy_mode:
                    input_messages = [{"role": "user", "content": user_prompt}]
                break

        events.append(posthog_llma.build_ai_generation(
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

    # Build $ai_span events for tool uses
    for tu in all_tool_uses:
        trace_id = session_trace_id if trace_grouping == "session" else (tu.get("prompt_id") or str(uuid.uuid4()))

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

        events.append(posthog_llma.build_ai_span(
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
            max_attribute_length=config["max_attribute_length"],
            timestamp=tu.get("timestamp"),
        ))

    # Build $ai_trace events
    if trace_grouping == "session":
        # One trace for the whole session
        total_input = sum(g["input_tokens"] for g in all_generations)
        total_output = sum(g["output_tokens"] for g in all_generations)
        has_error = any(g["is_error"] for g in all_generations)
        error_msg = next((g["error_message"] for g in all_generations if g.get("error_message")), None)

        # Session latency from first to last generation
        timestamps = [g["timestamp"] for g in all_generations if g.get("timestamp")]
        latency = None
        if len(timestamps) >= 2:
            try:
                from datetime import datetime as dt
                first = dt.fromisoformat(timestamps[0].replace("Z", "+00:00"))
                last = dt.fromisoformat(timestamps[-1].replace("Z", "+00:00"))
                latency = (last - first).total_seconds()
            except (ValueError, TypeError):
                pass

        # Use first generation timestamp for the trace
        trace_ts = timestamps[0] if timestamps else None

        # Use first meaningful user prompt as the trace name
        trace_name = _find_trace_name(parsed["prompts"])

        events.append(posthog_llma.build_ai_trace(
            trace_id=session_trace_id,
            session_id=session_id,
            trace_name=trace_name,
            latency_seconds=latency,
            total_input_tokens=total_input,
            total_output_tokens=total_output,
            is_error=has_error,
            error_message=error_msg,
            project_name=project_name,
            timestamp=trace_ts,
        ))
    else:
        # One trace per user prompt
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
            latency = None
            if len(timestamps) >= 2:
                try:
                    from datetime import datetime as dt
                    first = dt.fromisoformat(timestamps[0].replace("Z", "+00:00"))
                    last = dt.fromisoformat(timestamps[-1].replace("Z", "+00:00"))
                    latency = (last - first).total_seconds()
                except (ValueError, TypeError):
                    pass

            prompt_ts = timestamps[0] if timestamps else prompt.get("timestamp")
            trace_name = _find_trace_name([prompt])

            events.append(posthog_llma.build_ai_trace(
                trace_id=pid,
                session_id=session_id,
                trace_name=trace_name,
                latency_seconds=latency,
                total_input_tokens=total_input,
                total_output_tokens=total_output,
                is_error=has_error,
                error_message=error_msg,
                project_name=project_name,
                timestamp=prompt_ts,
            ))

    return events


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Load config — exit immediately if not configured
    config = load_config()
    if not config["enabled"] or not config["api_key"]:
        sys.exit(0)

    # Read hook input from stdin
    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    session_id = hook_input.get("session_id", "")
    cwd = hook_input.get("cwd", "")

    if not session_id or not cwd:
        sys.exit(0)

    # Find and parse session log
    jsonl_path = find_session_log(session_id, cwd)
    if not jsonl_path:
        sys.exit(0)

    parsed = parse_session(jsonl_path, config)
    if not parsed["generations"]:
        sys.exit(0)

    # Build events
    events = build_events(parsed, config)
    if not events:
        sys.exit(0)

    # Determine distinct_id
    distinct_id = config["distinct_id"]
    if not distinct_id:
        # Try git user email
        try:
            import subprocess
            result = subprocess.run(
                ["git", "config", "user.email"],
                capture_output=True, text=True, timeout=2, cwd=cwd,
            )
            if result.returncode == 0 and result.stdout.strip():
                distinct_id = result.stdout.strip()
        except Exception:
            pass
    if not distinct_id:
        distinct_id = f"claude-code:{session_id}"

    # Send to PostHog
    result = posthog_llma.send_batch(
        events,
        api_key=config["api_key"],
        host=config["host"],
        distinct_id=distinct_id,
    )

    # Write status for /posthog:llma-status
    posthog_llma.write_status({
        "session_id": session_id,
        "events_sent": result.get("sent", 0),
        "generations": len(parsed["generations"]),
        "tool_uses": len(parsed["tool_uses"]),
        "traces": len(parsed["prompts"]),
        "status": result.get("status", "unknown"),
        "error": result.get("error"),
        "host": config["host"],
        "distinct_id": distinct_id,
        "project_name": os.path.basename(cwd) if cwd else "",
    })

    # Exit 0 regardless — don't disrupt the session end
    sys.exit(0)


if __name__ == "__main__":
    main()
