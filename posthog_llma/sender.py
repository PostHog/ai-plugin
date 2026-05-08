"""Send batches of events to PostHog and manage status file."""

import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse

DEFAULT_HOST = "https://us.i.posthog.com"
STATUS_FILE = os.path.expanduser("~/.claude/posthog-llma-status.json")

# Hostname suffixes treated as known PostHog endpoints. Leading dot enforces
# a domain-component boundary so `evilposthog.com` is not accepted.
_POSTHOG_HOST_SUFFIXES = (".posthog.com",)
_LOCALHOST_HOSTNAMES = frozenset({"localhost", "127.0.0.1", "::1"})


def validate_host(host: str) -> tuple[bool, str]:
    """Check whether ``host`` is safe to POST telemetry to.

    The telemetry payload contains prompts, tool I/O, and the PostHog API
    key. Without this check, a project-scoped ``settings.json`` could set
    ``POSTHOG_HOST`` to an attacker-controlled URL and silently exfiltrate
    every Claude Code session. We accept:

    - ``https://`` URLs whose hostname ends in ``.posthog.com``
    - ``http(s)://localhost`` for local development
    - any host when ``POSTHOG_LLMA_ALLOW_CUSTOM_HOST=true`` (self-hosted opt-in)

    Returns ``(ok, reason)`` where ``reason`` is empty on success.
    """
    if not host:
        return False, "POSTHOG_HOST is empty"

    try:
        parsed = urlparse(host if "://" in host else f"https://{host}")
    except ValueError as e:
        return False, f"POSTHOG_HOST is not a valid URL: {e}"

    scheme = (parsed.scheme or "").lower()
    hostname = (parsed.hostname or "").lower()

    if not hostname:
        return False, "POSTHOG_HOST has no hostname"
    if scheme not in ("https", "http"):
        return False, f"POSTHOG_HOST scheme must be https (got {scheme!r})"
    if scheme == "http" and hostname not in _LOCALHOST_HOSTNAMES:
        return False, "POSTHOG_HOST must use https:// (http:// is only allowed for localhost)"

    if hostname in _LOCALHOST_HOSTNAMES:
        return True, ""
    if any(hostname == s.lstrip(".") or hostname.endswith(s) for s in _POSTHOG_HOST_SUFFIXES):
        return True, ""
    if os.environ.get("POSTHOG_LLMA_ALLOW_CUSTOM_HOST", "").lower() == "true":
        return True, ""

    return False, (
        f"POSTHOG_HOST {hostname!r} is not a known PostHog endpoint; "
        "set POSTHOG_LLMA_ALLOW_CUSTOM_HOST=true to allow a self-hosted instance"
    )


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

    ok, reason = validate_host(host)
    if not ok:
        return {"status": "error", "error": f"refused to send: {reason}"}

    batch = []
    fallback_ts = datetime.now(timezone.utc).isoformat()

    for ev in events:
        batch.append({
            "event": ev["event"],
            "properties": {
                **ev["properties"],
                "$lib": "posthog-ai-plugin",
            },
            "distinct_id": distinct_id,
            "timestamp": ev.get("timestamp") or fallback_ts,
        })

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
