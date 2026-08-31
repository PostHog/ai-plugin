import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_codex_windows_skips_the_bash_only_pre_tool_gate():
    config = json.loads((ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    handler = config["hooks"]["PreToolUse"][0]["hooks"][0]

    assert handler["commandWindows"] == "cmd /d /c exit 0"
