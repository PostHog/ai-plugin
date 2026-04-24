#!/usr/bin/env bash
# Cursor `beforeMCPExecution` gate for the PostHog MCP `exec` tool.
#
# Mirrors hooks/gate-exec-write.sh (Claude Code) but speaks Cursor's hook I/O
# (https://cursor.com/docs/hooks): input is `{tool_name, tool_input,
# url|command, ...}` on stdin; output is `{permission, user_message,
# agent_message}` on stdout. The PostHog MCP exposes a single `exec` tool
# that dispatches subcommands like `tools | search | info | schema |
# call <tool_name> [json]`. Once Cursor auto-runs `exec`, every subsequent
# `call` (including writes like `experiment-update`, `notebooks-destroy`)
# runs without a prompt. This hook re-introduces a prompt for write `call`s
# by returning `permission: "ask"`.
#
# Read-only PostHog tools and non-`call` exec verbs fall through (no JSON
# emitted, exit 0) so Cursor applies its default permission flow.
#
# Pure bash; no jq or other third-party tools required.

set -u

input="$(cat)"

# Extract `tool_name`. For MCP tools Cursor passes the bare tool name (e.g.
# `exec`), without a server prefix.
tool_name=""
if [[ "$input" =~ \"tool_name\"[[:space:]]*:[[:space:]]*\"([^\"]+)\" ]]; then
    tool_name="${BASH_REMATCH[1]}"
fi
[[ "$tool_name" == "exec" ]] || exit 0

# Extract the PostHog tool name from `"command":"call [--json] <tool>..."`.
# Cursor sends `tool_input` as an inline JSON object, so the literal
# `"command":"call <tool>` substring appears once in the raw payload.
posthog_tool=""
if [[ "$input" =~ \"command\"[[:space:]]*:[[:space:]]*\"call[[:space:]]+(--json[[:space:]]+)?([a-zA-Z0-9_-]+) ]]; then
    posthog_tool="${BASH_REMATCH[2]}"
fi
[[ -n "$posthog_tool" ]] || exit 0

# Match write-verb fragments as whole hyphen-separated words within the tool
# name. Keep this list in sync with hooks/gate-exec-write.sh.
write_re='(^|-)(archive|cancel|create|delete|destroy|disable|duplicate|enable|end|invocations|launch|materialize|merge|move|partial-update|pause|rearrange|reload|rename|reorder|reset|restore|resume|resync|retry|set|ship|unarchive|unmaterialize|update)(-|$)'

shopt -s nocasematch
if [[ "$posthog_tool" =~ $write_re ]]; then
    # `posthog_tool` is restricted to [a-zA-Z0-9_-]+ above, so no JSON
    # escaping needed when interpolating.
    printf '{"permission":"ask","user_message":"`%s` modifies PostHog data — approve to run.","agent_message":"User confirmation required to run PostHog write command `%s`."}' "$posthog_tool" "$posthog_tool"
fi

exit 0
