---
description: Set up PostHog LLM Analytics to capture Claude Code sessions
argument-hint: [api-key]
allowed-tools: Bash(echo:*),Bash(cat:*),Bash(mkdir:*)
---

# LLM Analytics — Claude Code Setup

Help the user configure PostHog LLM Analytics for Claude Code session capture.

## What this does

When enabled, every Claude Code session is automatically sent to PostHog's LLM Analytics as `$ai_generation`, `$ai_span`, and `$ai_trace` events — giving visibility into model usage, token consumption, tool calls, and costs.

## Configuration

The user needs to set these environment variables (in their shell profile or Claude Code settings):

### Required

- `POSTHOG_LLMA_CC_ENABLED` — Set to `true` to enable (must be explicitly opted in)
- `POSTHOG_API_KEY` — PostHog project API key (starts with `phc_`)

### Optional

- `POSTHOG_HOST` — PostHog instance URL (default: `https://us.i.posthog.com`, use `https://eu.i.posthog.com` for EU)
- `POSTHOG_LLMA_PRIVACY_MODE` — Set to `true` to redact prompt/output content (tokens and costs still captured)
- `POSTHOG_LLMA_DISTINCT_ID` — Override the distinct_id (default: git user email)

## Steps

1. Check if `POSTHOG_API_KEY` is already set in the environment
2. If the user provided an API key as an argument (`$ARGUMENTS`), guide them to set it
3. Help them choose US or EU hosting
4. Suggest adding to their shell profile or `~/.claude/settings.json` env block
5. Explain that analytics will start flowing on the next session end

## Example shell profile setup

```bash
export POSTHOG_LLMA_CC_ENABLED=true
export POSTHOG_API_KEY="phc_..."
export POSTHOG_HOST="https://eu.i.posthog.com"  # for EU, omit for US
```

## Example Claude Code settings.json setup

```json
{
  "env": {
    "POSTHOG_LLMA_CC_ENABLED": "true",
    "POSTHOG_API_KEY": "phc_...",
    "POSTHOG_HOST": "https://eu.i.posthog.com"
  }
}
```

Check current status:

```bash
echo "POSTHOG_LLMA_CC_ENABLED=${POSTHOG_LLMA_CC_ENABLED:-(not set, defaults to false)}"
echo "POSTHOG_API_KEY=${POSTHOG_API_KEY:-(not set)}"
echo "POSTHOG_HOST=${POSTHOG_HOST:-(not set, defaults to US)}"
echo "POSTHOG_LLMA_PRIVACY_MODE=${POSTHOG_LLMA_PRIVACY_MODE:-(not set, defaults to false)}"
```
