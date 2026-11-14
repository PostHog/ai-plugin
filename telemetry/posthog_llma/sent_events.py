"""Remember what each session sent, so a session that ends again sends only new or changed events.

The SessionEnd hook re-reads the whole session log every time a session
ends, including after `claude --resume`. ClickHouse merges the copies by
event UUID, but every copy still goes through ingestion again first.
"""

import hashlib
import json
import os
import time

from posthog_llma.sender import DEFAULT_HOST, send_batch

SENT_DIR = os.path.expanduser("~/.claude/posthog-llma-sent")
# Claude Code keeps session logs for `cleanupPeriodDays`, 30 days by
# default. A session whose log is deleted cannot end again, so its record
# of sent events has no further use.
RETENTION_SECONDS = 30 * 24 * 60 * 60


def send_new_events(
    events: list[dict],
    *,
    session_id: str,
    api_key: str,
    host: str = DEFAULT_HOST,
    distinct_id: str,
) -> dict:
    """Send the events that this session has not sent before in the same form.

    Records the sent events only when PostHog accepts the batch, so a failed
    send is tried again when the session next ends. Returns the result of
    `send_batch`.
    """
    sent = _load(session_id)
    unsent = [event for event in events if not event.get("uuid") or sent.get(event["uuid"]) != _fingerprint(event)]
    result = send_batch(unsent, api_key=api_key, host=host, distinct_id=distinct_id)
    if result.get("status") == "ok":
        sent.update({event["uuid"]: _fingerprint(event) for event in unsent if event.get("uuid")})
        _save(session_id, sent)
    return result


def _fingerprint(event: dict) -> str:
    return hashlib.sha256(json.dumps(event, sort_keys=True).encode("utf-8")).hexdigest()


def _path(session_id: str) -> str:
    return os.path.join(SENT_DIR, f"{session_id}.json")


def _load(session_id: str) -> dict:
    # A missing or damaged file makes the session send every event again.
    # That is safe, because ClickHouse merges the copies by event UUID.
    try:
        with open(_path(session_id)) as f:
            sent = json.load(f)
    except (OSError, ValueError):
        return {}
    return sent if isinstance(sent, dict) else {}


def _save(session_id: str, sent: dict) -> None:
    try:
        os.makedirs(SENT_DIR, exist_ok=True)
        path = _path(session_id)
        # Write a temporary file and rename it. If Claude Code stops the
        # hook during the write, the record stays whole.
        tmp_path = f"{path}.tmp"
        with open(tmp_path, "w") as f:
            json.dump(sent, f)
        os.replace(tmp_path, path)
        _remove_expired()
    except OSError:
        pass


def _remove_expired() -> None:
    cutoff = time.time() - RETENTION_SECONDS
    for name in os.listdir(SENT_DIR):
        path = os.path.join(SENT_DIR, name)
        try:
            if os.path.getmtime(path) < cutoff:
                os.remove(path)
        except OSError:
            pass
