#!/usr/bin/env bash
# PreToolUse gate for the PostHog MCP `exec` tool.
#
# The PostHog MCP exposes a single `exec` tool that dispatches subcommands like
# `tools | search | info | schema | call <tool_name> [json]`. Once the user
# allow-lists `mcp__posthog__exec`, every subsequent `call` (including writes
# like `experiment-update`, `notebooks-destroy`, `cdp-functions-delete`) runs
# without a prompt. This hook re-introduces a prompt for write `call`s by
# returning `permissionDecision: "ask"`.
#
# Read-only PostHog tools and non-`call` exec verbs are left alone — the hook
# exits 0 so normal permission flow applies.
#
# Users can opt specific write tools out of the prompt via
# `POSTHOG_MCP_EXEC_GATE_ALLOW` — a comma-separated list of bash glob patterns
# matched against the PostHog tool name. Example:
#
#     export POSTHOG_MCP_EXEC_GATE_ALLOW="llma-skill-*,annotation-create"
#
# Pure bash; no jq or other third-party tools required. Write-verb matching and
# payload parsing live in hooks/lib-exec-gate.sh, shared with the Codex gate.

set -u

# Codex compatibility: Codex's PreToolUse protocol does not support
# `permissionDecision: "ask"` (it is parsed then rejected as unsupported), and
# Codex gates `exec` writes through its own PermissionRequest hook
# (hooks/codex-gate-exec-write.sh). Detect Codex via its native PLUGIN_ROOT env
# var — Claude Code only ever sets CLAUDE_PLUGIN_ROOT, never PLUGIN_ROOT — and
# skip this gate so the hook neither errors nor fights Codex's prompt.
# See https://developers.openai.com/codex/hooks
if [[ -n "${PLUGIN_ROOT:-}" ]]; then
    exit 0
fi

# shellcheck source=hooks/lib-exec-gate.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib-exec-gate.sh"

input="$(cat)"

# Match any MCP tool whose name ends in `__exec` regardless of plugin/server
# namespacing (bare `mcp__posthog__exec` or plugin-prefixed variants like
# `mcp__posthog_posthog__exec`).
tool_name="$(posthog_extract_tool_name "$input")"
[[ "$tool_name" =~ __exec$ ]] || exit 0

# Only write `call`s are gated; reads and non-`call` verbs fall through.
posthog_tool="$(posthog_extract_call_tool "$input")"
[[ -n "$posthog_tool" ]] || exit 0

if posthog_is_write "$posthog_tool"; then
    # User-controlled allowlist — skip the prompt for matching tools.
    posthog_is_allowlisted "$posthog_tool" && exit 0

    # `posthog_tool` is restricted to [a-zA-Z0-9_-]+ by the parser, so
    # interpolating it into the JSON response is safe — no characters that
    # would need escaping for JSON or printf.
    printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"`%s` modifies PostHog data — approve to run."}}' "$posthog_tool"
fi

exit 0
