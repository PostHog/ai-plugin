#!/usr/bin/env bash
# Tests for hooks/codex-gate-exec-write.sh, the Codex PermissionRequest hook.
#
# Plain bash, no dependencies. Run from anywhere:
#
#     ./tests/test_codex_gate_exec_write.sh
#
# Each case feeds a PermissionRequest payload (the shape Codex passes on stdin)
# to the hook with PLUGIN_ROOT and CLAUDE_PLUGIN_ROOT set, as Codex sets them.
# "allow"  = the allow decision on stdout + exit 0 (Codex skips its prompt);
# "prompt" = empty stdout + exit 0 (no verdict, so Codex prompts).

set -u

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HOOKS="$HERE/../hooks"
ALLOW='{"hookSpecificOutput":{"hookEventName":"PermissionRequest","decision":{"behavior":"allow"}}}'

# Run copies of the hooks beside a fixture read list, so the cases don't depend
# on what the daily sync generates.
fixture_dir="$(mktemp -d)"
broken="$(mktemp -d)"
trap 'rm -rf "$fixture_dir" "$broken"' EXIT
cp "$HOOKS/codex-gate-exec-write.sh" "$HOOKS/gate-exec-write.sh" "$fixture_dir/"
cat > "$fixture_dir/read-tools.txt" <<'LIST'
# fixture
experiment-get
insight-get
insights-list
persons-list
LIST

pass=0
fail=0

# Args: case name, expected ("allow" or "prompt"), stdin payload, then optional
# KEY=VALUE env overrides. HOOK_DIR overrides the directory the hook runs from.
run_case() {
    local name="$1" expected="$2" payload="$3"
    shift 3
    local out status
    out="$(env -i PATH="$PATH" PLUGIN_ROOT="$HOOKS/.." CLAUDE_PLUGIN_ROOT="$HOOKS/.." "$@" \
        bash "${HOOK_DIR:-$fixture_dir}/codex-gate-exec-write.sh" <<<"$payload")"
    status=$?

    local want=""
    [[ "$expected" == "allow" ]] && want="$ALLOW"
    if [[ $status -eq 0 && "$out" == "$want" ]]; then
        pass=$((pass + 1))
        printf "  ok   %s\n" "$name"
    else
        fail=$((fail + 1))
        printf "  FAIL %s\n       expected=%s status=%d stdout=%q\n" "$name" "$expected" "$status" "$out"
    fi
}

# Payload for an exec command. The command is spliced into JSON verbatim, so
# pass JSON escapes (\n, \") as they would appear on the wire.
exec_payload() {
    printf '{"session_id":"s","turn_id":"t","transcript_path":null,"cwd":"/tmp","hook_event_name":"PermissionRequest","model":"m","permission_mode":"default","tool_name":"mcp__posthog__exec","tool_input":{"command":"%s"}}' "$1"
}

echo "Running codex-gate-exec-write.sh tests..."

# --- known reads run without a prompt ---

run_case "tools verb is allowed" allow "$(exec_payload 'tools')"
run_case "help verb is allowed" allow "$(exec_payload 'help call')"
run_case "learn verb is allowed" allow "$(exec_payload 'learn flags')"
run_case "search verb is allowed" allow "$(exec_payload 'search feature flag')"
run_case "info verb is allowed" allow "$(exec_payload 'info x')"
run_case "info verb naming a write tool is allowed" allow "$(exec_payload 'info --json delete-feature-flag')"
run_case "schema verb is allowed" allow "$(exec_payload 'schema insight-create query')"
run_case "listed read call is allowed" allow "$(exec_payload 'call persons-list {}')"
run_case "listed read call with a body is allowed" allow "$(exec_payload 'call experiment-get {\"id\":1}')"
run_case "listed read call with --json is allowed" allow "$(exec_payload 'call --json insights-list {}')"
run_case "--confirm before a listed read is allowed" allow "$(exec_payload 'call --confirm experiment-get {}')"

# --- every other call prompts, whatever its name ---

run_case "sensitive write prompts" prompt "$(exec_payload 'call delete-feature-flag {\"id\":1}')"
run_case "sensitive write with --json prompts" prompt "$(exec_payload 'call --json notebooks-destroy {}')"
run_case "--confirm before a sensitive write prompts" prompt "$(exec_payload 'call --confirm delete-feature-flag {}')"
run_case "write outside the default deny set prompts (experiment-update)" prompt "$(exec_payload 'call experiment-update {}')"
run_case "feature-flag write with no write verb prompts" prompt "$(exec_payload 'call feature-flag-roll-out-to-everyone {}')"
run_case "workflows-publish prompts" prompt "$(exec_payload 'call workflows-publish {}')"
run_case "cdp-functions-create prompts" prompt "$(exec_payload 'call cdp-functions-create {}')"
run_case "posthog-connection-call prompts" prompt \
    "$(exec_payload 'call posthog-connection-call {\"connection_id\":\"c\",\"tool_name\":\"delete-feature-flag\",\"arguments\":{\"id\":1}}')"
run_case "switch-project prompts" prompt "$(exec_payload 'call switch-project {\"project_id\":2}')"
run_case "gateway tool prompts" prompt "$(exec_payload 'call linear__list_issues {}')"

# --- commands the gate cannot classify prompt ---

run_case "leading space before a write prompts" prompt "$(exec_payload '  call delete-feature-flag {}')"
run_case "leading escaped newline before a write prompts" prompt "$(exec_payload '\ncall delete-feature-flag {}')"
run_case "read verb followed by a newline prompts" prompt "$(exec_payload 'tools\ncall delete-feature-flag {}')"
run_case "unknown verb prompts" prompt "$(exec_payload 'frobnicate delete-feature-flag')"
run_case "empty command prompts" prompt "$(exec_payload '')"
run_case "missing command prompts" prompt \
    '{"hook_event_name":"PermissionRequest","tool_name":"mcp__posthog__exec","tool_input":{}}'
run_case "decoy read call ahead of the real write prompts" prompt \
    '{"hook_event_name":"PermissionRequest","tool_name":"mcp__posthog__exec","tool_input":{"a":{"command":"call insight-get"},"command":"call delete-feature-flag {}"}}'
run_case "malformed payload prompts" prompt 'not json at all {{{'
run_case "empty payload prompts" prompt ''

# --- the POSTHOG_MCP_EXEC_GATE_* variables never approve a write ---

run_case "ALLOW match does not approve a write" prompt "$(exec_payload 'call delete-feature-flag {}')" \
    POSTHOG_MCP_EXEC_GATE_ALLOW="annotation-*,delete-feature-flag"
run_case 'ALLOW="*" does not approve a write' prompt "$(exec_payload 'call experiment-update {}')" \
    POSTHOG_MCP_EXEC_GATE_ALLOW="*"
run_case "DENY narrowed away from a write does not approve it" prompt "$(exec_payload 'call notebooks-destroy {}')" \
    POSTHOG_MCP_EXEC_GATE_DENY="*feature-flag*"
run_case "DISABLE=1 does not approve a write" prompt "$(exec_payload 'call delete-feature-flag {}')" \
    POSTHOG_MCP_EXEC_GATE_DISABLE="1"
run_case "DISABLE=1 still allows a read" allow "$(exec_payload 'call persons-list {}')" \
    POSTHOG_MCP_EXEC_GATE_DISABLE="1"

# --- a broken install prompts instead of allowing ---

cp "$HOOKS/codex-gate-exec-write.sh" "$HOOKS/gate-exec-write.sh" "$broken/"
HOOK_DIR="$broken" run_case "missing read list prompts on a read call" prompt "$(exec_payload 'call persons-list {}')"

rm "$broken/gate-exec-write.sh"
HOOK_DIR="$broken" run_case "missing shared gate prompts on a read" prompt "$(exec_payload 'tools')"

printf '#!/usr/bin/env bash\nexit 1\n' >"$broken/gate-exec-write.sh"
chmod +x "$broken/gate-exec-write.sh"
HOOK_DIR="$broken" run_case "failing shared gate prompts on a read" prompt "$(exec_payload 'tools')"

# Codex treats exit 2 with stderr as a deny, so only a syntax error could turn
# the gate into a blanket block; `bash -n` guards that.
for _script in codex-gate-exec-write.sh gate-exec-write.sh; do
    if bash -n "$HOOKS/$_script" 2>/dev/null; then
        pass=$((pass + 1)); printf "  ok   %s passes 'bash -n'\n" "$_script"
    else
        fail=$((fail + 1)); printf "  FAIL %s has a syntax error ('bash -n')\n" "$_script"
    fi
done

echo
echo "Passed: $pass  Failed: $fail"
(( fail == 0 ))
