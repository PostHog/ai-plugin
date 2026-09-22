#!/usr/bin/env python3
"""Manually ingest a Claude Code session log into PostHog LLM Analytics.

Usage:
    python3 llma_cc_ingest.py                          # most recent session for cwd
    python3 llma_cc_ingest.py <session-id>             # by session ID
    python3 llma_cc_ingest.py <path-to-jsonl>          # by file path
    python3 llma_cc_ingest.py --list                   # list recent sessions
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Add plugin root to path
PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PLUGIN_ROOT)

from posthog_llma import (  # noqa: E402
    parse_session,
    build_events,
    send_batch,
    DEFAULT_HOST,
)


def find_project_dir() -> Optional[Path]:
    """Find the Claude projects directory for the current working directory."""
    cwd = os.getcwd()
    project_dir_name = cwd.replace("/", "-")
    project_dir = Path.home() / ".claude" / "projects" / project_dir_name
    if project_dir.is_dir():
        return project_dir
    return None


def list_sessions(project_dir: Optional[Path] = None, limit: int = 10) -> list[dict]:
    """List recent session logs."""
    if project_dir:
        jsonl_files = list(project_dir.glob("*.jsonl"))
    else:
        projects_dir = Path.home() / ".claude" / "projects"
        jsonl_files = list(projects_dir.glob("**/*.jsonl"))

    jsonl_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    sessions = []

    for f in jsonl_files[:limit]:
        session_id = f.stem
        size_kb = f.stat().st_size / 1024
        first_prompt = ""
        try:
            with open(f) as fh:
                for line in fh:
                    entry = json.loads(line)
                    if (entry.get("type") == "user"
                            and not entry.get("toolUseResult")
                            and not entry.get("isMeta")):
                        msg = entry.get("message", {}).get("content", "")
                        if isinstance(msg, str) and msg.strip():
                            first_prompt = msg.strip()[:60]
                            break
                        elif isinstance(msg, list):
                            for item in msg:
                                if isinstance(item, dict) and item.get("type") == "text":
                                    first_prompt = item.get("text", "").strip()[:60]
                                    break
                            if first_prompt:
                                break
        except (json.JSONDecodeError, OSError):
            pass

        sessions.append({
            "session_id": session_id,
            "path": str(f),
            "size_kb": round(size_kb, 1),
            "first_prompt": first_prompt,
            "project": f.parent.name,
        })

    return sessions


def resolve_session_path(arg: str) -> Optional[str]:
    """Resolve a session ID or path to a JSONL file path."""
    expanded = os.path.expanduser(arg)
    if os.path.isfile(expanded):
        return expanded

    projects_dir = Path.home() / ".claude" / "projects"
    matches = list(projects_dir.glob(f"**/{arg}.jsonl"))
    if matches:
        return str(matches[0])

    matches = list(projects_dir.glob(f"**/{arg}*.jsonl"))
    if len(matches) == 1:
        return str(matches[0])
    elif len(matches) > 1:
        print(f"Multiple matches for '{arg}':")
        for m in matches:
            print(f"  {m}")
        return None

    return None


def ingest(jsonl_path: str) -> dict:
    """Parse and send a session log to PostHog."""
    api_key = os.environ.get("POSTHOG_API_KEY", "")
    if not api_key:
        return {"status": "error", "error": "POSTHOG_API_KEY not set"}

    host = os.environ.get("POSTHOG_HOST", DEFAULT_HOST)
    privacy_mode = os.environ.get("POSTHOG_LLMA_PRIVACY_MODE", "false").lower() == "true"
    trace_grouping = os.environ.get("POSTHOG_LLMA_TRACE_GROUPING", "session")
    max_attr = int(os.environ.get("POSTHOG_LLMA_MAX_ATTRIBUTE_LENGTH", "12000"))

    custom_props = {}
    raw = os.environ.get("POSTHOG_LLMA_CUSTOM_PROPERTIES", "")
    if raw:
        try:
            parsed_props = json.loads(raw)
            if isinstance(parsed_props, dict):
                custom_props = parsed_props
        except (json.JSONDecodeError, ValueError):
            pass

    config = {
        "privacy_mode": privacy_mode,
        "max_attribute_length": max_attr,
        "trace_grouping": trace_grouping,
        "custom_properties": custom_props,
    }

    parsed = parse_session(jsonl_path, config)
    if not parsed["generations"]:
        return {"status": "error", "error": "No generations found in session log"}

    events = build_events(parsed, config)
    if not events:
        return {"status": "error", "error": "No events built"}

    distinct_id = os.environ.get("POSTHOG_LLMA_DISTINCT_ID", "")
    if not distinct_id:
        try:
            result = subprocess.run(
                ["git", "config", "user.email"],
                capture_output=True, text=True, timeout=2,
            )
            if result.returncode == 0 and result.stdout.strip():
                distinct_id = result.stdout.strip()
        except Exception:
            pass
    if not distinct_id:
        distinct_id = f"claude-code:{parsed['session_id']}"

    result = send_batch(
        events,
        api_key=api_key,
        host=host,
        distinct_id=distinct_id,
    )

    gen_count = sum(1 for e in events if e["event"] == "$ai_generation")
    span_count = sum(1 for e in events if e["event"] == "$ai_span")
    trace_count = sum(1 for e in events if e["event"] == "$ai_trace")

    return {
        **result,
        "session_id": parsed["session_id"],
        "generations": gen_count,
        "spans": span_count,
        "traces": trace_count,
        "total_events": len(events),
        "host": host,
        "distinct_id": distinct_id,
    }


def main():
    args = sys.argv[1:]

    if not args or args == [""]:
        project_dir = find_project_dir()
        if not project_dir:
            print("No Claude Code sessions found for the current directory.")
            print("Use --list to see all sessions, or provide a session ID or path.")
            sys.exit(1)

        sessions = list_sessions(project_dir, limit=1)
        if not sessions:
            print("No session logs found.")
            sys.exit(1)

        jsonl_path = sessions[0]["path"]
        print(f"Ingesting most recent session: {sessions[0]['session_id']}")
        if sessions[0]["first_prompt"]:
            print(f"  First prompt: {sessions[0]['first_prompt']}")

    elif args[0] == "--list":
        project_dir = find_project_dir()
        sessions = list_sessions(project_dir, limit=10)
        if not sessions:
            print("No session logs found.")
            sys.exit(0)

        print(f"Recent sessions ({len(sessions)}):\n")
        for s in sessions:
            prompt = f' — "{s["first_prompt"]}"' if s["first_prompt"] else ""
            print(f"  {s['session_id']}  ({s['size_kb']}KB){prompt}")
        print(f"\nUsage: python3 {sys.argv[0]} <session-id>")
        sys.exit(0)

    else:
        jsonl_path = resolve_session_path(args[0])
        if not jsonl_path:
            print(f"Could not find session: {args[0]}")
            sys.exit(1)
        print(f"Ingesting: {jsonl_path}")

    result = ingest(jsonl_path)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("status") == "ok" else 1)


if __name__ == "__main__":
    main()
