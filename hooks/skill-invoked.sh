#!/usr/bin/env bash
# Skill telemetry — anonymous plugin usage analytics.
#
# Fires on PostToolUse(Skill), when Claude invokes a skill, and on
# UserPromptExpansion, when the user types `/posthog:<skill>`. *Only for this
# plugin's own skills*, it sends a single "plugin skill invoked" event to a
# PostHog-owned project so the team can see which skills get used in the field.
# Captures the skill name plus safe metadata only — never the skill arguments or
# any free-text content.
#
# Privacy & consent:
#   - Anonymous: distinct_id is a random per-install UUID (no email, no PII),
#     and events set `$process_person_profile: false` so no person is created.
#     Ingestion copies the request IP into an empty `$ip`, so `$ip` carries a
#     fixed loopback address instead, and `$geoip_disable` skips the lookup.
#   - Opt-out (on by default). Disable with any of:
#         export DO_NOT_TRACK=1
#         export POSTHOG_PLUGIN_TELEMETRY_DISABLED=1
#         export DISABLE_TELEMETRY=1
#         export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
#     It is also off on Bedrock, Vertex, Foundry, and Claude Platform on AWS,
#     like Claude Code's own telemetry.
#   - Endpoint/key are overridable for testing via POSTHOG_PLUGIN_TELEMETRY_KEY
#     and POSTHOG_PLUGIN_TELEMETRY_HOST.
#
# Pure bash + curl; no jq or other third-party tools. Reads the hook JSON on
# stdin, sends in the background, and always exits 0 with no output — losing a
# telemetry event is fine, interfering with the user's session is not, and
# UserPromptExpansion stdout would reach Claude's context.
#
# Every value interpolated into the JSON body is matched against or stripped to
# a quote-free charset first, so no JSON escaping is needed.

set -u

# PostHog project (public, write-only ingestion key — safe to ship).
API_KEY="${POSTHOG_PLUGIN_TELEMETRY_KEY:-sTMFPsFhdP1Ssg}"
HOST="${POSTHOG_PLUGIN_TELEMETRY_HOST:-https://us.i.posthog.com}"

# --- consent guards (opt-out) --------------------------------------------
# DO_NOT_TRACK: any value other than empty/0/false means "do not track".
case "${DO_NOT_TRACK:-}" in
    ""|0|false|FALSE|False) ;;
    *) exit 0 ;;
esac
case "${POSTHOG_PLUGIN_TELEMETRY_DISABLED:-}" in
    ""|0|false|FALSE|False) ;;
    *) exit 0 ;;
esac
# Claude Code's opt-outs: any non-empty value, even 0 or false, opts out.
[[ -z "${DISABLE_TELEMETRY:-}" && -z "${CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC:-}" ]] || exit 0
# Claude Code's telemetry is off by default on third-party providers.
for provider in "${CLAUDE_CODE_USE_BEDROCK:-}" "${CLAUDE_CODE_USE_VERTEX:-}" "${CLAUDE_CODE_USE_FOUNDRY:-}" "${CLAUDE_CODE_USE_ANTHROPIC_AWS:-}"; do
    case "$(printf '%s' "$provider" | tr '[:upper:]' '[:lower:]')" in
        1|true|yes|on) exit 0 ;;
    esac
done
# Self-hosted users point the MCP server or LLM analytics at their own
# instance; keep their usage off PostHog Cloud. Unparseable hosts fail closed.
for url in "${POSTHOG_MCP_URL:-}" "${POSTHOG_HOST:-}"; do
    [[ -n "$url" ]] || continue
    host="${url#*://}"
    host="${host%%[/?#]*}"
    host="$(printf '%s' "${host%%:*}" | tr '[:upper:]' '[:lower:]')"
    [[ "$host" == posthog.com || "$host" == *.posthog.com ]] || exit 0
done
# An empty or malformed key override → no-op.
[[ "$API_KEY" =~ ^[A-Za-z0-9_-]+$ ]] || exit 0

# curl is required to send; if absent, no-op silently.
command -v curl >/dev/null 2>&1 || exit 0

ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." 2>/dev/null && pwd)}"

input="$(cat)"

# Whether arguments were passed is kept as presence only, never the content.
args_present=false
if [[ "$input" =~ \"hook_event_name\"[[:space:]]*:[[:space:]]*\"UserPromptExpansion\" ]]; then
    invocation=user
    # The input is flat, and a `"` inside a JSON string is always escaped, so
    # these key matches can't start inside the user's prompt or args.
    [[ "$input" =~ \"expansion_type\"[[:space:]]*:[[:space:]]*\"slash_command\" ]] || exit 0
    [[ "$input" =~ \"command_source\"[[:space:]]*:[[:space:]]*\"plugin\" ]] || exit 0
    [[ "$input" =~ \"command_name\"[[:space:]]*:[[:space:]]*\"([^\"]*)\" ]] || exit 0
    name="${BASH_REMATCH[1]}"
    if [[ "$input" =~ \"command_args\"[[:space:]]*:[[:space:]]*\"[^\"] ]]; then
        args_present=true
    fi
else
    invocation=model
    [[ "$input" =~ \"tool_name\"[[:space:]]*:[[:space:]]*\"Skill\" ]] || exit 0
    # Walk tool_input's top level one whole JSON string or non-brace byte at a
    # time, so a key match can't start inside a string (args) or leave the
    # object (tool_response). Group 3 is the value.
    tool_input='"tool_input"[[:space:]]*:[[:space:]]*\{([^"{}]|"([^"\\]|\\.)*")*'
    [[ "$input" =~ ${tool_input}\"skill\"[[:space:]]*:[[:space:]]*\"([^\"]*)\" ]] || exit 0
    name="${BASH_REMATCH[3]}"
    if [[ "$input" =~ ${tool_input}\"args\"[[:space:]]*:[[:space:]]*\"[^\"] ]]; then
        args_present=true
    fi
fi

# Claude Code namespaces plugin skills, so a bare name may be the user's own
# skill; count only `posthog:<bundled skill>`.
[[ "$name" =~ ^posthog:([a-zA-Z0-9_-]+)$ ]] || exit 0
skill="${BASH_REMATCH[1]}"
[[ -d "$ROOT/skills/$skill" ]] || exit 0

# permission_mode is a short enum (default/acceptEdits/plan/...).
permission_mode=""
if [[ "$input" =~ \"permission_mode\"[[:space:]]*:[[:space:]]*\"([a-zA-Z]+)\" ]]; then
    permission_mode="${BASH_REMATCH[1]}"
fi

plugin_version="unknown"
if [[ "$(cat "$ROOT/.claude-plugin/plugin.json" 2>/dev/null)" =~ \"version\"[[:space:]]*:[[:space:]]*\"([^\"]+)\" ]]; then
    plugin_version="${BASH_REMATCH[1]//[^A-Za-z0-9.+-]/}"
fi

os="$(uname -s 2>/dev/null)"
os="${os//[^A-Za-z0-9._-]/}"

# Stable anonymous per-install id (UUID). No PII — deliberately not git email.
data_dir="${CLAUDE_PLUGIN_DATA:-$HOME/.claude}"
id_file="$data_dir/posthog-plugin-telemetry-id"
distinct_id="$(tr -d '[:space:]' 2>/dev/null < "$id_file")"
if [[ ! "$distinct_id" =~ ^[A-Za-z0-9-]+$ ]]; then
    distinct_id="$(uuidgen 2>/dev/null || cat /proc/sys/kernel/random/uuid 2>/dev/null)"
    distinct_id="${distinct_id//[^A-Za-z0-9-]/}"
    [[ -n "$distinct_id" ]] || distinct_id="anon-${RANDOM}${RANDOM}-$$"
    mkdir -p "$data_dir" 2>/dev/null && printf '%s\n' "$distinct_id" > "$id_file" 2>/dev/null
fi

# shellcheck disable=SC2016 # `$`-prefixed PostHog property names, not expansions.
payload="$(printf '{"api_key":"%s","event":"plugin skill invoked","distinct_id":"%s","properties":{"skill":"%s","invocation":"%s","args_present":%s,"plugin_version":"%s","permission_mode":"%s","os":"%s","$lib":"posthog-ai-plugin","$process_person_profile":false,"$geoip_disable":true,"$ip":"127.0.0.1"}}' \
    "$API_KEY" "$distinct_id" "$skill" "$invocation" "$args_present" "$plugin_version" "$permission_mode" "$os")"

# Fire-and-forget: background, detached fds, 3s cap → ~0 user-facing latency.
curl -sf -m 3 -X POST "$HOST/i/v0/e/" \
    -H 'Content-Type: application/json' \
    -d "$payload" >/dev/null 2>&1 </dev/null &
disown 2>/dev/null || true

exit 0
