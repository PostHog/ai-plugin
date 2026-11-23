#!/usr/bin/env python3
"""Claude Code SessionEnd hook — thin entry point.

Parses session JSONL and sends $ai_generation, $ai_span, $ai_trace
events to PostHog LLM Analytics. No-op unless POSTHOG_LLMA_CC_ENABLED
is set to true and POSTHOG_API_KEY is set.
"""

import glob
import json
import os
import subprocess
import sys

# Resolved from __file__, never from CLAUDE_PLUGIN_ROOT: the package sits
# beside this hooks/ directory in both plugins, while CLAUDE_PLUGIN_ROOT
# differs between them.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from posthog_llma import (  # noqa: E402
    load_config,
    find_session_log,
    parse_session,
    build_events,
    send_new_events,
    write_status,
)


def main():
    try:
        _run()
    except Exception:
        # Never crash — losing a session send is fine, interfering
        # with the user's workflow is not.
        sys.exit(0)


def _run():
    config = load_config()
    if not config["enabled"] or not config["api_key"]:
        sys.exit(0)

    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    session_id = hook_input.get("session_id", "")
    cwd = hook_input.get("cwd", "")
    if not session_id or not cwd:
        sys.exit(0)

    jsonl_path = find_session_log(session_id, cwd)
    if not jsonl_path:
        sys.exit(0)

    parsed = parse_session(jsonl_path, config)

    # Subagent transcripts live beside the session log at
    # <session_id>/subagents/agent-*.jsonl. Their generations and tool
    # uses belong in the same batch; their prompts are internal Task
    # calls, not user prompts, so they are not merged in.
    pattern = os.path.join(
        os.path.dirname(jsonl_path), session_id, "subagents", "agent-*.jsonl")
    seen = {g["msg_id"] for g in parsed["generations"] if g.get("msg_id")}
    for path in sorted(glob.glob(pattern)):
        try:
            sub = parse_session(path, config)
        except Exception:
            # One malformed subagent file (a cut multi-byte character, a
            # line of an unexpected shape) must not drop the whole batch.
            continue
        dup_spans = set()
        for gen in sub["generations"]:
            if gen.get("msg_id") and gen["msg_id"] in seen:
                dup_spans.add(gen["span_id"])
                continue
            seen.add(gen.get("msg_id"))
            parsed["generations"].append(gen)
        parsed["tool_uses"].extend(
            tu for tu in sub["tool_uses"]
            if tu.get("generation_span_id") not in dup_spans)

    if not parsed["generations"]:
        sys.exit(0)

    events = build_events(parsed, config)
    if not events:
        sys.exit(0)

    # Determine distinct_id
    distinct_id = config["distinct_id"]
    if not distinct_id:
        try:
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

    result = send_new_events(
        events,
        session_id=session_id,
        api_key=config["api_key"],
        host=config["host"],
        distinct_id=distinct_id,
    )

    write_status({
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

    sys.exit(0)


if __name__ == "__main__":
    main()
