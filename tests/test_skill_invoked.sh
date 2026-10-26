#!/usr/bin/env bash
# Tests for hooks/skill-invoked.sh.
#
# Bash plus python3 to parse the sent body. Run from anywhere, under the bash
# the hook should be tested with:
#
#     ./tests/test_skill_invoked.sh
#     /bin/bash ./tests/test_skill_invoked.sh
#
# Each case feeds a PostToolUse or UserPromptExpansion JSON payload (the
# shapes Claude Code passes on stdin) to the hook with a controlled
# environment, then asserts whether the hook sent an event and what the
# payload contained. The network call is
# intercepted by a fake `curl` on PATH that records the request to a file, so
# nothing leaves the machine.

# PostHog property names start with `$`, so single-quoted `$` is literal on purpose.
# shellcheck disable=SC2016

set -u

HERE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$HERE/.." && pwd)"
HOOK="$REPO_ROOT/hooks/skill-invoked.sh"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# --- fake curl: records URL + -d payload, sends nothing ------------------
FAKEBIN="$TMP/bin"
mkdir -p "$FAKEBIN"
cat > "$FAKEBIN/curl" <<'EOF'
#!/usr/bin/env bash
url="" ; payload=""
while (( $# )); do
    case "$1" in
        -d) payload="$2"; shift 2;;
        -X|-H|-m) shift 2;;
        http://*|https://*) url="$1"; shift;;
        *) shift;;
    esac
done
{ printf 'URL %s\n' "$url"; printf 'BODY %s\n' "$payload"; } >> "$CURL_CAPTURE"
EOF
chmod +x "$FAKEBIN/curl"

pass=0
fail=0

# Run the hook with an isolated env. Globals set per call:
#   CAP     — capture file for this run (reset)
#   OUT     — the hook's stdout
#   STATUS  — the hook's exit status
# Args:
#   $1 payload   $2 fresh-home? (1 to wipe the telemetry-id) $3+ env overrides
CAP=""
OUT=""
STATUS=0
run_hook() {
    local payload="$1" fresh="$2"; shift 2
    CAP="$TMP/capture.$RANDOM"
    : > "$CAP"
    local home="$TMP/home"
    (( fresh )) && rm -rf "$home"
    mkdir -p "$home"
    OUT="$(env -i PATH="$FAKEBIN:$PATH" HOME="$home" \
        CLAUDE_PLUGIN_ROOT="$REPO_ROOT" \
        CURL_CAPTURE="$CAP" \
        POSTHOG_PLUGIN_TELEMETRY_HOST="http://localhost:0" \
        "$@" "$BASH" "$HOOK" <<<"$payload")"
    STATUS=$?
}

# Wait (bounded) for the backgrounded fake curl to record a request.
wait_sent() { local _; for _ in $(seq 1 60); do [[ -s "$CAP" ]] && return 0; sleep 0.05; done; return 1; }
# Give a no-op case a moment, then confirm nothing was recorded.
assert_silent() { sleep 0.3; [[ ! -s "$CAP" ]]; }

ok()   { pass=$((pass + 1)); printf "  ok   %s\n" "$1"; }
bad()  { fail=$((fail + 1)); printf "  FAIL %s\n       %s\n" "$1" "${2:-}"; }

body() { sed -n 's/^BODY //p' "$CAP"; }
# JSON-encoded value of a property in the sent body; fails when the body isn't valid JSON.
prop() { body | python3 -I -c 'import json, sys; print(json.dumps(json.load(sys.stdin)["properties"].get(sys.argv[1])))' "$1"; }

# PostToolUse payload for a Skill invocation.
skill_payload() {
    local skill="$1" args="${2:-}"
    if [[ -n "$args" ]]; then
        printf '{"hook_event_name":"PostToolUse","permission_mode":"default","tool_name":"Skill","tool_input":{"skill":"%s","args":"%s"},"tool_response":{"ok":true}}' "$skill" "$args"
    else
        printf '{"hook_event_name":"PostToolUse","permission_mode":"default","tool_name":"Skill","tool_input":{"skill":"%s"},"tool_response":{"ok":true}}' "$skill"
    fi
}

# UserPromptExpansion payload for a user-typed slash command.
expansion_payload() {
    local name="$1" args="${2:-}" type="${3:-slash_command}" source="${4:-plugin}"
    printf '{"hook_event_name":"UserPromptExpansion","permission_mode":"default","expansion_type":"%s","command_name":"%s","command_args":"%s","command_source":"%s","prompt":"/%s %s"}' \
        "$type" "$name" "$args" "$source" "$name" "$args"
}

echo "Running skill-invoked.sh tests..."

# --- captured: this plugin's skills --------------------------------------

# Top-level and property keys of the sent body, sorted and space-separated.
keys() { body | python3 -I -c 'import json, sys; e = json.load(sys.stdin); print(" ".join(sorted(e)), "|", " ".join(sorted(e["properties"])))'; }

run_hook "$(skill_payload "posthog:querying-posthog-data")" 1
wait_sent
if [[ "$(keys)" == 'api_key distinct_id event properties | $geoip_disable $ip $lib $process_person_profile args_present invocation os permission_mode plugin_version skill' ]]; then
    ok "payload carries only the disclosed fields"
else
    bad "payload carries only the disclosed fields" "keys=$(keys)"
fi
if [[ "$(prop skill)" == '"querying-posthog-data"' ]]; then ok "skill slug sent without namespace"; else bad "skill slug sent without namespace" "body=$(body)"; fi
if [[ "$(prop args_present)" == "false" ]]; then ok "args_present false without args"; else bad "args_present false without args" "body=$(body)"; fi
if [[ "$(prop plugin_version)" == "\"$(sed -n 's/.*"version": *"\([^"]*\)".*/\1/p' "$REPO_ROOT/.claude-plugin/plugin.json")\"" ]]; then
    ok "plugin version read from the manifest"
else
    bad "plugin version read from the manifest" "body=$(body)"
fi

if [[ "$(prop invocation)" == '"model"' ]]; then ok "Skill tool call counted as a model invocation"; else bad "Skill tool call counted as a model invocation" "body=$(body)"; fi
if [[ "$STATUS" == 0 && -z "$OUT" ]]; then ok "PostToolUse exits 0 with no output"; else bad "PostToolUse exits 0 with no output" "status=$STATUS out=$OUT"; fi

# Codex sets PLUGIN_ROOT, but no longer ships this hook; nothing should depend on it.
run_hook "$(skill_payload "posthog:querying-posthog-data")" 1 PLUGIN_ROOT="$REPO_ROOT"
if wait_sent && [[ "$(body)" != *codex* ]]; then ok "no Codex client label"; else bad "no Codex client label" "body=$(body)"; fi

# args present → boolean true, but the content must never appear.
run_hook "$(skill_payload "posthog:exploring-llm-traces" "SECRET_ARG_PAYLOAD path/to/file")" 1
if wait_sent && [[ "$(prop args_present)" == "true" && "$(body)" != *"SECRET_ARG_PAYLOAD"* ]]; then
    ok "args presence captured as boolean, content never sent"
else
    bad "args presence captured as boolean, content never sent" "body=$(body)"
fi

# --- user-typed slash commands --------------------------------------------

run_hook "$(expansion_payload "posthog:querying-posthog-data")" 1
wait_sent
if [[ "$(prop invocation)" == '"user"' && "$(prop skill)" == '"querying-posthog-data"' ]]; then
    ok "slash command counted as a user invocation"
else
    bad "slash command counted as a user invocation" "body=$(body)"
fi
if [[ "$(keys)" == *'| $geoip_disable $ip $lib $process_person_profile args_present invocation os permission_mode plugin_version skill' ]]; then
    ok "slash command payload carries the same fields"
else
    bad "slash command payload carries the same fields" "keys=$(keys)"
fi
if [[ "$(prop args_present)" == "false" ]]; then ok "slash command without args"; else bad "slash command without args" "body=$(body)"; fi
# Claude Code adds UserPromptExpansion stdout to Claude's context.
if [[ "$STATUS" == 0 && -z "$OUT" ]]; then ok "UserPromptExpansion exits 0 with no output"; else bad "UserPromptExpansion exits 0 with no output" "status=$STATUS out=$OUT"; fi

run_hook "$(expansion_payload "posthog:exploring-llm-traces" "SECRET_ARG_PAYLOAD path/to/file")" 1
if wait_sent && [[ "$(prop args_present)" == "true" && "$(body)" != *"SECRET_ARG_PAYLOAD"* ]]; then
    ok "slash command args presence captured, content never sent"
else
    bad "slash command args presence captured, content never sent" "body=$(body)"
fi

for case in \
    "posthog:querying-posthog-data||mcp_prompt|plugin" \
    "posthog:querying-posthog-data||slash_command|userSettings" \
    "some-other-plugin:do-thing||slash_command|plugin" \
    "querying-posthog-data||slash_command|plugin" \
    "posthog:definitely-not-a-bundled-skill||slash_command|plugin" \
    'other:thing|\"command_name\":\"posthog:querying-posthog-data\"|slash_command|plugin'; do
    IFS='|' read -r name args type source <<<"$case"
    run_hook "$(expansion_payload "$name" "$args" "$type" "$source")" 1
    if assert_silent && [[ -z "$OUT" ]]; then ok "expansion $case is ignored"; else bad "expansion $case is ignored" "body=$(body) out=$OUT"; fi
done

# --- anonymous: no GeoIP lookup, client IP replaced before ingestion ------

run_hook "$(skill_payload "posthog:querying-posthog-data")" 1
wait_sent
if [[ "$(prop '$geoip_disable')" == "true" ]]; then ok "GeoIP lookup disabled"; else bad "GeoIP lookup disabled" "body=$(body)"; fi
if [[ "$(prop '$ip')" == '"127.0.0.1"' ]]; then ok "client IP replaced"; else bad "client IP replaced" "body=$(body)"; fi
if [[ "$(prop '$process_person_profile')" == "false" ]]; then ok "no person profile"; else bad "no person profile" "body=$(body)"; fi

# --- ignored: not this plugin's skills -----------------------------------

# A bundled skill's bare name can also be a project or user skill, so only the plugin namespace counts.
BARE_SKILL="querying-posthog-data"
[[ -d "$REPO_ROOT/skills/$BARE_SKILL" ]] || bad "fixture skill $BARE_SKILL exists"
for skill in \
    some-other-plugin:do-thing \
    other:querying-posthog-data \
    posthog-telemetry:querying-posthog-data \
    "$BARE_SKILL" \
    posthog:definitely-not-a-bundled-skill \
    posthog: \
    posthog:other:querying-posthog-data; do
    run_hook "$(skill_payload "$skill")" 1
    if assert_silent; then ok "skill '$skill' is ignored"; else bad "skill '$skill' is ignored" "body=$(body)"; fi
done

run_hook '{"tool_name":"Bash","tool_input":{"command":"ls"}}' 1
if assert_silent; then ok "non-Skill tool is ignored"; else bad "non-Skill tool is ignored" "body=$(body)"; fi

# A plugin skill named only in the tool response, not the input, is not an invocation of it.
run_hook '{"tool_name":"Skill","tool_input":{"skill":"other:thing"},"tool_response":{"skill":"posthog:querying-posthog-data"}}' 1
if assert_silent; then ok "skill named only in tool_response is ignored"; else bad "skill named only in tool_response is ignored" "body=$(body)"; fi

# --- hostile input never reaches the shell or the JSON body ---------------

PWNED="$TMP/pwned"
run_hook '{"permission_mode":"default\",\"x\":\"y","tool_name":"Skill","tool_input":{"args":"\",\"skill\":\"posthog:evil\"} $(touch '"$PWNED"') `touch '"$PWNED"'` SECRET_ARG_PAYLOAD","skill":"posthog:querying-posthog-data"}}' 1
wait_sent
if [[ "$(prop skill)" == '"querying-posthog-data"' && "$(prop args_present)" == "true" && "$(prop permission_mode)" == '""' ]]; then
    ok "quotes in args and permission_mode don't change the body"
else
    bad "quotes in args and permission_mode don't change the body" "body=$(body)"
fi
if [[ "$(body)" != *SECRET_ARG_PAYLOAD* && "$(body)" != *evil* ]]; then ok "args content never sent"; else bad "args content never sent" "body=$(body)"; fi
if [[ ! -e "$PWNED" ]]; then ok "command substitution in args never runs"; else bad "command substitution in args never runs"; fi

run_hook "$(skill_payload "posthog:querying-posthog-data")" 1 'POSTHOG_PLUGIN_TELEMETRY_KEY=k","event":"x'
if assert_silent; then ok "malformed key override is ignored"; else bad "malformed key override is ignored" "body=$(body)"; fi

run_hook '{"tool_name":"Skill","tool_input":{"skill":"posthog:querying-posthog-data\",\"x\":\"y"}}' 1
if assert_silent; then ok "skill name with JSON metacharacters is ignored"; else bad "skill name with JSON metacharacters is ignored" "body=$(body)"; fi

# A tampered id file, plugin manifest, and uname output can't inject into the body.
FAKE_ROOT="$TMP/fake-root"
mkdir -p "$FAKE_ROOT/.claude-plugin" "$FAKE_ROOT/skills/$BARE_SKILL" "$TMP/fakeuname"
printf '{"version": "1.0\\",\\"event\\":\\"x"}' > "$FAKE_ROOT/.claude-plugin/plugin.json"
printf '#!/bin/sh\necho %s\n' "'Linux\",\"event\":\"x'" > "$TMP/fakeuname/uname"
chmod +x "$TMP/fakeuname/uname"
mkdir -p "$TMP/home/.claude"
printf '%s\n' 'abc","event":"x' > "$TMP/home/.claude/posthog-plugin-telemetry-id"
run_hook "$(skill_payload "posthog:$BARE_SKILL")" 0 CLAUDE_PLUGIN_ROOT="$FAKE_ROOT" PATH="$TMP/fakeuname:$FAKEBIN:$PATH"
wait_sent
event="$(body | python3 -I -c 'import json, sys; e = json.load(sys.stdin); print(e["event"], e["distinct_id"])')"
if [[ "$event" =~ ^plugin\ skill\ invoked\ [A-Za-z0-9-]+$ && "$event" != *abc* ]]; then
    ok "tampered id file is replaced"
else
    bad "tampered id file is replaced" "body=$(body)"
fi
if [[ "$(prop plugin_version)" == '"1.0"' && "$(prop os)" == '"Linuxeventx"' ]]; then
    ok "manifest version and uname output are sanitised"
else
    bad "manifest version and uname output are sanitised" "body=$(body)"
fi

# --- consent guards ------------------------------------------------------

run_hook "$(skill_payload "posthog:querying-posthog-data")" 1 DO_NOT_TRACK=1
if assert_silent; then ok "DO_NOT_TRACK=1 disables capture"; else bad "DO_NOT_TRACK=1 disables capture" "body=$(body)"; fi

run_hook "$(skill_payload "posthog:querying-posthog-data")" 1 POSTHOG_PLUGIN_TELEMETRY_DISABLED=true
if assert_silent; then ok "POSTHOG_PLUGIN_TELEMETRY_DISABLED=true disables capture"; else bad "telemetry disabled flag" "body=$(body)"; fi

run_hook "$(skill_payload "posthog:querying-posthog-data")" 1 DO_NOT_TRACK=0
if wait_sent; then ok "DO_NOT_TRACK=0 does not disable capture"; else bad "DO_NOT_TRACK=0 does not disable capture" "no send"; fi

# Claude Code turns its own telemetry off by default on these providers; any truthy value selects one.
for provider in CLAUDE_CODE_USE_BEDROCK CLAUDE_CODE_USE_VERTEX CLAUDE_CODE_USE_FOUNDRY CLAUDE_CODE_USE_ANTHROPIC_AWS; do
    for value in 1 true YES On; do
        run_hook "$(skill_payload "posthog:querying-posthog-data")" 1 "$provider=$value"
        if assert_silent; then ok "$provider=$value disables capture"; else bad "$provider=$value disables capture" "body=$(body)"; fi
    done
    for value in 0 false ""; do
        run_hook "$(skill_payload "posthog:querying-posthog-data")" 1 "$provider=$value"
        if wait_sent; then ok "$provider='$value' keeps capture"; else bad "$provider='$value' keeps capture" "no send"; fi
    done
done

# Claude Code's own opt-outs treat any non-empty value, including 0 and false, as opting out.
for opt_out in DISABLE_TELEMETRY CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC; do
    for value in 1 0 false; do
        run_hook "$(skill_payload "posthog:querying-posthog-data")" 1 "$opt_out=$value"
        if assert_silent; then ok "$opt_out=$value disables capture"; else bad "$opt_out=$value disables capture" "body=$(body)"; fi
    done
done

# --- self-hosted users: never send to PostHog Cloud ----------------------

for setting in \
    POSTHOG_MCP_URL=https://mcp.example.com/mcp \
    POSTHOG_MCP_URL=https://mcp.posthog.com.example.com/mcp \
    POSTHOG_MCP_URL=http://localhost:8010/mcp \
    POSTHOG_HOST=https://posthog.internal \
    POSTHOG_HOST=https://user@posthog.com.example.com; do
    run_hook "$(skill_payload "posthog:querying-posthog-data")" 1 "$setting"
    if assert_silent; then ok "$setting disables capture"; else bad "$setting disables capture" "body=$(body)"; fi
done

for setting in \
    POSTHOG_MCP_URL=https://mcp.posthog.com/mcp \
    POSTHOG_MCP_URL=https://MCP-EU.POSTHOG.COM/mcp \
    POSTHOG_HOST=https://eu.i.posthog.com; do
    run_hook "$(skill_payload "posthog:querying-posthog-data")" 1 "$setting"
    if wait_sent; then ok "$setting keeps capture"; else bad "$setting keeps capture" "no send"; fi
done

# --- anonymous id is stable across runs ----------------------------------

run_hook "$(skill_payload "posthog:querying-posthog-data")" 1   # fresh home → new id
wait_sent; id1="$(body | sed -n 's/.*"distinct_id":"\([^"]*\)".*/\1/p')"
run_hook "$(skill_payload "posthog:querying-posthog-data")" 0   # reuse home → same id
wait_sent; id2="$(body | sed -n 's/.*"distinct_id":"\([^"]*\)".*/\1/p')"
if [[ -n "$id1" && "$id1" == "$id2" ]]; then
    ok "anonymous distinct_id persists across runs ($id1)"
else
    bad "anonymous distinct_id persists across runs" "id1=$id1 id2=$id2"
fi

# --- summary -------------------------------------------------------------

echo
echo "Passed: $pass  Failed: $fail"
(( fail == 0 ))
