#!/usr/bin/env bash
# PermissionRequest gate for the PostHog MCP `exec` tool on Codex.
#
# Codex hooks cannot return "ask", so the plugin sets the posthog MCP server's
# `default_tools_approval_mode` to `prompt` (codex-mcp.json): every `exec` call
# reaches Codex's approval flow, and this hook runs first. It allows the calls
# the Claude Code gate (gate-exec-write.sh) passes and returns no verdict for the
# rest, so Codex prompts. Classification and the POSTHOG_MCP_EXEC_GATE_*
# variables therefore behave exactly as they do on Claude Code.
#
# Anything other than a clean pass from the shared gate — an ask, an
# unclassifiable command, a missing script, a crash — leaves Codex's prompt in
# place: this hook exits 0 without a verdict. Codex reads exit 2 with stderr as
# a deny, so the shared gate's stderr is discarded.

input="$(cat)"
gate="$(dirname -- "${BASH_SOURCE[0]}")/gate-exec-write.sh"

verdict="$("$gate" --fail-closed <<<"$input" 2>/dev/null)" || exit 0
[[ -z "$verdict" ]] || exit 0

printf '{"hookSpecificOutput":{"hookEventName":"PermissionRequest","decision":{"behavior":"allow"}}}'
