"""Configuration loading from env vars and optional config file."""

import os

from posthog_llma.sender import DEFAULT_HOST


def load_config() -> dict:
    """Load configuration from env vars and optional config file.

    Env vars always take precedence. The config file at
    ~/.claude/posthog-llma.local.md is used as a fallback.
    """
    config = {
        "api_key": os.environ.get("POSTHOG_API_KEY", ""),
        "host": os.environ.get("POSTHOG_HOST", DEFAULT_HOST),
        "privacy_mode": os.environ.get("POSTHOG_LLMA_PRIVACY_MODE", "false").lower() == "true",
        "enabled": os.environ.get("POSTHOG_LLMA_CC_ENABLED", "false").lower() == "true",
        "distinct_id": os.environ.get("POSTHOG_LLMA_DISTINCT_ID", ""),
        "max_attribute_length": int(os.environ.get("POSTHOG_LLMA_MAX_ATTRIBUTE_LENGTH", "12000")),
        "trace_grouping": os.environ.get("POSTHOG_LLMA_TRACE_GROUPING", "session"),
    }

    # Try config file as fallback for missing values
    config_path = os.path.expanduser("~/.claude/posthog-llma.local.md")
    if os.path.isfile(config_path):
        try:
            with open(config_path) as f:
                content = f.read()
            # Parse YAML-like frontmatter
            if content.startswith("---"):
                end = content.find("---", 3)
                if end > 0:
                    for line in content[3:end].strip().splitlines():
                        if ":" in line:
                            key, val = line.split(":", 1)
                            key = key.strip()
                            val = val.strip().strip('"').strip("'")
                            if key == "api_key" and not config["api_key"]:
                                config["api_key"] = val
                            elif key == "host" and config["host"] == DEFAULT_HOST:
                                config["host"] = val
                            elif key == "distinct_id" and not config["distinct_id"]:
                                config["distinct_id"] = val
                            elif key == "privacy_mode" and val.lower() == "true":
                                config["privacy_mode"] = True
        except OSError:
            pass

    return config
