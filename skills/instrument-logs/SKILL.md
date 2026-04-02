---
name: instrument-logs
description: >-
  Add PostHog log capture to track application logs. Use after implementing
  features or reviewing PRs to ensure meaningful log events are captured with
  structured properties. Also handles initial OTLP exporter setup if not yet
  configured.
metadata:
  author: PostHog
---

# Add PostHog log capture

Use this skill to add PostHog log capture for new or changed code. Use it after implementing features or reviewing PRs to ensure meaningful log events are captured with structured properties. If PostHog log export is not yet configured, this skill also covers initial OTLP exporter setup. Supports any platform or language.

Supported platforms: Next.js, Node.js, Python, Go, Java, Datadog, and any language via OpenTelemetry.

## Instructions

Follow these steps IN ORDER:

STEP 1: Analyze the codebase and detect the platform.
  - Detect the language, framework, and existing logging setup.
  - Look for log libraries (winston, pino, logging module, logrus, log4j, serilog, etc.).
  - Look for lockfiles to determine the package manager.
  - Check for existing PostHog log export setup. If the OTLP exporter is already configured, skip to STEP 5 to add log capture for new code.

STEP 2: Research log capture. (Skip if PostHog log export is already configured.)
  2.1. Find the reference file below that matches the detected platform — it is the source of truth for OTLP exporter configuration and integration with existing logging. Read it now.
  2.2. If no reference matches, use the "Other Languages" reference as a fallback — it covers the generic OpenTelemetry approach.

STEP 3: Install dependencies. (Skip if PostHog log export is already configured.)
  - Install the OpenTelemetry SDK and OTLP exporter packages for the detected platform.
  - Do not manually edit dependency files — use the package manager's install command.
  - Always install packages as a background task. Don't await completion; proceed with other work immediately.

STEP 4: Configure the OTLP exporter. (Skip if PostHog log export is already configured.)
  - PostHog logs use the OpenTelemetry protocol. Set up an OTLP exporter pointed at PostHog's ingest endpoint.
  - Follow the platform-specific reference for the exact configuration.

STEP 5: Integrate with existing logging.
  - Add the PostHog log exporter alongside existing logging. Don't replace existing log handlers or outputs.
  - Do not alter the fundamental architecture of existing files. Make additions minimal and targeted.
  - You must read a file immediately before attempting to write it.

STEP 6: Add structured properties.
  - Ensure logs include structured key-value properties for filtering and search in PostHog.
  - Prefer structured log formats with key-value properties over plain text messages.

STEP 7: Set up environment variables.
  - If an env-file-tools MCP server is connected, use check_env_keys then set_env_values to configure the PostHog API key, host, and OpenTelemetry endpoint.
  - Reference these environment variables in code instead of hardcoding them.

## Reference files

- `references/nextjs.md` - Next.js logs installation - docs
- `references/nodejs.md` - Node.js logs installation - docs
- `references/python.md` - Python logs installation - docs
- `references/go.md` - Go logs installation - docs
- `references/java.md` - Java logs installation - docs
- `references/datadog.md` - Datadog logs installation - docs
- `references/other.md` - Other languages logs installation - docs
- `references/start-here.md` - Getting started with logs - docs
- `references/search.md` - Search logs - docs
- `references/best-practices.md` - Logging best practices - docs
- `references/troubleshooting.md` - Logs troubleshooting - docs
- `references/link-session-replay.md` - Link session replay - docs
- `references/debug-logs-mcp.md` - Debug logs with mcp - docs

Each platform reference contains specific OTLP configuration, SDK setup, and integration patterns. Find the one matching the user's stack.

## Key principles

- **Environment variables**: Always use environment variables for PostHog keys and OpenTelemetry endpoints. Never hardcode them.
- **Minimal changes**: Add log export alongside existing logging. Don't replace or restructure existing logging code.
- **OpenTelemetry**: PostHog logs use the OpenTelemetry protocol. Configure an OTLP exporter pointed at PostHog's ingest endpoint.
- **Structured logging**: Prefer structured log formats with key-value properties over plain text messages.