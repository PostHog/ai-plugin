#!/usr/bin/env bash
# PermissionRequest gate for the PostHog MCP `exec` tool on Codex.
#
# Codex runs the posthog MCP server in `prompt` approval mode (see
# `default_tools_approval_mode` in .mcp.json), so by default EVERY `exec` call
# reaches an approval prompt. This hook narrows that to write `call`s only,
# mirroring the Claude Code gate (hooks/gate-exec-write.sh):
#
#   - read / meta verbs (tools, search, info, schema), read `call`s, and
#     allow-listed writes  -> return `allow` (suppresses the prompt)
#   - write `call`s                                  -> no decision (defer), so
#     Codex's prompt fires
#   - unparseable `call`s                            -> no decision (defer), to
#     fail safe toward asking
#
# Unlike the Claude gate, reads must be explicitly allowed: under `prompt` mode
# a no-decision return would itself surface a prompt. The decision verbs are
# `allow` / `deny` only — there is no `ask`; "ask" is the absence of a decision
# combined with prompt mode. See https://developers.openai.com/codex/hooks
#
# Users can opt specific write tools out of the prompt via
# `POSTHOG_MCP_EXEC_GATE_ALLOW` (same syntax as the Claude gate).
#
# Pure bash; no jq. Output is kept to `hookEventName` + `decision.behavior`
# only: Codex denies unknown fields and fails closed on the reserved
# `updatedInput`/`updatedPermissions`/`interrupt` fields.

set -u

# shellcheck source=hooks/lib-exec-gate.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib-exec-gate.sh"

# Return an `allow` decision and stop (prompt suppressed).
allow() {
    printf '{"hookSpecificOutput":{"hookEventName":"PermissionRequest","decision":{"behavior":"allow"}}}'
    exit 0
}

# Emit no decision and stop — defer to Codex's normal approval flow. Under
# prompt mode this means the user is asked.
defer() {
    exit 0
}

input="$(cat)"

# Only gate the umbrella exec tool; if the matcher ever feeds us anything else,
# don't interfere.
tool_name="$(posthog_extract_tool_name "$input")"
[[ "$tool_name" =~ __exec$ ]] || allow

# Non-`call` verbs (tools/search/info/schema) are read-only metadata.
verb="$(posthog_extract_verb "$input")"
[[ "$verb" == "call" ]] || allow

# It is a `call`: a write defers to the prompt (unless allow-listed); a read
# `call` is allowed; an unparseable tool name fails safe to the prompt.
posthog_tool="$(posthog_extract_call_tool "$input")"
[[ -n "$posthog_tool" ]] || defer

if posthog_is_write "$posthog_tool"; then
    posthog_is_allowlisted "$posthog_tool" && allow
    defer
fi

allow
