"""Claude Code session JSONL parser.

Reads a Claude Code session log and extracts generations, tool uses,
prompts, and metadata into a structured dict.
"""

import json
import uuid
from pathlib import Path


def find_session_log(session_id: str, cwd: str) -> str | None:
    """Find the JSONL session log file.

    Claude Code stores logs at:
        ~/.claude/projects/{cwd-with-slashes-replaced}/{session_id}.jsonl
    """
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

            # Session metadata
            if entry_type == "permission-mode":
                session_id = entry.get("sessionId", "")

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

    Session logs can have duplicate entries for the same message
    (streaming updates). The later entry is more complete (has
    tool_use blocks), so we overwrite earlier entries per message ID.
    """
    msg = entry.get("message", {})
    if msg.get("role") != "assistant":
        return

    msg_id = msg.get("id", "")
    usage = msg.get("usage", {})
    model = msg.get("model", "unknown")
    stop_reason = msg.get("stop_reason")
    timestamp = entry.get("timestamp", "")
    entry_uuid = entry.get("uuid", "")
    prompt_id = resolve_prompt_id(entry_uuid)
    span_id = str(uuid.uuid4())

    # Extract text, thinking blocks, and tool_use blocks
    content = msg.get("content", [])
    text_parts = []
    entry_tool_uses = []

    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
                elif item.get("type") == "thinking":
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

    key = msg_id or entry_uuid or str(uuid.uuid4())
    if key not in generations_by_msg_id:
        generations_order.append(key)
    generations_by_msg_id[key] = (generation, entry_tool_uses)
