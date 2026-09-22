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
    hooks_file = plugin_root / "hooks" / "hooks.json"
    if not hooks_file.is_file():
        pytest.skip(f"{name} ships no hooks.json")

    referenced = [
        (command, match)
        for command in _hook_commands(hooks_file)
        for match in PLUGIN_ROOT_REF.findall(command)
    ]
    assert referenced, f"{hooks_file} references no script"

    for command, relative in referenced:
        target = plugin_root / relative.lstrip("/")
        assert target.is_file(), f"{hooks_file}: {command} points at missing {target}"


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


def test_marketplace_sources_are_plugins():
    marketplace = json.loads((REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text())
    for entry in marketplace["plugins"]:
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
