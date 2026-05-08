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
# JSON parsing and command tokenization are delegated to python3 (already
# required by the SessionEnd hook). Earlier versions parsed the raw payload
# with bash regexes and were trivially bypassable: leading whitespace, a
# leading newline, JSON-escaped quotes around the tool name, an upper-case
# `CALL`, or any future write verb not listed below all silently failed
# open. python3's json.loads + shlex.split close those gaps.

set -u

input="$(cat)"

# Parse: emit four lines — tool_name, verb, posthog_tool, parse_failed.
# parse_failed=1 when shlex couldn't tokenize a non-empty command, so we
# default-deny rather than silently allow whatever the server might run.
parsed=$(
    PARSE_INPUT="$input" python3 - <<'PY'
import json
import os
import re
import shlex
import sys

raw = os.environ.get("PARSE_INPUT", "")
try:
    data = json.loads(raw)
except Exception:
    sys.exit(0)

if not isinstance(data, dict):
    sys.exit(0)

tool_name = (data.get("tool_name") or "").strip()
ti = data.get("tool_input") if isinstance(data.get("tool_input"), dict) else {}
command = (ti.get("command") or "").strip() if isinstance(ti, dict) else ""

parse_failed = "0"
verb = ""
ph_tool = ""

if command:
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        tokens = None
    if tokens is None:
        parse_failed = "1"
    elif tokens:
        verb = tokens[0].lower()
        if verb == "call":
            args = tokens[1:]
            if args and args[0] == "--json":
                args = args[1:]
            if args:
                candidate = args[0]
                # Restrict to kebab-case alphanumerics. Anything else is
                # treated as no tool name; the caller will default-deny
                # for `call` invocations.
                if re.fullmatch(r"[A-Za-z0-9_-]+", candidate):
                    ph_tool = candidate

print(tool_name)
print(verb)
print(ph_tool)
print(parse_failed)
PY
)

# python3 missing or errored — exit silently to match prior behaviour.
[[ -n "$parsed" ]] || exit 0

# Read four lines portably (no `mapfile` — macOS still ships bash 3.2).
tool_name=""; verb=""; posthog_tool=""; parse_failed="0"
{
    IFS= read -r tool_name || true
    IFS= read -r verb || true
    IFS= read -r posthog_tool || true
    IFS= read -r parse_failed || true
} <<< "$parsed"
parse_failed="${parse_failed:-0}"

# Match any MCP tool whose name ends in `__exec` regardless of plugin/server
# namespacing (bare `mcp__posthog__exec` or plugin-prefixed variants like
# `mcp__posthog_posthog__exec`).
[[ "$tool_name" =~ __exec$ ]] || exit 0

# Default-deny on unparseable exec commands: better to over-prompt than to
# silently let an oddly-shaped command through to the MCP server.
if [[ "$parse_failed" == "1" ]]; then
    printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"unable to parse PostHog `exec` command — approve to run."}}'
    exit 0
fi

# Only `call` invocations route to PostHog tools; other verbs (tools, search,
# info, schema) are read-only and unaffected.
[[ "$verb" == "call" ]] || exit 0

# `call` with no recognizable tool name: default-deny.
if [[ -z "$posthog_tool" ]]; then
    printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"unable to parse PostHog tool name — approve to run."}}'
    exit 0
fi

# Match write-verb fragments as whole hyphen-separated words within the tool
# name. Keep this list in sync with the PostHog MCP write surface; new
# destructive verbs default to silent until added here, so additions to the
# server tool set must be mirrored.
write_re='(^|-)(archive|cancel|clear|create|delete|destroy|disable|duplicate|enable|end|expire|flush|grant|invocations|kill|launch|materialize|merge|move|partial-update|pause|purge|rearrange|reload|rename|reorder|reset|restore|resume|resync|retry|revoke|set|ship|terminate|truncate|unarchive|unmaterialize|update|void)(-|$)'

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

    # `posthog_tool` is restricted to [a-zA-Z0-9_-]+ by the parser above, so
    # interpolating it into the JSON response is safe — no characters that
    # would need escaping for JSON or printf.
    printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"`%s` modifies PostHog data — approve to run."}}' "$posthog_tool"
fi

exit 0
