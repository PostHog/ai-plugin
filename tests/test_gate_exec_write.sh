#!/usr/bin/env bash
# Tests for hooks/gate-exec-write.sh.
#
# Plain bash, no dependencies. Run from anywhere:
#
#     ./tests/test_gate_exec_write.sh
#
# Each case feeds a JSON payload (the same shape Claude Code passes on stdin)
# to the hook with a controlled environment, then asserts on stdout and exit
# status. "silent" = empty stdout + exit 0 (normal permission flow);
# "prompt"  = JSON `permissionDecision: ask` payload + exit 0.

set -u

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$HERE/../hooks/gate-exec-write.sh"

pass=0
fail=0

# Run hook with given input + env and capture stdout. Args:
#   $1: case name
#   $2: stdin payload
#   $3: expected mode — "silent" or "prompt"
#   $4: when "prompt", the posthog tool name expected in the response
#   $5+: optional `KEY=VALUE` env overrides for this run
run_case() {
    local name="$1" payload="$2" expected="$3" expected_tool="${4:-}"
    # Drop the fixed slots; whatever remains are KEY=VALUE env overrides.
    if (( $# >= 4 )); then shift 4; else shift $#; fi
    local out status
    out="$(env -i PATH="$PATH" "$@" bash "$HOOK" <<<"$payload")"
    status=$?

    local ok=1
    if [[ "$expected" == "silent" ]]; then
        [[ -z "$out" && $status -eq 0 ]] || ok=0
    else
        # Match the actual JSON shape the hook produces. When expected_tool
        # is non-empty we also assert the message names that tool; an empty
        # expected_tool just asserts an "ask" decision (used for default-deny
        # paths where the message is generic).
        local needle="\"permissionDecision\":\"ask\""
        if [[ $status -eq 0 && "$out" == *"$needle"* ]]; then
            if [[ -n "$expected_tool" ]]; then
                local tool_needle="\`${expected_tool}\` modifies PostHog data"
                [[ "$out" == *"$tool_needle"* ]] || ok=0
            fi
        else
            ok=0
        fi
    fi

    if (( ok )); then
        pass=$((pass + 1))
        printf "  ok   %s\n" "$name"
    else
        fail=$((fail + 1))
        printf "  FAIL %s\n       expected=%s status=%d stdout=%q\n" \
            "$name" "$expected" "$status" "$out"
    fi
}

# Helper: payload for an exec `call <tool>` invocation with default tool name.
exec_call() {
    local tool="$1" exec_name="${2:-mcp__posthog__exec}"
    printf '{"tool_name":"%s","tool_input":{"command":"call %s {}"}}' "$exec_name" "$tool"
}

echo "Running gate-exec-write.sh tests..."

# --- pass-through cases (no prompt regardless of allowlist) ---

run_case "non-exec tool is ignored" \
    '{"tool_name":"Bash","tool_input":{}}' \
    silent

run_case "exec subcommand other than call (tools)" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"tools"}}' \
    silent

run_case "exec subcommand other than call (search foo)" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"search foo"}}' \
    silent

run_case "read-only call (experiment-get) is silent" \
    "$(exec_call experiment-get)" \
    silent

run_case "read-only call (insights-list) is silent" \
    "$(exec_call insights-list)" \
    silent

run_case "read-only call with allowlist set is still silent" \
    "$(exec_call experiment-get)" \
    silent "" \
    POSTHOG_MCP_EXEC_GATE_ALLOW="llma-skill-*"

# --- write cases without allowlist (should prompt) ---

run_case "write call (experiment-update) prompts" \
    "$(exec_call experiment-update)" \
    prompt experiment-update

run_case "write call (notebooks-destroy) prompts" \
    "$(exec_call notebooks-destroy)" \
    prompt notebooks-destroy

run_case "write call (cdp-functions-delete) prompts" \
    "$(exec_call cdp-functions-delete)" \
    prompt cdp-functions-delete

run_case "write call via plugin-prefixed exec name prompts" \
    "$(exec_call llma-skill-update mcp__posthog_posthog__exec)" \
    prompt llma-skill-update

run_case "write call with --json flag still extracts tool" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"call --json experiment-update {\"id\":1}"}}' \
    prompt experiment-update

run_case "empty POSTHOG_MCP_EXEC_GATE_ALLOW behaves as unset" \
    "$(exec_call llma-skill-update)" \
    prompt llma-skill-update \
    POSTHOG_MCP_EXEC_GATE_ALLOW=""

# --- write cases with allowlist (should be silent on match) ---

run_case "allowlist glob matches (llma-skill-*)" \
    "$(exec_call llma-skill-update)" \
    silent "" \
    POSTHOG_MCP_EXEC_GATE_ALLOW="llma-skill-*"

run_case "allowlist glob matches multiple skill writes (file-create)" \
    "$(exec_call llma-skill-file-create)" \
    silent "" \
    POSTHOG_MCP_EXEC_GATE_ALLOW="llma-skill-*"

run_case "allowlist exact match" \
    "$(exec_call annotation-create)" \
    silent "" \
    POSTHOG_MCP_EXEC_GATE_ALLOW="annotation-create"

run_case "allowlist multi-entry with whitespace" \
    "$(exec_call llma-skill-update)" \
    silent "" \
    POSTHOG_MCP_EXEC_GATE_ALLOW=" annotation-create , llma-skill-update "

run_case "allowlist ? glob matches single char" \
    "$(exec_call experiment-end)" \
    silent "" \
    POSTHOG_MCP_EXEC_GATE_ALLOW="experiment-en?"

# --- write cases with non-matching allowlist (should still prompt) ---

run_case "non-matching allowlist still prompts" \
    "$(exec_call llma-skill-update)" \
    prompt llma-skill-update \
    POSTHOG_MCP_EXEC_GATE_ALLOW="annotation-*"

run_case "allowlist does not bypass an unrelated write tool" \
    "$(exec_call experiment-update)" \
    prompt experiment-update \
    POSTHOG_MCP_EXEC_GATE_ALLOW="llma-skill-*,annotation-create"

# --- regex word-boundary cases ---

run_case "tool with no write verb stays silent (persons-list)" \
    "$(exec_call persons-list)" \
    silent

run_case "embedded substring is not a write verb (e.g. updates-feed)" \
    "$(exec_call some-updates-feed)" \
    silent

# --- parser-bypass regression tests ---
# Each input below slipped past the original bash-regex parser. The
# python-backed parser must catch them.

run_case "leading whitespace before 'call' still prompts on writes" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"  call experiment-update {}"}}' \
    prompt experiment-update

run_case "tab between 'call' and tool name still prompts" \
    "$(printf '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"call\\texperiment-update {}"}}')" \
    prompt experiment-update

run_case "leading newline in command still prompts" \
    "$(printf '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"\\ncall experiment-update {}"}}')" \
    prompt experiment-update

run_case "uppercase CALL still prompts on writes" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"CALL experiment-update {}"}}' \
    prompt experiment-update

run_case "JSON-quoted tool name still prompts on writes" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"call \"experiment-update\" {}"}}' \
    prompt experiment-update

# --- newly-classified write verbs (post-audit additions) ---

run_case "write verb 'purge' prompts" \
    "$(exec_call data-purge)" \
    prompt data-purge

run_case "write verb 'revoke' prompts" \
    "$(exec_call api-key-revoke)" \
    prompt api-key-revoke

run_case "write verb 'truncate' prompts" \
    "$(exec_call event-truncate)" \
    prompt event-truncate

run_case "write verb 'terminate' prompts" \
    "$(exec_call session-terminate)" \
    prompt session-terminate

# --- default-deny on unparseable / odd-shaped exec commands ---

run_case "unbalanced quotes in exec command default-deny" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"call experiment-get \"unterminated"}}' \
    prompt ""

run_case "call with no tool name default-denies" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"call"}}' \
    prompt ""

# --- summary ---

echo
echo "Passed: $pass  Failed: $fail"
(( fail == 0 ))
