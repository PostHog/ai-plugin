"""Every path a manifest hands to Claude Code must resolve to a real file.

Manifests reference scripts through `${CLAUDE_PLUGIN_ROOT}`, which differs per
plugin, and `claude plugin validate` checks manifest schema only. Moving a file
without updating a manifest is therefore silent until a session ends.
"""

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT_REF = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT(?::-\$PLUGIN_ROOT)?\}(/[^\"'\s]+)")

# Every directory Claude Code can install on its own, and so every root that
# `${CLAUDE_PLUGIN_ROOT}` can expand to.
PLUGIN_ROOTS = [("posthog", REPO_ROOT), ("posthog-telemetry", REPO_ROOT / "telemetry")]


def _hooks_files(plugin_root):
    # Claude Code loads hooks/hooks.json and merges in whatever the manifest's `hooks` names.
    declared = json.loads((plugin_root / ".claude-plugin" / "plugin.json").read_text()).get("hooks", [])
    paths = [declared] if isinstance(declared, str) else declared
    candidates = [plugin_root / "hooks" / "hooks.json"] + [plugin_root / path for path in paths]
    return [path for path in candidates if path.is_file()]


def _hook_commands(hooks_file):
    for entries in json.loads(hooks_file.read_text())["hooks"].values():
        for entry in entries:
            for hook in entry.get("hooks", []):
                if "command" in hook:
                    yield hook["command"]


@pytest.mark.parametrize("name,plugin_root", PLUGIN_ROOTS, ids=[n for n, _ in PLUGIN_ROOTS])
def test_plugin_manifest_is_present(name, plugin_root):
    manifest = plugin_root / ".claude-plugin" / "plugin.json"
    assert manifest.is_file()
    assert json.loads(manifest.read_text())["name"] == name


@pytest.mark.parametrize("name,plugin_root", PLUGIN_ROOTS, ids=[n for n, _ in PLUGIN_ROOTS])
def test_hook_commands_resolve(name, plugin_root):
    hooks_files = _hooks_files(plugin_root)
    if not hooks_files:
        pytest.skip(f"{name} ships no hooks")

    for hooks_file in hooks_files:
        referenced = [
            (command, match)
            for command in _hook_commands(hooks_file)
            for match in PLUGIN_ROOT_REF.findall(command)
        ]
        assert referenced, f"{hooks_file} references no script"

        for command, relative in referenced:
            target = plugin_root / relative.lstrip("/")
            assert target.is_file(), f"{hooks_file}: {command} points at missing {target}"


@pytest.mark.parametrize("name,plugin_root", PLUGIN_ROOTS, ids=[n for n, _ in PLUGIN_ROOTS])
def test_hook_commands_quote_plugin_root(name, plugin_root):
    # Claude Code runs hook commands through a shell, so an unquoted path splits on a space in the plugin root.
    hooks_files = _hooks_files(plugin_root)
    if not hooks_files:
        pytest.skip(f"{name} ships no hooks")

    for hooks_file in hooks_files:
        for command in _hook_commands(hooks_file):
            for match in PLUGIN_ROOT_REF.finditer(command):
                quoted = command[match.start() - 1 : match.start()] == '"' and command[match.end() : match.end() + 1] == '"'
                assert quoted, f"{hooks_file}: {command} leaves {match.group(0)} unquoted"


HOOK_EVENTS_CLAUDE_CODE_2_1_75_ACCEPTS = {
    "PreToolUse",
    "PostToolUse",
    "PostToolUseFailure",
    "Notification",
    "UserPromptSubmit",
    "SessionStart",
    "SessionEnd",
    "Stop",
    "SubagentStart",
    "SubagentStop",
    "PreCompact",
    "PermissionRequest",
    "Setup",
    "TeammateIdle",
    "TaskCompleted",
    "Elicitation",
    "ElicitationResult",
    "ConfigChange",
    "WorktreeCreate",
    "WorktreeRemove",
    "InstructionsLoaded",
}


@pytest.mark.parametrize("name,plugin_root", PLUGIN_ROOTS, ids=[n for n, _ in PLUGIN_ROOTS])
def test_default_hooks_load_on_old_clients(name, plugin_root):
    hooks_file = plugin_root / "hooks" / "hooks.json"
    if not hooks_file.is_file():
        pytest.skip(f"{name} ships no hooks.json")

    rejected = set(json.loads(hooks_file.read_text())["hooks"]) - HOOK_EVENTS_CLAUDE_CODE_2_1_75_ACCEPTS
    assert not rejected, (
        f"{hooks_file}: {sorted(rejected)} makes Claude Code 2.1.75 drop every hook in the file, "
        "including the exec write gate. Declare newer events in a separate file named by the manifest's `hooks`."
    )


@pytest.mark.parametrize(
    "command_file",
    sorted((REPO_ROOT / "commands").glob("*.md")) + sorted((REPO_ROOT / "commands").glob("*.toml")),
    ids=lambda p: p.name,
)
def test_command_files_resolve(command_file):
    # Commands ship with the root plugin only, so their root is the repository.
    for relative in PLUGIN_ROOT_REF.findall(command_file.read_text()):
        target = REPO_ROOT / relative.lstrip("/")
        assert target.is_file(), f"{command_file}: points at missing {target}"


MARKETPLACE_ENTRY_KEYS_CLAUDE_CODE_2_1_75_ACCEPTS = {
    "name",
    "source",
    "description",
    "version",
    "author",
    "homepage",
    "repository",
    "license",
    "category",
    "keywords",
}


def test_marketplace_entries_load_on_old_clients_and_point_at_plugins():
    marketplace = json.loads((REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text())
    for entry in marketplace["plugins"]:
        rejected_keys = set(entry) - MARKETPLACE_ENTRY_KEYS_CLAUDE_CODE_2_1_75_ACCEPTS
        assert not rejected_keys, (
            f"{entry['name']}: {sorted(rejected_keys)} makes `claude plugin marketplace add` fail "
            "on Claude Code 2.1.75 and older, which reject the whole marketplace with "
            "`Invalid schema: Unrecognized key`"
        )
        source = entry["source"]
        assert isinstance(source, str), f"{entry['name']}: only local sources are checked here"
        manifest = (REPO_ROOT / source) / ".claude-plugin" / "plugin.json"
        assert manifest.is_file(), f"{entry['name']}: source {source} has no plugin manifest"
        assert json.loads(manifest.read_text())["name"] == entry["name"]


def test_marketplace_versions_match_manifests():
    marketplace = json.loads((REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text())
    for entry in marketplace["plugins"]:
        manifest = json.loads(((REPO_ROOT / entry["source"]) / ".claude-plugin" / "plugin.json").read_text())
        assert entry["version"] == manifest["version"], (
            f"{entry['name']}: marketplace says {entry['version']}, manifest says {manifest['version']}. "
            "An install pins the version, so a stale entry never reaches existing users."
        )


def test_antigravity_mcp_server_matches_claude_code():
    # Antigravity reads mcp_config.json and names the URL field serverUrl, so it is a second copy of .mcp.json.
    claude_code = json.loads((REPO_ROOT / ".mcp.json").read_text())["mcpServers"]["posthog"]
    antigravity = json.loads((REPO_ROOT / "mcp_config.json").read_text())["mcpServers"]["posthog"]
    assert (antigravity["serverUrl"], antigravity["headers"]) == (claude_code["url"], claude_code["headers"])


def test_cursor_mcp_server_matches_claude_code():
    claude_code = json.loads((REPO_ROOT / ".mcp.json").read_text())["mcpServers"]["posthog"]
    cursor = json.loads((REPO_ROOT / "mcp.json").read_text())["mcpServers"]["posthog"]
    assert (cursor["url"], cursor["headers"]) == (claude_code["url"], claude_code["headers"])


def test_cursor_mcp_server_is_hosted():
    # Grok Bot only connects to MCP servers placed on Cursor's hosted side; without it the plugin installs but never offers sign-in.
    cursor = json.loads((REPO_ROOT / "mcp.json").read_text())["mcpServers"]["posthog"]
    assert cursor.get("placement") == "server"


def test_codex_mcp_server_matches_claude_code():
    # Codex reads codex-mcp.json, a copy of .mcp.json plus the approval mode its exec gate relies on.
    # Codex's server config only reads `http_headers`; it silently drops `headers`.
    claude_code = json.loads((REPO_ROOT / ".mcp.json").read_text())["mcpServers"]["posthog"]
    codex = json.loads((REPO_ROOT / "codex-mcp.json").read_text())["mcpServers"]["posthog"]
    expected = {k: v for k, v in claude_code.items() if k != "headers"}
    expected |= {"http_headers": claude_code["headers"], "default_tools_approval_mode": "prompt"}
    assert codex == expected


# Cursor runs hooks/hooks.json, but the gate never matches its `MCP:exec` tool name, Cursor does not
# enforce the gate's "ask", and the session hook parses Claude Code transcripts, so Cursor gets none.
def test_cursor_gets_no_claude_code_hooks():
    manifest = json.loads((REPO_ROOT / ".cursor-plugin" / "plugin.json").read_text())
    assert json.loads((REPO_ROOT / manifest["hooks"]).read_text())["hooks"] == {}


def test_codex_gets_only_its_exec_gate():
    manifest = json.loads((REPO_ROOT / ".codex-plugin" / "plugin.json").read_text())
    hooks_file = REPO_ROOT / manifest["hooks"]
    assert list(json.loads(hooks_file.read_text())["hooks"]) == ["PermissionRequest"]
    assert list(_hook_commands(hooks_file)) == ['"${PLUGIN_ROOT}/hooks/codex-gate-exec-write.sh"']
    assert (REPO_ROOT / "hooks" / "codex-gate-exec-write.sh").is_file()


def test_cursor_manifest_paths_exist():
    manifest = json.loads((REPO_ROOT / ".cursor-plugin" / "plugin.json").read_text())
    paths = [manifest[key] for key in ("skills", "agents", "hooks", "mcpServers")]
    missing = [path for path in paths if not (REPO_ROOT / path).exists()]
    assert missing == []
