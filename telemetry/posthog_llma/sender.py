"""Send batches of events to PostHog and manage status file."""

import json
import os
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Callable, Optional

DEFAULT_HOST = "https://us.i.posthog.com"
STATUS_FILE = os.path.expanduser("~/.claude/posthog-llma-status.json")

# PostHog's capture endpoint refuses request bodies over 20MB. 5MB leaves
# room, and keeps each POST well inside the 10 s urlopen timeout.
MAX_BATCH_BYTES = 5 * 1024 * 1024

# Bytes reserved for the payload's api_key and JSON wrapper.
_ENVELOPE_BYTES = 200

# Too little time left for a POST to finish; send_chunks stops below this.
MIN_POST_SECONDS = 2


def _batch_entry(ev: dict, distinct_id: str, fallback_ts: str) -> dict:
    """Build one entry of a /batch payload from an event dict."""
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
    return entry


def send_batch(
    events: list[dict],
    *,
    api_key: str,
    host: str = DEFAULT_HOST,
    distinct_id: str,
    timeout: float = 10,
) -> dict:
    """Send a batch of events to PostHog's /batch endpoint.

    Each event dict must have 'event' and 'properties' keys,
    and optionally a 'timestamp' key.

    Returns {"status": "ok", "sent": N} on success or
    {"status": "error", "error": str}.
    """
    if not events:
        return {"status": "ok", "sent": 0}

    fallback_ts = datetime.now(timezone.utc).isoformat()
    batch = [_batch_entry(ev, distinct_id, fallback_ts) for ev in events]

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
        with urllib.request.urlopen(req, timeout=timeout) as resp:
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


def chunk_events(
    events: list[dict],
    *,
    distinct_id: str,
    max_bytes: Optional[int] = None,
) -> list[list[dict]]:
    """Split events, in order, into chunks whose /batch bodies stay within max_bytes.

    An event larger than max_bytes on its own goes in a chunk by itself.
    It is never dropped or split.
    """
    if max_bytes is None:
        # Read at call time, so a changed MAX_BATCH_BYTES takes effect.
        max_bytes = MAX_BATCH_BYTES
    fallback_ts = datetime.now(timezone.utc).isoformat()
    chunks = []
    current = []
    size = _ENVELOPE_BYTES
    for ev in events:
        entry = _batch_entry(ev, distinct_id, fallback_ts)
        # The +1 is the comma that separates entries in the JSON array.
        entry_bytes = len(json.dumps(entry).encode("utf-8")) + 1
        if current and size + entry_bytes > max_bytes:
            chunks.append(current)
            current = []
            size = _ENVELOPE_BYTES
        current.append(ev)
        size += entry_bytes
    if current:
        chunks.append(current)
    return chunks


def send_chunks(
    events: list[dict],
    *,
    api_key: str,
    host: str = DEFAULT_HOST,
    distinct_id: str,
    max_bytes: Optional[int] = None,
    deadline: Optional[float] = None,
    on_sent: Optional[Callable[[list[dict]], None]] = None,
) -> dict:
    """Send events as size-bounded /batch requests, in order.

    Stops at the first failed chunk, or before starting a chunk once less
    than MIN_POST_SECONDS remains before `deadline` (a time.monotonic()
    value). Each POST's timeout is capped by the time left before
    `deadline`. `on_sent(chunk)` runs after each accepted chunk. Returns {"status": "ok", "sent": N} or
    {"status": "error", "sent": N, "error": str}, where N counts the events
    in the chunks accepted so far.
    """
    total = 0
    for chunk in chunk_events(events, distinct_id=distinct_id, max_bytes=max_bytes):
        timeout = 10
        if deadline is not None:
            remaining = deadline - time.monotonic()
            if remaining < MIN_POST_SECONDS:
                return {
                    "status": "error",
                    "sent": total,
                    "error": "stopped before the hook timeout; the rest is sent at the next session end",
                }
            # Cap the POST's timeout at the time left, so a slow PostHog
            # cannot hold the hook past the deadline.
            timeout = min(10, remaining)
        result = send_batch(chunk, api_key=api_key, host=host, distinct_id=distinct_id, timeout=timeout)
        if result.get("status") != "ok":
            return {"status": "error", "sent": total, "error": result.get("error")}
        total += result.get("sent", 0)
        if on_sent:
            on_sent(chunk)
    return {"status": "ok", "sent": total}


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
