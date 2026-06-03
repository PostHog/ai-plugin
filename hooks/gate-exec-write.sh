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
# Pure bash; no jq or other third-party tools required. Relies on the fact
# that PostHog tool names are kebab-case alphanumerics, so a narrow regex on
# the raw JSON payload is safe.

set -u

# Codex compatibility: Codex's PreToolUse protocol does not support
# `permissionDecision: "ask"` (it is parsed then rejected as unsupported), and
# Codex already gates tool calls through its own approval flow. Detect Codex via
# its native PLUGIN_ROOT env var — Claude Code only ever sets CLAUDE_PLUGIN_ROOT,
# never PLUGIN_ROOT — and skip the gate so the hook neither errors nor fights
# Codex's prompt. See https://developers.openai.com/codex/hooks
if [[ -n "${PLUGIN_ROOT:-}" ]]; then
    exit 0
fi

input="$(cat)"

# Extract `tool_name` — simple identifier, no escaping inside the value.
tool_name=""
if [[ "$input" =~ \"tool_name\"[[:space:]]*:[[:space:]]*\"([^\"]+)\" ]]; then
    tool_name="${BASH_REMATCH[1]}"
fi

# Match any MCP tool whose name ends in `__exec` regardless of plugin/server
# namespacing (bare `mcp__posthog__exec` or plugin-prefixed variants like
# `mcp__posthog_posthog__exec`).
[[ "$tool_name" =~ __exec$ ]] || exit 0

# Extract the PostHog tool name from `"command":"call [--json] <tool>..."`.
# Tool names are kebab-case [a-zA-Z0-9_-]+ so the regex stops cleanly at the
# first space or escaped quote without needing to parse the trailing JSON.
posthog_tool=""
if [[ "$input" =~ \"command\"[[:space:]]*:[[:space:]]*\"call[[:space:]]+(--json[[:space:]]+)?([a-zA-Z0-9_-]+) ]]; then
    posthog_tool="${BASH_REMATCH[2]}"
fi
[[ -n "$posthog_tool" ]] || exit 0

# Match write-verb fragments as whole hyphen-separated words within the tool
# name. Keep this list in sync with the PostHog MCP write surface.
write_re='(^|-)(archive|cancel|create|delete|destroy|disable|duplicate|enable|end|invocations|launch|materialize|merge|move|partial-update|pause|rearrange|reload|rename|reorder|reset|restore|resume|resync|retry|set|ship|unarchive|unmaterialize|update)(-|$)'

shopt -s nocasematch
if [[ "$posthog_tool" =~ $write_re ]]; then
    # User-controlled allowlist — skip the prompt for tools matching any glob
    # in POSTHOG_MCP_EXEC_GATE_ALLOW. Patterns use bash glob syntax (`*`, `?`).
    if [[ -n "${POSTHOG_MCP_EXEC_GATE_ALLOW:-}" ]]; then
        IFS=',' read -ra _allow_patterns <<< "$POSTHOG_MCP_EXEC_GATE_ALLOW"
        for _pat in "${_allow_patterns[@]}"; do
            _pat="${_pat#"${_pat%%[![:space:]]*}"}"
            _pat="${_pat%"${_pat##*[![:space:]]}"}"
            [[ -n "$_pat" && "$posthog_tool" == $_pat ]] && exit 0
        done
    fi

    # `posthog_tool` is restricted to [a-zA-Z0-9_-]+ by the regex above, so
    # interpolating it into the JSON response is safe — no characters that
    # would need escaping for JSON or printf.
    printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"`%s` modifies PostHog data — approve to run."}}' "$posthog_tool"
fi

exit 0
