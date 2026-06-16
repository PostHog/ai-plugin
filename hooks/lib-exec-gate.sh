#!/usr/bin/env bash
# Shared helpers for the PostHog MCP `exec` write-gate hooks.
#
# Sourced (not executed) by both client gates so the write-verb surface and the
# exec-payload parsing live in exactly one place and never drift:
#   - hooks/gate-exec-write.sh        (Claude Code, PreToolUse)
#   - hooks/codex-gate-exec-write.sh  (Codex, PermissionRequest)
#
# Pure bash; no jq or other third-party tools. PostHog tool names are kebab-case
# alphanumerics, so narrow regexes on the raw JSON payload are safe.

# Write-verb fragments matched as whole hyphen-separated words within a PostHog
# tool name. Keep this list in sync with the PostHog MCP write surface.
POSTHOG_WRITE_RE='(^|-)(archive|cancel|create|delete|destroy|disable|duplicate|enable|end|invocations|launch|materialize|merge|move|partial-update|pause|rearrange|reload|rename|reorder|reset|restore|resume|resync|retry|set|ship|unarchive|unmaterialize|update)(-|$)'

# Echo the `tool_name` from a hook JSON payload (empty if absent). The value is
# a simple identifier with no escaping inside it.
posthog_extract_tool_name() {
    local input="$1"
    if [[ "$input" =~ \"tool_name\"[[:space:]]*:[[:space:]]*\"([^\"]+)\" ]]; then
        printf '%s' "${BASH_REMATCH[1]}"
    fi
}

# Echo the leading verb of the exec `command` (e.g. `call`, `tools`, `search`,
# `info`, `schema`); empty if no `command` is present.
posthog_extract_verb() {
    local input="$1"
    if [[ "$input" =~ \"command\"[[:space:]]*:[[:space:]]*\"([a-zA-Z0-9_-]+) ]]; then
        printf '%s' "${BASH_REMATCH[1]}"
    fi
}

# Echo the PostHog tool name from a `"command":"call [--json] <tool> ..."`
# payload; empty if the command is not a `call` or the tool can't be parsed.
# Tool names are [a-zA-Z0-9_-]+ so the regex stops cleanly at the first space.
posthog_extract_call_tool() {
    local input="$1"
    if [[ "$input" =~ \"command\"[[:space:]]*:[[:space:]]*\"call[[:space:]]+(--json[[:space:]]+)?([a-zA-Z0-9_-]+) ]]; then
        printf '%s' "${BASH_REMATCH[2]}"
    fi
}

# Return 0 if the PostHog tool name denotes a write operation. Case-insensitive.
posthog_is_write() {
    local tool="$1" rc restore
    restore="$(shopt -p nocasematch)"
    shopt -s nocasematch
    [[ "$tool" =~ $POSTHOG_WRITE_RE ]]
    rc=$?
    eval "$restore"
    return "$rc"
}

# Return 0 if the tool matches any glob in POSTHOG_MCP_EXEC_GATE_ALLOW — a
# comma-separated list of bash glob patterns (`*`, `?`). Case-insensitive.
posthog_is_allowlisted() {
    local tool="$1" pat rc=1 restore patterns
    [[ -n "${POSTHOG_MCP_EXEC_GATE_ALLOW:-}" ]] || return 1
    restore="$(shopt -p nocasematch)"
    shopt -s nocasematch
    local IFS=','
    read -ra patterns <<< "$POSTHOG_MCP_EXEC_GATE_ALLOW"
    for pat in "${patterns[@]}"; do
        # Trim surrounding whitespace.
        pat="${pat#"${pat%%[![:space:]]*}"}"
        pat="${pat%"${pat##*[![:space:]]}"}"
        if [[ -n "$pat" && "$tool" == $pat ]]; then
            rc=0
            break
        fi
    done
    eval "$restore"
    return "$rc"
}
