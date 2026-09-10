#!/usr/bin/env bash
# PostToolUse telemetry for the `Skill` tool — anonymous plugin usage analytics.
#
# Fires after a skill is invoked and, *only for this plugin's own skills*,
# sends a single "plugin skill invoked" event to a PostHog-owned project so the
# team can see which skills get used in the field. Captures the skill name plus
# safe metadata only — never the skill arguments or any free-text content.
#
# Privacy & consent:
#   - Anonymous: distinct_id is a random per-install UUID (no email, no PII),
#     and events set `$process_person_profile: false` so no person is created.
#   - Opt-out (on by default). Disable with either:
#         export DO_NOT_TRACK=1
#         export POSTHOG_PLUGIN_TELEMETRY_DISABLED=1
#   - Endpoint/key are overridable for testing via POSTHOG_PLUGIN_TELEMETRY_KEY
#     and POSTHOG_PLUGIN_TELEMETRY_HOST.
#
# Pure bash + curl; no jq or other third-party tools. Reads the hook JSON on
# stdin, sends in the background, and always exits 0 — losing a telemetry event
# is fine, interfering with the user's session is not.
#
# Scope: Claude Code only in practice. Codex injects skills as context (no Skill
# tool → no PostToolUse event), and Cursor/Gemini have no hooks, so the matcher
# simply never fires there. See https://developers.openai.com/codex/hooks

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
# No key configured (e.g. placeholder build) → no-op.
[[ -n "$API_KEY" && "$API_KEY" != "phc_REPLACE_ME" ]] || exit 0

# curl is required to send; if absent, no-op silently.
command -v curl >/dev/null 2>&1 || exit 0

# Plugin root: Claude Code sets CLAUDE_PLUGIN_ROOT, Codex sets PLUGIN_ROOT (plus
# a CLAUDE_PLUGIN_ROOT alias). Fall back to the script's parent dir.
ROOT="${CLAUDE_PLUGIN_ROOT:-${PLUGIN_ROOT:-}}"
if [[ -z "$ROOT" ]]; then
    ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." 2>/dev/null && pwd)"
fi

# Client label — forward-compatible; today only Claude Code fires this hook.
if [[ -n "${PLUGIN_ROOT:-}" ]]; then
    client="codex"
else
    client="claude-code"
fi

input="$(cat)"

# Only act on the Skill tool (the matcher should already guarantee this).
tool_name=""
if [[ "$input" =~ \"tool_name\"[[:space:]]*:[[:space:]]*\"([^\"]+)\" ]]; then
    tool_name="${BASH_REMATCH[1]}"
fi
[[ "$tool_name" == "Skill" ]] || exit 0

# Skill identifier lives in tool_input.skill, e.g. "posthog:creating-experiments"
# (verified against real transcripts). Names are [a-zA-Z0-9:_-]+, so a narrow
# regex on the raw payload is safe and matches the first (tool_input) occurrence,
# never anything inside the trailing tool_response.
skill=""
if [[ "$input" =~ \"skill\"[[:space:]]*:[[:space:]]*\"([a-zA-Z0-9:_-]+)\" ]]; then
    skill="${BASH_REMATCH[1]}"
fi
[[ -n "$skill" ]] || exit 0

# Split "namespace:name" → namespace + base name.
if [[ "$skill" == *:* ]]; then
    skill_namespace="${skill%%:*}"
    skill_name="${skill##*:}"
else
    skill_namespace=""
    skill_name="$skill"
fi

# Capture only THIS plugin's skills: the `posthog:` namespace, or a bare name
# that matches a bundled skill directory. Everything else is ignored.
if [[ "$skill_namespace" != "posthog" && ! -d "$ROOT/skills/$skill_name" ]]; then
    exit 0
fi

# Whether arguments were passed — presence only, never the content.
args_present=false
if [[ "$input" =~ \"args\"[[:space:]]*:[[:space:]]*\"[^\"]+\" ]]; then
    args_present=true
fi

# permission_mode is a short enum (default/acceptEdits/plan/...).
permission_mode=""
if [[ "$input" =~ \"permission_mode\"[[:space:]]*:[[:space:]]*\"([a-zA-Z]+)\" ]]; then
    permission_mode="${BASH_REMATCH[1]}"
fi

# Plugin version from the manifest.
plugin_version="unknown"
if [[ -f "$ROOT/.claude-plugin/plugin.json" ]]; then
    pj="$(cat "$ROOT/.claude-plugin/plugin.json" 2>/dev/null || true)"
    if [[ "$pj" =~ \"version\"[[:space:]]*:[[:space:]]*\"([^\"]+)\" ]]; then
        plugin_version="${BASH_REMATCH[1]}"
    fi
fi

os="$(uname -s 2>/dev/null || echo unknown)"

# Stable anonymous per-install id (UUID). Persisted under the plugin's writable
# data dir (Codex: PLUGIN_DATA) or ~/.claude. No PII — deliberately not git email.
data_dir="${CLAUDE_PLUGIN_DATA:-${PLUGIN_DATA:-$HOME/.claude}}"
id_file="$data_dir/posthog-plugin-telemetry-id"
distinct_id=""
[[ -f "$id_file" ]] && distinct_id="$(tr -d '[:space:]' < "$id_file" 2>/dev/null || true)"
if [[ -z "$distinct_id" ]]; then
    if command -v uuidgen >/dev/null 2>&1; then
        distinct_id="$(uuidgen 2>/dev/null || true)"
    elif [[ -r /proc/sys/kernel/random/uuid ]]; then
        distinct_id="$(cat /proc/sys/kernel/random/uuid 2>/dev/null || true)"
    fi
    [[ -z "$distinct_id" ]] && distinct_id="anon-${RANDOM}${RANDOM}-$$"
    distinct_id="$(printf '%s' "$distinct_id" | tr -d '[:space:]')"
    mkdir -p "$data_dir" 2>/dev/null && printf '%s\n' "$distinct_id" > "$id_file" 2>/dev/null || true
fi
[[ -n "$distinct_id" ]] || exit 0

# All interpolated values are constrained to safe charsets (slugs, enums, a
# UUID, a semver), so no JSON/shell escaping is required — same reasoning as
# gate-exec-write.sh.
payload="$(printf '{"api_key":"%s","event":"plugin skill invoked","distinct_id":"%s","properties":{"skill":"%s","skill_name":"%s","skill_namespace":"%s","args_present":%s,"plugin_version":"%s","client":"%s","permission_mode":"%s","os":"%s","$lib":"posthog-ai-plugin","$lib_version":"%s","$process_person_profile":false}}' \
    "$API_KEY" "$distinct_id" "$skill" "$skill_name" "$skill_namespace" "$args_present" "$plugin_version" "$client" "$permission_mode" "$os" "$plugin_version")"

# Fire-and-forget: background, detached fds, 3s cap → ~0 user-facing latency.
curl -sf -m 3 -X POST "$HOST/i/v0/e/" \
    -H 'Content-Type: application/json' \
    -d "$payload" >/dev/null 2>&1 </dev/null &
disown 2>/dev/null || true

exit 0
