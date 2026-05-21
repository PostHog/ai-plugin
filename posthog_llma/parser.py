"""Claude Code session JSONL parser.

Reads a Claude Code session log and extracts generations, tool uses,
prompts, and metadata into a structured dict.
"""

import json
import uuid
from pathlib import Path
from typing import Optional


def find_session_log(session_id: str, cwd: str) -> Optional[str]:
    """Find the JSONL session log file.

    Claude Code stores logs at:
        ~/.claude/projects/{cwd-with-special-chars-replaced}/{session_id}.jsonl

    Claude Code collapses `/`, `.`, `\\`, `:`, `_`, and spaces to `-` when
    naming the project dir, and the exact rules have drifted across versions
    and platforms (Windows paths, paths under `.claude` worktrees, paths
    with underscores or spaces, etc.). Rather than mirror that rule set, we
    try the direct lookup first and fall back to a glob across project dirs
    — session IDs are UUIDs and unique, so the match is unambiguous.
    """
    base = Path.home() / ".claude" / "projects"
    project_dir_name = cwd.replace("/", "-")
    direct = base / project_dir_name / f"{session_id}.jsonl"
    if direct.is_file():
        return str(direct)
    for candidate in base.glob(f"*/{session_id}.jsonl"):
        return str(candidate)
    return None


def parse_session(jsonl_path: str, config: dict) -> dict:
    """Parse a Claude Code session JSONL file into structured data.

    Returns:
        {
            "session_id": str,
            "generations": [...],
            "tool_uses": [...],
            "prompts": [...],
            "metadata": {...},
        }
    """
    generations_by_msg_id = {}  # msg_id -> (generation_dict, [tool_uses])
    generations_order = []      # preserve insertion order of msg_ids
    tool_results = {}           # tool_use_id -> result content
    prompts = []                # {prompt_id, timestamp, text}
    metadata = {}

    session_id = ""
    privacy_mode = config.get("privacy_mode", False)

    # Maps for resolving promptId via parentUuid chains.
    # Assistant messages don't carry promptId directly — it lives on the
    # originating user message. We walk parentUuid up the chain to find it.
    uuid_to_prompt_id = {}  # uuid -> promptId
    uuid_to_parent = {}     # uuid -> parentUuid

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

            # Session metadata. The Claude Code CLI emits a permission-mode
            # entry at the top of every session, but the Claude Agent SDK
            # JSONL format does not — every entry just carries `sessionId`.
            # Pull it opportunistically so SDK sessions still get a non-empty
            # $ai_session_id / $ai_trace_id.
            if not session_id:
                session_id = entry.get("sessionId", "") or session_id
            if entry_type == "permission-mode":
                session_id = entry.get("sessionId", "") or session_id

            # User messages (prompts + tool results)
            if entry_type == "user":
                _process_user_entry(
                    entry, privacy_mode, tool_results, prompts,
                    uuid_to_prompt_id,
                )

            # Assistant messages (generations)
            if entry_type == "assistant":
                _process_assistant_entry(
                    entry, resolve_prompt_id,
                    generations_by_msg_id, generations_order,
                )

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

    # Flatten merged per-msg_id states into generations + tool_uses
    generations = []
    tool_uses = []
    for key in generations_order:
        gen, tus = _finalize_generation(generations_by_msg_id[key])
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


def _process_user_entry(
    entry: dict,
    privacy_mode: bool,
    tool_results: dict,
    prompts: list,
    uuid_to_prompt_id: dict,
) -> None:
    """Process a user-type JSONL entry."""
    msg = entry.get("message", {})
    if msg.get("role") != "user":
        return

    prompt_id = entry.get("promptId", "")
    timestamp = entry.get("timestamp", "")

    # Check for tool results (two formats)
    tool_result_top = entry.get("toolUseResult")
    has_tool_result = False

    if tool_result_top:
        source_tool_id = entry.get("sourceToolUseID", "")
        if source_tool_id:
            tool_results[source_tool_id] = tool_result_top
            has_tool_result = True

    msg_content = msg.get("content", "")
    if isinstance(msg_content, list):
        for item in msg_content:
            if isinstance(item, dict) and item.get("type") == "tool_result":
                tool_use_id = item.get("tool_use_id", "")
                if tool_use_id:
                    tool_results[tool_use_id] = item
                    has_tool_result = True

    if has_tool_result or entry.get("isMeta"):
        return

    # It's a user prompt (or slash command invocation)
    content = msg_content
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))
        content = "\n".join(text_parts)

    if not isinstance(content, str) or not content.strip():
        return

    # Use promptId if available, otherwise fall back to the entry's uuid
    # so slash commands (which lack a promptId) still get captured.
    effective_prompt_id = prompt_id or entry.get("uuid", str(uuid.uuid4()))
    entry_uuid = entry.get("uuid", "")
    if entry_uuid and effective_prompt_id:
        uuid_to_prompt_id[entry_uuid] = effective_prompt_id

    prompts.append({
        "prompt_id": effective_prompt_id,
        "timestamp": timestamp,
        "text": content if not privacy_mode else None,
    })


def _process_assistant_entry(
    entry: dict,
    resolve_prompt_id,
    generations_by_msg_id: dict,
    generations_order: list,
) -> None:
    """Process an assistant-type JSONL entry.

    Session logs can have multiple entries for the same message ID, and
    the Claude Agent SDK splits content blocks across them — one entry
    may carry only `thinking`, the next only `tool_use`, the next only
    `text`. Naively overwriting per msg_id drops every block except the
    last entry's, so thinking content vanishes from $ai_output_choices.

    Instead, merge per content type:
      - When an entry carries blocks of a type we've seen, replace that
        type's blocks (handles cumulative streaming where each chunk
        repeats prior content in a longer form).
      - When an entry carries blocks of a type we haven't seen, add them
        (handles delta streaming where each chunk has only new content).

    Usage/stop_reason/timestamp/model are taken from the latest non-empty
    chunk — Claude Code typically emits these on the final entry.
    """
    msg = entry.get("message", {})
    if msg.get("role") != "assistant":
        return

    msg_id = msg.get("id", "")
    usage = msg.get("usage", {})
    model = msg.get("model", "")
    stop_reason = msg.get("stop_reason")
    timestamp = entry.get("timestamp", "")
    entry_uuid = entry.get("uuid", "")
    prompt_id = resolve_prompt_id(entry_uuid)

    # Group this entry's content blocks by type
    entry_blocks_by_type = {"thinking": [], "text": [], "tool_use": []}
    content = msg.get("content", [])
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict):
                t = item.get("type")
                if t in entry_blocks_by_type:
                    entry_blocks_by_type[t].append(item)

    key = msg_id or entry_uuid or str(uuid.uuid4())

    state = generations_by_msg_id.get(key)
    if state is None:
        state = {
            "model": model or "unknown",
            "usage": usage,
            "stop_reason": stop_reason,
            "timestamp": timestamp,
            "prompt_id": prompt_id,
            "span_id": str(uuid.uuid4()),
            "msg_id": msg_id,
            "blocks_by_type": {"thinking": [], "text": [], "tool_use": []},
            # Order types by first appearance across chunks rather than
            # assuming thinking → text → tool_use. Most Anthropic streams
            # do follow that order, but if a chunk arrives text-first the
            # output sequence should still reflect what the model produced.
            "type_order": [],
            "error_message": msg.get("error_message"),
        }
        generations_by_msg_id[key] = state
        generations_order.append(key)

    # Merge content blocks per type, preserving first-seen order
    for t, blocks in entry_blocks_by_type.items():
        if blocks:
            if t not in state["type_order"]:
                state["type_order"].append(t)
            state["blocks_by_type"][t] = blocks

    # Take latest non-empty metadata
    if usage:
        state["usage"] = usage
    if stop_reason:
        state["stop_reason"] = stop_reason
    if timestamp:
        state["timestamp"] = timestamp
    if model:
        state["model"] = model
    if msg.get("error_message"):
        state["error_message"] = msg["error_message"]
    # prompt_id can resolve later as more entries arrive
    if not state["prompt_id"] and prompt_id:
        state["prompt_id"] = prompt_id


def _finalize_generation(state: dict) -> tuple[dict, list]:
    """Convert a merged per-msg_id state into a (generation, tool_uses) pair."""
    span_id = state["span_id"]
    prompt_id = state["prompt_id"]
    timestamp = state["timestamp"]
    usage = state.get("usage") or {}

    blocks = state["blocks_by_type"]
    # Fall back to a sensible default order for older state dicts; new
    # entries populate type_order in first-seen order during the merge.
    type_order = state.get("type_order") or ["thinking", "text", "tool_use"]

    text_parts = []
    entry_tool_uses = []
    for block_type in type_order:
        if block_type == "thinking":
            for item in blocks.get("thinking", []):
                t = item.get("thinking", "")
                if t:
                    text_parts.append(t)
        elif block_type == "text":
            for item in blocks.get("text", []):
                t = item.get("text", "")
                if t:
                    text_parts.append(t)
        elif block_type == "tool_use":
            for item in blocks.get("tool_use", []):
                entry_tool_uses.append({
                    "tool_use_id": item.get("id", ""),
                    "name": item.get("name", "unknown"),
                    "input": item.get("input"),
                    "generation_span_id": span_id,
                    "prompt_id": prompt_id,
                    "timestamp": timestamp,
                })

    tool_use_blocks = [
        {"type": "tool_use", "name": tu["name"], "input": tu.get("input")}
        for tu in entry_tool_uses
    ]
    output_text = "\n".join(text_parts) if text_parts else None
    stop_reason = state.get("stop_reason")

    generation = {
        "model": state.get("model") or "unknown",
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
        "cache_read_tokens": usage.get("cache_read_input_tokens", 0),
        "cache_creation_tokens": usage.get("cache_creation_input_tokens", 0),
        "stop_reason": stop_reason,
        "timestamp": timestamp,
        "prompt_id": prompt_id,
        "span_id": span_id,
        "msg_id": state.get("msg_id", ""),
        "output_text": output_text,
        "tool_use_blocks": tool_use_blocks,
        "is_error": stop_reason == "error",
        "error_message": state.get("error_message"),
    }
    return generation, entry_tool_uses
