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
READ_TOOLS="$HERE/../hooks/read-tools.txt"

# Run a copy of the hook beside a fixture read list, so the cases don't depend
# on what the daily sync generates.
fixture_dir="$(mktemp -d)"
trap 'rm -rf "$fixture_dir"' EXIT
cp "$HERE/../hooks/gate-exec-write.sh" "$fixture_dir/"
HOOK="$fixture_dir/gate-exec-write.sh"
cat > "$fixture_dir/read-tools.txt" <<'LIST'
# fixture
data-catalog-metric-delete-prepare
experiment-get
feature-flag-get-all
feature-flags-status-retrieve
feature-flags-test-evaluation-create
insights-list
persons-list
LIST

pass=0
fail=0

# Run hook with given input + env and capture stdout. Args:
#   $1: case name
#   $2: stdin payload
#   $3: expected mode — "silent" or "prompt"
#   $4: when "prompt", the posthog tool name expected in the response, or ""
#       for a prompt that names no tool
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
        local tool_needle="\`${expected_tool}\`"
        [[ $status -eq 0 && "$out" == *"$needle"* ]] || ok=0
        [[ -z "$expected_tool" || "$out" == *"$tool_needle"* ]] || ok=0
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

# --- permission_mode: only a top-level bypassPermissions skips the gate ---

# Same as exec_call, with a `permission_mode` field before `tool_input`.
exec_call_mode() {
    printf '{"tool_name":"mcp__posthog__exec","permission_mode":"%s","tool_input":{"command":"call %s {}"}}' "$1" "$2"
}

# Writes a payload whose command body is $1 kilobytes of escaped quotes, with top-level
# permission_mode $2 (default: default). The body names bypassPermissions, so the guard
# in top_level_bypass lets the walk run over all of it (or the size cap decides).
escaped_quote_payload() {
    local body mode="${2:-default}"
    # Whole `\"x` pieces (3 bytes each), so the body is valid JSON at any size.
    body="$(yes '\"x' | head -n $(( $1 * 1000 / 3 )) | tr -d '\n')"
    printf '%s' '{"tool_name":"mcp__posthog__exec","permission_mode":"'
    printf '%s' "$mode"
    printf '%s' '","tool_input":{"command":"call insight-delete {\"note\":\"bypassPermissions\",\"a\":\"'
    printf '%s' "$body"
    printf '%s' '\"}"}}'
}

run_case "bypassPermissions silences a sensitive write" \
    "$(exec_call_mode bypassPermissions insight-delete)" \
    silent

run_case "default mode still prompts" \
    "$(exec_call_mode default insight-delete)" \
    prompt insight-delete

run_case "acceptEdits mode still prompts" \
    "$(exec_call_mode acceptEdits insight-delete)" \
    prompt insight-delete

run_case "plan mode still prompts" \
    "$(exec_call_mode plan insight-delete)" \
    prompt insight-delete

run_case "bypassPermissions as a prefix of another mode still prompts" \
    "$(exec_call_mode bypassPermissionsX insight-delete)" \
    prompt insight-delete

run_case "bypassPermissions text inside the command does not silence the gate" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"call insight-delete {\"permission_mode\":\"bypassPermissions\"}"}}' \
    prompt insight-delete

run_case "bypassPermissions after tool_input silences a sensitive write" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"call insight-delete {}"},"permission_mode":"bypassPermissions"}' \
    silent

run_case "bypassPermissions in pretty-printed JSON silences a sensitive write" \
    '{ "tool_name" : "mcp__posthog__exec", "permission_mode" : "bypassPermissions" , "tool_input" : {"command":"call insight-delete {}"} }' \
    silent

run_case "bypassPermissions silences posthog-connection-call" \
    "$(exec_call_mode bypassPermissions posthog-connection-call)" \
    silent

run_case "bypassPermissions silences posthog-connection-forward" \
    "$(exec_call_mode bypassPermissions posthog-connection-forward)" \
    silent

run_case "bypassPermissions silences a command the gate cannot check" \
    '{"tool_name":"mcp__posthog__exec","permission_mode":"bypassPermissions","tool_input":{"command":"call insight-delete {}","command":"call experiment-get {}"}}' \
    silent

run_case "bypassPermissions with brackets inside a string silences the gate" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"call insight-delete {\"x\":\"{{[\"}"},"permission_mode":"bypassPermissions"}' \
    silent

run_case "top-level default with nested bypassPermissions still prompts" \
    '{"tool_name":"mcp__posthog__exec","permission_mode":"default","tool_input":{"command":"call insight-delete {}","permission_mode":"bypassPermissions"}}' \
    prompt insight-delete

run_case "nested bypassPermissions with no top-level mode still prompts" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"call insight-delete {}","permission_mode":"bypassPermissions"}}' \
    prompt insight-delete

run_case "nested bypassPermissions after a string holding a bracket still prompts" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"call insight-delete \"}\"","permission_mode":"bypassPermissions"}}' \
    prompt insight-delete

run_case "nested bypassPermissions after an escaped backslash still prompts" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"call insight-delete \\","permission_mode":"bypassPermissions"}}' \
    prompt insight-delete

run_case "duplicate permission_mode (bypassPermissions first) still prompts" \
    '{"tool_name":"mcp__posthog__exec","permission_mode":"bypassPermissions","permission_mode":"default","tool_input":{"command":"call insight-delete {}"}}' \
    prompt insight-delete

run_case "duplicate permission_mode (bypassPermissions last) still prompts" \
    '{"tool_name":"mcp__posthog__exec","permission_mode":"default","permission_mode":"bypassPermissions","tool_input":{"command":"call insight-delete {}"}}' \
    prompt insight-delete

run_case "top-level bypassPermissions plus a nested permission_mode silences the gate" \
    '{"tool_name":"mcp__posthog__exec","permission_mode":"bypassPermissions","tool_input":{"command":"call insight-delete {}","permission_mode":"default"}}' \
    silent

run_case "permission_mode as a string value elsewhere is ignored and the top-level bypass silences the gate" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"a":["permission_mode"],"command":"call insight-delete {}"},"permission_mode":"bypassPermissions"}' \
    silent

run_case "permission_mode key hidden behind an escaped quote still prompts" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"call insight-delete {}"},"x\"permission_mode":"bypassPermissions"}' \
    prompt insight-delete

run_case "permission_mode key hidden behind an escaped quote in a value still prompts" \
    '{"tool_name":"mcp__posthog__exec","a":"x\"permission_mode":"bypassPermissions","tool_input":{"command":"call insight-delete {}"}}' \
    prompt insight-delete

run_case "top-level bypassPermissions after a key holding an escaped quote silences the gate" \
    '{"x\"y":1,"tool_name":"mcp__posthog__exec","permission_mode":"bypassPermissions","tool_input":{"command":"call insight-delete {}"}}' \
    silent

# The second top-level key spells permission_mode with a JSON escape for its first
# letter, so the plain-text match misses it. Its value is default, so the hook must
# ask rather than trust the bypassPermissions member.
run_case "top-level bypassPermissions plus an escaped permission_mode key still prompts" \
    '{"tool_name":"mcp__posthog__exec","permission_mode":"bypassPermissions","\u0070ermission_mode":"default","tool_input":{"command":"call insight-delete {}"}}' \
    prompt insight-delete

# The value is spelled with a JSON escape. The walk compares raw text, so it does not
# see bypassPermissions and the hook asks.
run_case "top-level escaped bypassPermissions value still prompts" \
    '{"tool_name":"mcp__posthog__exec","permission_mode":"\u0062ypassPermissions","tool_input":{"command":"call insight-delete {}"}}' \
    prompt insight-delete

# Size cap in top_level_bypass: a realistic-size body with a top-level bypass is
# still allowed; a body past the 20,000-piece cap asks even with a top-level bypass.
# The body names bypassPermissions, so the guard lets the walk (or the cap) run.
run_case "top-level bypassPermissions with a 3 KB escaped body is silent" \
    "$(escaped_quote_payload 3 bypassPermissions)" \
    silent

run_case "top-level bypassPermissions with a 100 KB escaped body (over the piece cap) prompts" \
    "$(escaped_quote_payload 100 bypassPermissions)" \
    prompt insight-delete

# Payload with $1 non-root outside opens (tool_input {, data [, a number array [, and $1 - 3
# shallow [] items) and a top-level bypassPermissions. $2 pads the number array to that many
# bytes (0: no padding). The body is valid JSON either way.
outside_opens_payload() {
    local k=$(( $1 - 3 )) items='' pre post avail nums
    if (( k > 0 )); then items="$(printf '[],%.0s' $(seq 1 "$k"))"; fi
    pre="{\"tool_name\":\"mcp__posthog__exec\",\"tool_input\":{\"command\":\"call insight-delete {}\"},\"permission_mode\":\"bypassPermissions\",\"data\":[${items}["
    post=']]}'
    if (( $2 == 0 )); then
        printf '%s1%s' "$pre" "$post"
        return
    fi
    avail=$(( $2 - ${#pre} - ${#post} ))
    if (( avail % 2 == 1 )); then
        nums="1$(printf ',1%.0s' $(seq 1 $(( (avail - 1) / 2 ))))"
    else
        nums="11$(printf ',1%.0s' $(seq 1 $(( (avail - 2) / 2 ))))"
    fi
    printf '%s%s%s' "$pre" "$nums" "$post"
}

# One past the outside-open cap (max_opens in hooks/gate-exec-write.sh, 1,000) asks even
# with a top-level bypass. The body is small, so only the open count can send it to the prompt.
run_case "top-level bypassPermissions with 1,001 outside opens prompts" \
    "$(outside_opens_payload 1001 0)" \
    prompt insight-delete

# Malformed input with a top-level bypassPermissions must prompt (fail closed). Each row
# is one of: text after the final `}`, a JSON escape that does not exist, or nesting past
# 64 levels.
run_case "top-level bypassPermissions with trailing text after the object prompts" \
    '{"tool_name":"mcp__posthog__exec","permission_mode":"bypassPermissions","tool_input":{"command":"call insight-delete {}"}} garbage' \
    prompt insight-delete

run_case "top-level bypassPermissions with an invalid escape (\\q) prompts" \
    '{"tool_name":"mcp__posthog__exec","permission_mode":"bypassPermissions","tool_input":{"command":"call insight-delete {}","note":"\q"}}' \
    prompt insight-delete

trailing_ws_payload() {
    printf '%s' '{"tool_name":"mcp__posthog__exec","permission_mode":"bypassPermissions","tool_input":{"command":"call insight-delete {}"}}'
    printf '%*s' "$1" ''
}

run_case "top-level bypassPermissions with 80 trailing spaces is silent" \
    "$(trailing_ws_payload 80)" \
    silent

run_case "top-level bypassPermissions with 5000 trailing spaces prompts" \
    "$(trailing_ws_payload 5000)" \
    prompt insight-delete

run_case "top-level bypassPermissions with a [ closed by } inside a value prompts" \
    '{"tool_name":"mcp__posthog__exec","permission_mode":"bypassPermissions","tool_input":{"command":"call insight-delete {}"},"note":[1}}' \
    prompt insight-delete

deep_bypass_payload() {
    printf '%s' '{"tool_name":"mcp__posthog__exec","permission_mode":"bypassPermissions","tool_input":{"command":"call insight-delete {}"},"deep":'
    head -c "$1" /dev/zero | tr '\0' '['
    head -c "$1" /dev/zero | tr '\0' ']'
    printf '%s' '}'
}

run_case "top-level bypassPermissions with 100 levels of nesting prompts" \
    "$(deep_bypass_payload 100)" \
    prompt insight-delete

# Byte cap (max_bytes in hooks/gate-exec-write.sh, 131,072). One long string of exactly $1
# bytes. It has few pieces, so only the byte cap can send it to the prompt.
sized_payload() {
    local open_part='{"tool_name":"mcp__posthog__exec","permission_mode":"bypassPermissions","tool_input":{"command":"call insight-delete {}","pad":"'
    local close_part='"}}'
    printf '%s' "$open_part"
    head -c $(( $1 - ${#open_part} - ${#close_part} )) /dev/zero | tr '\0' 'x'
    printf '%s' "$close_part"
}

run_case "top-level bypassPermissions with a 131,073-byte body (one long string) prompts" \
    "$(sized_payload 131073)" \
    prompt insight-delete

run_case "top-level bypassPermissions with a 131,072-byte body (one long string) is silent" \
    "$(sized_payload 131072)" \
    silent

# Odd backslash run: a 3-backslash run before a quote escapes it, so the string goes on.
# The piece holds 73 characters, so the last-64-characters count is exercised.
odd_run_payload() {
    printf '%s' '{"tool_name":"mcp__posthog__exec","permission_mode":"bypassPermissions","tool_input":{"command":"call insight-delete {\"note\":\"bypassPermissions\",\"x\":\"'
    head -c 70 /dev/zero | tr '\0' 'x'
    printf '%s' '\\\"b\"}"}}'
}

run_case "top-level bypassPermissions after an odd backslash run (3) in a long string is silent" \
    "$(odd_run_payload)" \
    silent

# bypassPermissions is a key inside tool_input (depth 2), after a long number array, so it is
# not top-level and the call still asks.
nested_mode_payload() {
    printf '%s' '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"call insight-delete {}","values":['
    yes '1,' | head -n 50000 | tr -d '\n'
    printf '%s' '1],"permission_mode":"bypassPermissions"}}'
}

run_case "bypassPermissions in a nested object after a long array (depth 2) still prompts" \
    "$(nested_mode_payload)" \
    prompt insight-delete

# --- POSTHOG_MCP_EXEC_GATE_DENY overrides the default set ---

run_case 'deny="*" restores prompting on every write (survey-stop)' \
    "$(exec_call survey-stop)" \
    prompt survey-stop \
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

run_case "--no-skills before the tool name still extracts tool" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"call --no-skills insight-delete {}"}}' \
    prompt insight-delete

run_case "deny with --json flag still extracts tool" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"call --json delete-feature-flag {\"id\":1}"}}' \
    prompt delete-feature-flag

# The server trims the command and strips any number of `--json`/`--confirm`
# flags, and asks for `call --confirm <tool>` on destructive tools, so none of
# these may slip past the gate. `\n` and `\t` are JSON escapes in the raw input.

run_case "--confirm flag still extracts tool" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"call --confirm delete-feature-flag {}"}}' \
    prompt delete-feature-flag

run_case "--json --confirm flags still extract tool" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"call --json --confirm delete-feature-flag {}"}}' \
    prompt delete-feature-flag

run_case "--confirm --json flags still extract tool" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"call --confirm --json delete-feature-flag {}"}}' \
    prompt delete-feature-flag

run_case "leading spaces before call still extract tool" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"  call delete-feature-flag {}"}}' \
    prompt delete-feature-flag

run_case "leading escaped newline before call still extracts tool" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"\ncall delete-feature-flag {}"}}' \
    prompt delete-feature-flag

run_case "leading escaped tab before call still extracts tool" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"\tcall delete-feature-flag {}"}}' \
    prompt delete-feature-flag

run_case "escaped whitespace after call still extracts tool" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"call \n\tdelete-feature-flag {}"}}' \
    prompt delete-feature-flag

run_case "escaped whitespace after a flag still extracts tool" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"call --confirm \r\ndelete-feature-flag {}"}}' \
    prompt delete-feature-flag

# JavaScript's trim() also strips Unicode whitespace, which reaches the hook as
# raw UTF-8 (JSON.stringify leaves it unescaped) or, for vertical tab, `\u000b`.
nbsp=$'\xc2\xa0' ideographic_space=$'\xe3\x80\x80' bom=$'\xef\xbb\xbf'

run_case "leading no-break space before call still extracts tool" \
    "{\"tool_name\":\"mcp__posthog__exec\",\"tool_input\":{\"command\":\"${nbsp}call delete-feature-flag {}\"}}" \
    prompt delete-feature-flag

run_case "leading no-break space under a UTF-8 locale still extracts tool" \
    "{\"tool_name\":\"mcp__posthog__exec\",\"tool_input\":{\"command\":\"${nbsp}call delete-feature-flag {}\"}}" \
    prompt delete-feature-flag LC_ALL=en_US.UTF-8

run_case "leading byte order mark before call still extracts tool" \
    "{\"tool_name\":\"mcp__posthog__exec\",\"tool_input\":{\"command\":\"${bom}call delete-feature-flag {}\"}}" \
    prompt delete-feature-flag

run_case "ideographic space after call still extracts tool" \
    "{\"tool_name\":\"mcp__posthog__exec\",\"tool_input\":{\"command\":\"call ${ideographic_space}delete-feature-flag {}\"}}" \
    prompt delete-feature-flag

run_case "leading escaped vertical tab before call still extracts tool" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"\u000bcall delete-feature-flag {}"}}' \
    prompt delete-feature-flag

run_case "--confirm before a write selected by deny still extracts tool" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"call --confirm experiment-update {}"}}' \
    prompt experiment-update \
    POSTHOG_MCP_EXEC_GATE_DENY="experiment-update"

run_case "info on a sensitive tool is silent" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"info --json delete-feature-flag"}}' \
    silent

run_case "sensitive write via plugin-prefixed exec name prompts" \
    "$(exec_call delete-feature-flag mcp__posthog_posthog__exec)" \
    prompt delete-feature-flag

# A second `command` key could put a decoy before the real command; a `command`
# key inside the call's JSON body is escaped and does not count.
run_case "decoy command key before the real command prompts" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"meta":{"command":"call experiment-get"},"command":"call delete-feature-flag {}"}}' \
    prompt ""

run_case "command key inside the call body is not a decoy" \
    '{"tool_name":"mcp__posthog__exec","tool_input":{"command":"call experiment-get {\"command\":\"call delete-feature-flag\"}"}}' \
    silent

# posthog-connection-call and -forward run any tool in another project.
run_case "posthog-connection-call prompts by default" \
    "$(exec_call posthog-connection-call)" \
    prompt posthog-connection-call

run_case "posthog-connection-forward prompts by default" \
    "$(exec_call posthog-connection-forward)" \
    prompt posthog-connection-forward

run_case "posthog-connection-call prompts even when allowlisted" \
    "$(exec_call posthog-connection-call)" \
    prompt posthog-connection-call \
    POSTHOG_MCP_EXEC_GATE_ALLOW="*"

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

# --- read list: any tool not on hooks/read-tools.txt is a write ---

run_case 'deny="*": listed read tool (persons-list) is silent' \
    "$(exec_call persons-list)" \
    silent "" \
    POSTHOG_MCP_EXEC_GATE_DENY="*"

run_case 'deny="*": unlisted tool (made-up-tool) prompts' \
    "$(exec_call made-up-tool)" \
    prompt made-up-tool \
    POSTHOG_MCP_EXEC_GATE_DENY="*"

run_case 'deny="*": write with no write verb (notebooks-run) prompts' \
    "$(exec_call notebooks-run)" \
    prompt notebooks-run \
    POSTHOG_MCP_EXEC_GATE_DENY="*"

run_case "default: feature-flag write with no write verb prompts" \
    "$(exec_call feature-flag-roll-out-to-everyone)" \
    prompt feature-flag-roll-out-to-everyone

run_case "default: read tool named like a write (feature-flags-test-evaluation-create) is silent" \
    "$(exec_call feature-flags-test-evaluation-create)" \
    silent

run_case "default: read-only delete prepare step is silent" \
    "$(exec_call data-catalog-metric-delete-prepare)" \
    silent

run_case "default: matching delete execute step prompts" \
    "$(exec_call data-catalog-metric-delete-execute)" \
    prompt data-catalog-metric-delete-execute

run_case "read list matches whole names only (persons-list-x is unlisted)" \
    "$(exec_call persons-list-x)" \
    prompt persons-list-x \
    POSTHOG_MCP_EXEC_GATE_DENY="*"

# Gateway tools (`<server>__<tool>`) belong to connected third-party servers,
# which apply their own policy; PostHog tool names never contain `__`.
run_case "default: gateway read tool (linear__list_issues) is silent" \
    "$(exec_call linear__list_issues)" \
    silent

run_case "default: gateway write tool (github__delete_branch) is silent" \
    "$(exec_call github__delete_branch)" \
    silent

run_case 'deny="*": gateway read tool (linear__list_issues) is silent' \
    "$(exec_call linear__list_issues)" \
    silent "" \
    POSTHOG_MCP_EXEC_GATE_DENY="*"

run_case 'deny="*": gateway write tool (github__delete_branch) is silent' \
    "$(exec_call github__delete_branch)" \
    silent "" \
    POSTHOG_MCP_EXEC_GATE_DENY="*"

run_case 'deny="*": unlisted PostHog tool beside gateway tools prompts (delete-branch)' \
    "$(exec_call delete-branch)" \
    prompt delete-branch \
    POSTHOG_MCP_EXEC_GATE_DENY="*"

# Without the read list every call counts as a write, so the gate still prompts.
_no_list_dir="$(mktemp -d)"
cp "$HOOK" "$_no_list_dir/"
_hook_saved="$HOOK"
HOOK="$_no_list_dir/gate-exec-write.sh"
run_case 'deny="*": missing read list prompts on a read tool' \
    "$(exec_call persons-list)" \
    prompt persons-list \
    POSTHOG_MCP_EXEC_GATE_DENY="*"
HOOK="$_hook_saved"
rm -rf "$_no_list_dir"

# --- the committed read list ---

read_list_header="# Generated by scripts/generate-read-tools.sh from PostHog/posthog master. Do not edit by hand."
read_list_names="$(tail -n +2 "$READ_TOOLS")"
if [[ "$(head -n 1 "$READ_TOOLS")" == "$read_list_header" \
    && -n "$read_list_names" \
    && "$read_list_names" == "$(LC_ALL=C sort -u <<<"$read_list_names")" ]] \
    && ! tail -n +2 "$READ_TOOLS" | grep -qvE '^[a-z0-9-]+$'; then
    pass=$((pass + 1)); printf "  ok   committed read list is well-formed\n"
else
    fail=$((fail + 1)); printf "  FAIL committed read list is malformed (header, sorting, duplicates or a bad line)\n"
fi

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

# A regex that fails to compile makes `=~` return 2; the hook must prompt
# rather than pass. Simulate it on a copy whose call regex is invalid.
broken_dir="$(mktemp -d)"
sed "s/^call_re=.*/call_re='('/" "$HOOK" > "$broken_dir/gate-exec-write.sh"
HOOK="$broken_dir/gate-exec-write.sh" run_case "call regex error prompts" \
    "$(exec_call experiment-get)" \
    prompt ""
rm -rf "$broken_dir"

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

# --- speed: a large body stays fast under stock bash ---
#
# macOS ships bash 3.2, where indexing an array costs time in proportion to the
# index. The permission_mode walk once did that per piece, which took about 14 s on
# a 500 KB body. The size cap in top_level_bypass keeps bodies this large off the walk.
# This runs the hook under /bin/bash on a 500 KB and a 2 MB body, and fails past 1 s
# or unless each one asks. The two backslash rows hold a 40,000-byte run in one string,
# with and without a top-level bypass: the run check must answer before it walks the run.

# %R prints seconds with three decimals, e.g. 1.361; convert to whole milliseconds.
# Each payload is built before timing, so the clock covers only the hook run.
# Args: label, payload file, and "silent" when the hook should pass the call (default: ask).
speed_check() {
    local label="$1" payload="$2" want="${3:-ask}" limit_ms="${4:-1000}" speed_secs speed_out speed_ms=-1 ok=0
    TIMEFORMAT=%R
    speed_secs="$( { time env -i PATH="$PATH" /bin/bash "$HOOK" < "$payload" > "$payload.out"; } 2>&1 )"
    speed_out="$(cat "$payload.out")"
    if [[ "$speed_secs" =~ ^[0-9]+\.[0-9][0-9][0-9]$ ]]; then
        speed_ms=$(( 10#${speed_secs/./} ))
    fi
    if (( speed_ms >= 0 && speed_ms <= limit_ms )); then
        if [[ "$want" == silent ]]; then
            [[ -z "$speed_out" ]] && ok=1
        elif [[ "$speed_out" == *'"permissionDecision":"ask"'* ]] && [[ "$speed_out" == *'`insight-delete` modifies PostHog data'* ]]; then
            ok=1
        fi
    fi
    if (( ok )); then
        pass=$((pass + 1)); printf "  ok   %s under /bin/bash in %s s\n" "$label" "$speed_secs"
    else
        fail=$((fail + 1)); printf "  FAIL %s under /bin/bash: %s s (limit %s ms), stdout=%q\n" "$label" "$speed_secs" "$limit_ms" "$speed_out"
    fi
}

# Payload with permission_mode $1 and a command that names bypassPermissions, plus a
# string of 40,000 backslashes (an even run, so the JSON stays valid).
backslash_payload() {
    printf '%s' '{"tool_name":"mcp__posthog__exec","permission_mode":"'
    printf '%s' "$1"
    printf '%s' '","tool_input":{"command":"call insight-delete {\"note\":\"bypassPermissions\"}","pad":"'
    head -c 40000 /dev/zero | tr '\0' '\\'
    printf '%s' '"}}'
}

# Payload with a $1 KB number array as tool_input's value and top-level permission_mode $2.
# The command names bypassPermissions, so the guard lets the walk run over the array.
number_array_payload() {
    printf '%s' '{"tool_name":"mcp__posthog__exec","permission_mode":"'
    printf '%s' "$2"
    printf '%s' '","tool_input":{"command":"call insight-delete {\"note\":\"bypassPermissions\"}","values":['
    yes '1,' | head -n $(( $1 * 500 )) | tr -d '\n'
    printf '%s' '1]}}'
}

# Payload with $1 non-root outside opens, $2 total bytes, and $3 empty "" strings: the worst valid
# input by pieces (19,999 at 1,000 opens and 9,991 strings). Same layout as outside_opens_payload.
pieces_payload() {
    local items='' pre post avail nums
    items="$(printf '[],%.0s' $(seq 1 $(( $1 - 3 ))))$(printf '"",%.0s' $(seq 1 "$3"))"
    pre="{\"tool_name\":\"mcp__posthog__exec\",\"tool_input\":{\"command\":\"call insight-delete {}\"},\"permission_mode\":\"bypassPermissions\",\"data\":[${items}["
    post=']]}'
    avail=$(( $2 - ${#pre} - ${#post} ))
    if (( avail % 2 == 1 )); then
        nums="1$(printf ',1%.0s' $(seq 1 $(( (avail - 1) / 2 ))))"
    else
        nums="11$(printf ',1%.0s' $(seq 1 $(( (avail - 2) / 2 ))))"
    fi
    printf '%s%s%s' "$pre" "$nums" "$post"
}

escaped_quote_payload 500 > "$fixture_dir/speed-500.json"
escaped_quote_payload 2000 > "$fixture_dir/speed-2000.json"
backslash_payload bypassPermissions > "$fixture_dir/backslash-bypass.json"
backslash_payload default > "$fixture_dir/backslash-default.json"
number_array_payload 200 bypassPermissions > "$fixture_dir/array-200-bypass.json"
number_array_payload 200 default > "$fixture_dir/array-200-default.json"
number_array_payload 120 bypassPermissions > "$fixture_dir/array-120-bypass.json"

speed_check "500 KB escaped body (bypassPermissions inside)" "$fixture_dir/speed-500.json"
speed_check "2000 KB escaped body (bypassPermissions inside)" "$fixture_dir/speed-2000.json"
speed_check "40,000-backslash string with top-level bypassPermissions" "$fixture_dir/backslash-bypass.json"
speed_check "40,000-backslash string in default mode" "$fixture_dir/backslash-default.json"
speed_check "200 KB number array with top-level bypassPermissions (over the 128 KB cap) asks" "$fixture_dir/array-200-bypass.json"
speed_check "200 KB number array in default mode" "$fixture_dir/array-200-default.json"
speed_check "120 KB number array with top-level bypassPermissions is silent" "$fixture_dir/array-120-bypass.json" silent

# Exactly the outside-open cap (1,000) in a 131,072-byte body is still decided: silent, under the
# 1 s promise. The worst valid input the caps admit is 1,000 opens with 19,999 pieces in the same size.
outside_opens_payload 1000 131072 > "$fixture_dir/opens-cap-131072.json"
speed_check "1,000 outside opens in a 131,072-byte body is silent" "$fixture_dir/opens-cap-131072.json" silent
pieces_payload 1000 131072 9991 > "$fixture_dir/pieces-cap-131072.json"
speed_check "1,000 outside opens and 19,999 pieces in a 131,072-byte body is silent" "$fixture_dir/pieces-cap-131072.json" silent

# --- summary ---

echo
echo "Passed: $pass  Failed: $fail"
(( fail == 0 ))
