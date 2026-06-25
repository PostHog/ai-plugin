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
# By default the prompt fires only for a curated "sensitive" subset of write
# tools — feature-flag writes and any delete/destroy — rather than every write.
# Three env vars tune this (all matched against the PostHog tool name):
#
#   POSTHOG_MCP_EXEC_GATE_DISABLE  — set to a non-empty value (e.g. `1`) to turn
#       the gate off entirely. Useful for remote devboxes and Claude Cloud runs
#       where the prompt can't be answered. Example:
#
#           export POSTHOG_MCP_EXEC_GATE_DISABLE=1
#
#   POSTHOG_MCP_EXEC_GATE_DENY     — comma-separated bash globs selecting which
#       write tools prompt. Overrides the built-in default set. Use `*` to
#       prompt on every write (the previous behaviour). Example:
#
#           export POSTHOG_MCP_EXEC_GATE_DENY="*feature-flag*,*-delete"
#
#   POSTHOG_MCP_EXEC_GATE_ALLOW    — comma-separated bash globs that opt specific
#       write tools out of the prompt. Applied on top of the deny set (allow
#       wins). Example:
#
#           export POSTHOG_MCP_EXEC_GATE_ALLOW="llma-skill-*,annotation-create"
#
# Pure bash; no jq or other third-party tools required. Relies on the fact
# that PostHog tool names are kebab-case alphanumerics, so a narrow regex on
# the raw JSON payload is safe.

# Fail open — this gate must never break a Claude Code tool call.
#
# The "ask" decision is delivered entirely through the stdout JSON below; the
# exit code is never used to signal it. So we force every exit path to 0 via an
# EXIT trap. Any unexpected runtime failure — an unbound variable under `set -u`,
# a failed builtin, an unusually old bash — then falls through to normal
# permission flow instead of surfacing as a hook error. Crucially, it can never
# exit 2, which Claude Code interprets as a hard *block* of the tool call.
#
# The one failure a trap can't catch is a parse-time syntax error (the trap
# isn't installed yet); `tests/test_gate_exec_write.sh` guards that with `bash -n`.
trap 'exit 0' EXIT

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

# Full opt-out — turn the gate off entirely. Set to any non-empty value other
# than `0`. Lets remote devboxes and Claude Cloud runs, where no one can answer
# the prompt, run write `call`s without interruption.
if [[ -n "${POSTHOG_MCP_EXEC_GATE_DISABLE:-}" && "${POSTHOG_MCP_EXEC_GATE_DISABLE}" != "0" ]]; then
    exit 0
fi

# Default set of write tools that prompt. Comma-separated bash globs, grounded in
# the live PostHog MCP tool registry. Covers the genuinely sensitive surface:
#
#   *feature-flag*  — feature-flag rollout writes: create-feature-flag,
#                     update-feature-flag, delete-feature-flag,
#                     feature-flags-bulk-{delete,update-tags}-create,
#                     feature-flags-copy-flags-create
#   *delete*        — any deletion: insight-delete, dashboard-delete,
#                     cdp-functions-delete, persons-bulk-delete,
#                     external-data-schemas-delete-data, session-recording-delete, …
#   *destroy*       — any destroy: notebooks-destroy, accounts-destroy,
#                     experiment-saved-metrics-destroy, agent-applications-destroy, …
#   experiment-launch / experiment-ship-variant / experiment-reset
#                   — start exposing users / roll a variant to everyone / wipe results
#   survey-launch   — start showing a survey to real users
#   workflows-enable — activate a user-facing automation
#
# Deliberately silent by default (lower blast radius / easily reverted): routine
# create & update (insight, dashboard, annotation, cohort, alert, skill, …),
# experiment-pause/resume/end, survey-stop, persons-property-set,
# error-tracking-issues-merge/split. Add any of these via
# POSTHOG_MCP_EXEC_GATE_DENY, which overrides this set wholesale; use
# POSTHOG_MCP_EXEC_GATE_DENY="*" to restore prompting on every write.
DEFAULT_DENY='*feature-flag*,*delete*,*destroy*,experiment-launch,experiment-ship-variant,experiment-reset,survey-launch,workflows-enable'

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

# Match comma-separated bash globs in $2 against the PostHog tool name ($1).
# Whitespace around each pattern is trimmed; empty patterns are skipped.
# Returns 0 on the first match, 1 if none match.
matches_any_glob() {
    local tool="$1" patterns="$2" _pat
    local -a _list
    IFS=',' read -ra _list <<< "$patterns"
    for _pat in "${_list[@]}"; do
        _pat="${_pat#"${_pat%%[![:space:]]*}"}"
        _pat="${_pat%"${_pat##*[![:space:]]}"}"
        [[ -n "$_pat" && "$tool" == $_pat ]] && return 0
    done
    return 1
}

shopt -s nocasematch
if [[ "$posthog_tool" =~ $write_re ]]; then
    # Allowlist wins — skip the prompt for tools matching any glob in
    # POSTHOG_MCP_EXEC_GATE_ALLOW. Patterns use bash glob syntax (`*`, `?`).
    if [[ -n "${POSTHOG_MCP_EXEC_GATE_ALLOW:-}" ]]; then
        matches_any_glob "$posthog_tool" "$POSTHOG_MCP_EXEC_GATE_ALLOW" && exit 0
    fi

    # Denylist selects which writes actually prompt. POSTHOG_MCP_EXEC_GATE_DENY
    # overrides the built-in default set; an empty/unset value falls back to it.
    deny_patterns="${POSTHOG_MCP_EXEC_GATE_DENY:-}"
    [[ -n "$deny_patterns" ]] || deny_patterns="$DEFAULT_DENY"
    matches_any_glob "$posthog_tool" "$deny_patterns" || exit 0

    # `posthog_tool` is restricted to [a-zA-Z0-9_-]+ by the regex above, so
    # interpolating it into the JSON response is safe — no characters that
    # would need escaping for JSON or printf.
    printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"`%s` modifies PostHog data — approve to run."}}' "$posthog_tool"
fi

exit 0
