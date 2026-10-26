"""Load the repository with the real Antigravity CLI, the way `agy plugin install` reads it.

Without a native manifest, agy converts `gemini-extension.json` instead, which runs MCP through
mcp-remote and copies the Claude Code hooks it cannot run. Skipped when `agy` is not on PATH.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
AGY = shutil.which("agy")

pytestmark = pytest.mark.skipif(AGY is None, reason="agy is not installed")


def _agy(home, *args):
    result = subprocess.run(
        [AGY, "plugin", *args], env={"HOME": str(home), "PATH": "/usr/bin:/bin"}, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout


def test_validate_finds_native_manifest_with_mcp_and_no_hooks(tmp_path):
    report = json.loads(_agy(tmp_path, "validate", str(REPO_ROOT), "--json"))
    assert (report["manifest"], report["components"]["mcpServers"], report["components"]["hooks"]) == (
        ".antigravity-plugin/plugin.json",
        1,
        0,
    )


def test_install_loads_as_native_plugin(tmp_path):
    _agy(tmp_path, "install", str(REPO_ROOT))
    (plugin,) = json.loads(_agy(tmp_path, "list", "--json"))
    assert plugin["source"] == "antigravity"
