"""Send batches of events to PostHog and manage status file."""

import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Optional

DEFAULT_HOST = "https://us.i.posthog.com"
STATUS_FILE = os.path.expanduser("~/.claude/posthog-llma-status.json")


def send_batch(
    events: list[dict],
    *,
    api_key: str,
    host: str = DEFAULT_HOST,
    distinct_id: str,
) -> dict:
    """Send a batch of events to PostHog's /batch endpoint.

    Each event dict must have 'event' and 'properties' keys,
    and optionally a 'timestamp' key.

    Returns {"status": "ok", "sent": N} on success or
    {"status": "error", "error": str}.
    """
    if not events:
        return {"status": "ok", "sent": 0}

    batch = []
    fallback_ts = datetime.now(timezone.utc).isoformat()

    for ev in events:
        entry = {
            "event": ev["event"],
            "properties": {
                **ev["properties"],
                "$lib": "posthog-ai-plugin",
            },
            "distinct_id": distinct_id,
            "timestamp": ev.get("timestamp") or fallback_ts,
        }
        # PostHog's /batch endpoint dedupes on the event-level `uuid`
        # field via ClickHouse's ReplacingMergeTree. Pass through when
        # the builder set it (deterministic uuid5 in event_builder.py).
        if ev.get("uuid"):
            entry["uuid"] = ev["uuid"]
        batch.append(entry)

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


def write_status(status: dict) -> None:
    """Write last send status for /posthog:llma-cc-status to read."""
    status["timestamp"] = datetime.now(timezone.utc).isoformat()
    try:
        os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
        with open(STATUS_FILE, "w") as f:
            json.dump(status, f, indent=2)
    except OSError:
        pass


def read_status() -> Optional[dict]:
    """Read last send status."""
    try:
        with open(STATUS_FILE) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
