#!/usr/bin/env bash
# Tests for hooks/skill-invoked.sh.
#
# Plain bash, no dependencies. Run from anywhere:
#
#     ./tests/test_skill_invoked.sh
#
# Each case feeds a PostToolUse JSON payload (the shape Claude Code passes on
# stdin) to the hook with a controlled environment, then asserts whether the
# hook sent an event and what the payload contained. The network call is
# intercepted by a fake `curl` on PATH that records the request to a file, so
# nothing leaves the machine.

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
#   CAP  — capture file for this run (reset)
# Args:
#   $1 payload   $2 fresh-home? (1 to wipe the telemetry-id) $3+ env overrides
CAP=""
run_hook() {
    local payload="$1" fresh="$2"; shift 2
    CAP="$TMP/capture.$RANDOM"
    : > "$CAP"
    local home="$TMP/home"
    (( fresh )) && rm -rf "$home"
    mkdir -p "$home"
    env -i PATH="$FAKEBIN:$PATH" HOME="$home" \
        CLAUDE_PLUGIN_ROOT="$REPO_ROOT" \
        CURL_CAPTURE="$CAP" \
        POSTHOG_PLUGIN_TELEMETRY_HOST="http://localhost:0" \
        "$@" bash "$HOOK" <<<"$payload"
}

# Wait (bounded) for the backgrounded fake curl to record a request.
wait_sent() { local i; for i in $(seq 1 60); do [[ -s "$CAP" ]] && return 0; sleep 0.05; done; return 1; }
# Give a no-op case a moment, then confirm nothing was recorded.
assert_silent() { sleep 0.3; [[ ! -s "$CAP" ]]; }

ok()   { pass=$((pass + 1)); printf "  ok   %s\n" "$1"; }
bad()  { fail=$((fail + 1)); printf "  FAIL %s\n       %s\n" "$1" "${2:-}"; }

body() { sed -n 's/^BODY //p' "$CAP"; }

# PostToolUse payload for a Skill invocation.
skill_payload() {
    local skill="$1" args="${2:-}"
    if [[ -n "$args" ]]; then
        printf '{"hook_event_name":"PostToolUse","permission_mode":"default","tool_name":"Skill","tool_input":{"skill":"%s","args":"%s"},"tool_response":{"ok":true}}' "$skill" "$args"
    else
        printf '{"hook_event_name":"PostToolUse","permission_mode":"default","tool_name":"Skill","tool_input":{"skill":"%s"},"tool_response":{"ok":true}}' "$skill"
    fi
}

echo "Running skill-invoked.sh tests..."

# --- captured: this plugin's skills --------------------------------------

run_hook "$(skill_payload "posthog:querying-posthog-data")" 1
if wait_sent && [[ "$(body)" == *'"skill":"posthog:querying-posthog-data"'* \
        && "$(body)" == *'"skill_name":"querying-posthog-data"'* \
        && "$(body)" == *'"skill_namespace":"posthog"'* \
        && "$(body)" == *'"event":"plugin skill invoked"'* \
        && "$(body)" == *'"$process_person_profile":false'* \
        && "$(body)" == *'"args_present":false'* ]]; then
    ok "posthog: namespaced skill is captured"
else
    bad "posthog: namespaced skill is captured" "body=$(body)"
fi

# A bundled skill invoked by bare name (matches a dir under skills/).
BARE_SKILL=""
for d in "$REPO_ROOT"/skills/*/; do BARE_SKILL="$(basename "$d")"; break; done
run_hook "$(skill_payload "$BARE_SKILL")" 1
if wait_sent && [[ "$(body)" == *"\"skill\":\"$BARE_SKILL\""* \
        && "$(body)" == *'"skill_namespace":""'* ]]; then
    ok "bundled bare-name skill ($BARE_SKILL) is captured"
else
    bad "bundled bare-name skill is captured" "body=$(body)"
fi

# args present → boolean true, but the content must never appear.
run_hook "$(skill_payload "posthog:exploring-llm-traces" "SECRET_ARG_PAYLOAD path/to/file")" 1
if wait_sent && [[ "$(body)" == *'"args_present":true'* && "$(body)" != *"SECRET_ARG_PAYLOAD"* ]]; then
    ok "args presence captured as boolean, content never sent"
else
    bad "args presence captured as boolean, content never sent" "body=$(body)"
fi

# --- ignored: not this plugin's skills -----------------------------------

run_hook "$(skill_payload "some-other-plugin:do-thing")" 1
if assert_silent; then ok "other-plugin skill is ignored"; else bad "other-plugin skill is ignored" "body=$(body)"; fi

run_hook "$(skill_payload "definitely-not-a-bundled-skill")" 1
if assert_silent; then ok "unknown project skill is ignored"; else bad "unknown project skill is ignored" "body=$(body)"; fi

run_hook '{"tool_name":"Bash","tool_input":{"command":"ls"}}' 1
if assert_silent; then ok "non-Skill tool is ignored"; else bad "non-Skill tool is ignored" "body=$(body)"; fi

# --- consent guards ------------------------------------------------------

run_hook "$(skill_payload "posthog:querying-posthog-data")" 1 DO_NOT_TRACK=1
if assert_silent; then ok "DO_NOT_TRACK=1 disables capture"; else bad "DO_NOT_TRACK=1 disables capture" "body=$(body)"; fi

run_hook "$(skill_payload "posthog:querying-posthog-data")" 1 POSTHOG_PLUGIN_TELEMETRY_DISABLED=true
if assert_silent; then ok "POSTHOG_PLUGIN_TELEMETRY_DISABLED=true disables capture"; else bad "telemetry disabled flag" "body=$(body)"; fi

run_hook "$(skill_payload "posthog:querying-posthog-data")" 1 DO_NOT_TRACK=0
if wait_sent; then ok "DO_NOT_TRACK=0 does not disable capture"; else bad "DO_NOT_TRACK=0 does not disable capture" "no send"; fi

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
