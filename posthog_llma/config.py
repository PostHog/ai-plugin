"""Configuration loading from environment variables.

All configuration is via env vars. Users can set these in their shell
profile or in Claude Code's settings.json "env" block:

    // ~/.claude/settings.json (global)
    // .claude/settings.local.json (per-project, gitignored)
    {
      "env": {
        "POSTHOG_LLMA_CC_ENABLED": "true",
        "POSTHOG_API_KEY": "phc_...",
        "POSTHOG_HOST": "https://eu.i.posthog.com"
      }
    }
"""

import os

from posthog_llma.sender import DEFAULT_HOST


def load_config() -> dict:
    """Load configuration from environment variables.

    Both POSTHOG_LLMA_CC_ENABLED=true and POSTHOG_API_KEY are required
    for the hook to send data. All other settings have sensible defaults.
    """
    return {
        "api_key": os.environ.get("POSTHOG_API_KEY", ""),
        "host": os.environ.get("POSTHOG_HOST", DEFAULT_HOST),
        "privacy_mode": os.environ.get("POSTHOG_LLMA_PRIVACY_MODE", "false").lower() == "true",
        "enabled": os.environ.get("POSTHOG_LLMA_CC_ENABLED", "false").lower() == "true",
        "distinct_id": os.environ.get("POSTHOG_LLMA_DISTINCT_ID", ""),
        "max_attribute_length": int(os.environ.get("POSTHOG_LLMA_MAX_ATTRIBUTE_LENGTH", "12000")),
        "trace_grouping": os.environ.get("POSTHOG_LLMA_TRACE_GROUPING", "session"),
    }
