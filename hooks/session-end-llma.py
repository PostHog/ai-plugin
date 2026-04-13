#!/usr/bin/env python3
"""Claude Code SessionEnd hook — thin entry point.

Parses session JSONL and sends $ai_generation, $ai_span, $ai_trace
events to PostHog LLM Analytics. No-op unless POSTHOG_LLMA_CC_ENABLED
is set to true and POSTHOG_API_KEY is set.
"""

import json
import os
import subprocess
import sys

# Add plugin root to path so we can import the posthog_llma package
PLUGIN_ROOT = os.environ.get(
    "CLAUDE_PLUGIN_ROOT",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)
sys.path.insert(0, PLUGIN_ROOT)

from posthog_llma import (  # noqa: E402
    load_config,
    find_session_log,
    parse_session,
    build_events,
    send_batch,
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

    result = send_batch(
        events,
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
