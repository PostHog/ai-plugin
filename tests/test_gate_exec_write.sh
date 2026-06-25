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
        # Match the actual JSON shape the hook produces, with the tool name
        # interpolated. Any drift in the response template will fail here.
        local needle="\"permissionDecision\":\"ask\""
        local tool_needle="\`${expected_tool}\` modifies PostHog data"
        [[ $status -eq 0 && "$out" == *"$needle"* && "$out" == *"$tool_needle"* ]] || ok=0
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

# --- default deny set: sensitive writes prompt, other writes are silent ---

run_case "default: feature-flag write (create-feature-flag) prompts" \
    "$(exec_call create-feature-flag)" \
    prompt create-feature-flag

run_case "default: feature-flag write (update-feature-flag) prompts" \
    "$(exec_call update-feature-flag)" \
    prompt update-feature-flag

run_case "default: feature-flag bulk write prompts" \
    "$(exec_call feature-flags-bulk-update-tags-create)" \
    prompt feature-flags-bulk-update-tags-create

run_case "default: destroy write (notebooks-destroy) prompts" \
    "$(exec_call notebooks-destroy)" \
    prompt notebooks-destroy

run_case "default: delete write (cdp-functions-delete) prompts" \
    "$(exec_call cdp-functions-delete)" \
    prompt cdp-functions-delete

run_case "default: rollout write (experiment-launch) prompts" \
    "$(exec_call experiment-launch)" \
    prompt experiment-launch

run_case "default: rollout write (experiment-ship-variant) prompts" \
    "$(exec_call experiment-ship-variant)" \
    prompt experiment-ship-variant

run_case "default: rollout write (survey-launch) prompts" \
    "$(exec_call survey-launch)" \
    prompt survey-launch

run_case "default: rollout write (workflows-enable) prompts" \
    "$(exec_call workflows-enable)" \
    prompt workflows-enable

run_case "default: non-sensitive write (experiment-update) is silent" \
    "$(exec_call experiment-update)" \
    silent

run_case "default: reversible lifecycle write (experiment-pause) is silent" \
    "$(exec_call experiment-pause)" \
    silent

run_case "default: routine write (insight-create) is silent" \
    "$(exec_call insight-create)" \
    silent

run_case "default: non-sensitive write (llma-skill-update) is silent" \
    "$(exec_call llma-skill-update)" \
    silent

run_case "default: feature-flag read (feature-flag-get-all) is silent" \
    "$(exec_call feature-flag-get-all)" \
    silent

run_case "default: feature-flag read (feature-flags-status-retrieve) is silent" \
    "$(exec_call feature-flags-status-retrieve)" \
    silent

# --- POSTHOG_MCP_EXEC_GATE_DISABLE turns the gate off entirely ---

run_case "disable=1 silences a sensitive feature-flag write" \
    "$(exec_call delete-feature-flag)" \
    silent "" \
    POSTHOG_MCP_EXEC_GATE_DISABLE="1"

run_case "disable=0 leaves the gate active" \
    "$(exec_call delete-feature-flag)" \
    prompt delete-feature-flag \
    POSTHOG_MCP_EXEC_GATE_DISABLE="0"

# --- POSTHOG_MCP_EXEC_GATE_DENY overrides the default set ---

run_case 'deny="*" restores prompting on every write' \
    "$(exec_call experiment-update)" \
    prompt experiment-update \
    POSTHOG_MCP_EXEC_GATE_DENY="*"

run_case "deny narrowed to feature flags: experiment-update is silent" \
    "$(exec_call experiment-update)" \
    silent "" \
    POSTHOG_MCP_EXEC_GATE_DENY="*feature-flag*"

run_case "deny narrowed to feature flags: create-feature-flag prompts" \
    "$(exec_call create-feature-flag)" \
    prompt create-feature-flag \
    POSTHOG_MCP_EXEC_GATE_DENY="*feature-flag*"

run_case "empty POSTHOG_MCP_EXEC_GATE_DENY falls back to default set" \
    "$(exec_call notebooks-destroy)" \
    prompt notebooks-destroy \
    POSTHOG_MCP_EXEC_GATE_DENY=""

run_case "deny with --json flag still extracts tool" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"call --json delete-feature-flag {\"id\":1}"}}' \
    prompt delete-feature-flag

run_case "sensitive write via plugin-prefixed exec name prompts" \
    "$(exec_call delete-feature-flag mcp__posthog_posthog__exec)" \
    prompt delete-feature-flag

# --- allowlist wins over the deny set (silent on match) ---

run_case "allowlist glob matches (feature-flag-*) over default deny" \
    "$(exec_call create-feature-flag)" \
    silent "" \
    POSTHOG_MCP_EXEC_GATE_ALLOW="create-feature-flag"

run_case "allowlist glob matches (llma-skill-*) under deny=*" \
    "$(exec_call llma-skill-update)" \
    silent "" \
    POSTHOG_MCP_EXEC_GATE_DENY="*" POSTHOG_MCP_EXEC_GATE_ALLOW="llma-skill-*"

run_case "allowlist glob matches multiple skill writes (file-create)" \
    "$(exec_call llma-skill-file-create)" \
    silent "" \
    POSTHOG_MCP_EXEC_GATE_DENY="*" POSTHOG_MCP_EXEC_GATE_ALLOW="llma-skill-*"

run_case "allowlist exact match" \
    "$(exec_call annotation-create)" \
    silent "" \
    POSTHOG_MCP_EXEC_GATE_DENY="*" POSTHOG_MCP_EXEC_GATE_ALLOW="annotation-create"

run_case "allowlist multi-entry with whitespace" \
    "$(exec_call llma-skill-update)" \
    silent "" \
    POSTHOG_MCP_EXEC_GATE_DENY="*" POSTHOG_MCP_EXEC_GATE_ALLOW=" annotation-create , llma-skill-update "

run_case "allowlist ? glob matches single char" \
    "$(exec_call experiment-end)" \
    silent "" \
    POSTHOG_MCP_EXEC_GATE_DENY="*" POSTHOG_MCP_EXEC_GATE_ALLOW="experiment-en?"

# --- non-matching allowlist still prompts ---

run_case "non-matching allowlist still prompts a feature-flag write" \
    "$(exec_call create-feature-flag)" \
    prompt create-feature-flag \
    POSTHOG_MCP_EXEC_GATE_ALLOW="annotation-*"

run_case "empty POSTHOG_MCP_EXEC_GATE_ALLOW behaves as unset" \
    "$(exec_call create-feature-flag)" \
    prompt create-feature-flag \
    POSTHOG_MCP_EXEC_GATE_ALLOW=""

# --- regex word-boundary cases ---

run_case "tool with no write verb stays silent (persons-list)" \
    "$(exec_call persons-list)" \
    silent

run_case "embedded substring is not a write verb (e.g. updates-feed)" \
    "$(exec_call some-updates-feed)" \
    silent

# --- fail-open contract: the hook must never break a tool call ---
#
# The hook signals "ask" only via stdout JSON + exit 0. Every other path must
# also exit 0 so a hook failure can never reach Claude Code as exit 2 — which it
# treats as a hard *block* of the user's tool call.

# The only thing that can make the hook exit 2 is a parse-time syntax error,
# which the runtime EXIT trap cannot catch. Guard it here.
if bash -n "$HOOK" 2>/dev/null; then
    pass=$((pass + 1)); printf "  ok   hook passes 'bash -n' syntax check\n"
else
    fail=$((fail + 1)); printf "  FAIL hook has a syntax error ('bash -n')\n"
fi

# No input, however malformed, may yield exit code 2 (block). Fail open instead.
for _payload in \
    '' \
    'not json at all {{{' \
    '{"tool_name":"mcp__posthog__exec"}' \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"call ' \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"call delete-feature-flag {}"}}'
do
    env -i PATH="$PATH" bash "$HOOK" <<<"$_payload" >/dev/null 2>&1
    if (( $? != 2 )); then
        pass=$((pass + 1)); printf "  ok   never exits 2 (block) for: %q\n" "$_payload"
    else
        fail=$((fail + 1)); printf "  FAIL exited 2 (would block) for: %q\n" "$_payload"
    fi
done

# --- summary ---

echo
echo "Passed: $pass  Failed: $fail"
(( fail == 0 ))
