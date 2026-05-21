#!/usr/bin/env python3
"""Launch a Claude Code session against the local (or a remote-branch)
build of this plugin, with the marketplace plugin disabled so SessionEnd
doesn't double-fire.

Examples:
    scripts/dev_test_session.py
        # Load this repo at its current checkout via --plugin-dir.

    scripts/dev_test_session.py --branch fix/claude-code-ingest-bugs
        # Load the branch zip from GitHub via --plugin-url.

    scripts/dev_test_session.py --cwd ~/some/other/project
        # Run the session in a different working dir (useful for testing
        # path-mangling cases like worktrees, spaces, underscores, dots).

The marketplace plugin (posthog@claude-plugins-official) is disabled at
session start and re-enabled in a finally block, so an interrupted run
still restores it. Re-running while it's already disabled is harmless.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

MARKETPLACE_PLUGIN = "posthog@claude-plugins-official"
REPO_ROOT = Path(__file__).resolve().parent.parent
REQUIRED_ENV = ("POSTHOG_LLMA_CC_ENABLED", "POSTHOG_API_KEY")


def _git_branch(cwd: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd, text=True, stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "(unknown)"


def _warn_missing_env(target_cwd: Path) -> None:
    """Warn if the env vars the hook needs aren't visible in this shell
    AND aren't present in the target cwd's .claude/settings*.json. The
    hook will silently no-op without these — easy to miss."""
    shell_missing = [k for k in REQUIRED_ENV if not os.environ.get(k)]
    if not shell_missing:
        return

    found_in_settings = set()
    for fname in ("settings.json", "settings.local.json"):
        path = target_cwd / ".claude" / fname
        if path.is_file():
            text = path.read_text(errors="ignore")
            for k in shell_missing:
                if f'"{k}"' in text:
                    found_in_settings.add(k)

    still_missing = [k for k in shell_missing if k not in found_in_settings]
    if still_missing:
        print(
            f"warning: {', '.join(still_missing)} not set in this shell "
            f"and not found in {target_cwd}/.claude/settings*.json — "
            f"the SessionEnd hook will silently no-op.",
            file=sys.stderr,
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--branch",
        help="Load a remote branch zip via --plugin-url instead of the local repo.",
    )
    parser.add_argument(
        "--repo", default="PostHog/ai-plugin",
        help="owner/repo for --branch (default: PostHog/ai-plugin).",
    )
    parser.add_argument(
        "--cwd", default=os.getcwd(),
        help="Working dir to launch claude in (default: current).",
    )
    parser.add_argument(
        "--skip-disable", action="store_true",
        help="Don't disable the marketplace plugin. Causes duplicate "
             "SessionEnd events; only use if you're isolating something else.",
    )
    parser.add_argument(
        "claude_args", nargs=argparse.REMAINDER,
        help="Extra args passed through to `claude` (prefix with --).",
    )
    args = parser.parse_args()

    target_cwd = Path(args.cwd).expanduser().resolve()
    if not target_cwd.is_dir():
        print(f"error: --cwd not a directory: {target_cwd}", file=sys.stderr)
        return 2

    if args.branch:
        url = f"https://github.com/{args.repo}/archive/refs/heads/{args.branch}.zip"
        plugin_args = ["--plugin-url", url]
        print(f"plugin source: remote — {args.repo}@{args.branch}")
        print(f"               {url}")
    else:
        plugin_args = ["--plugin-dir", str(REPO_ROOT)]
        print(f"plugin source: local  — {REPO_ROOT}")
        print(f"               branch: {_git_branch(REPO_ROOT)}")

    print(f"cwd:           {target_cwd}")
    _warn_missing_env(target_cwd)

    disabled = False
    if not args.skip_disable:
        print(f"disabling {MARKETPLACE_PLUGIN} for this session...")
        result = subprocess.run(
            ["claude", "plugin", "disable", MARKETPLACE_PLUGIN],
            capture_output=True, text=True,
        )
        # `disable` returns 0 even if already disabled, so accept that.
        disabled = result.returncode == 0
        if not disabled:
            print(f"warning: disable failed:\n{result.stderr}", file=sys.stderr)

    # Pass-through extra claude args; REMAINDER includes the leading "--"
    # if the user used one, so strip it.
    extra = args.claude_args
    if extra and extra[0] == "--":
        extra = extra[1:]

    try:
        cmd = ["claude", *plugin_args, *extra]
        print(f"launching:     {' '.join(cmd)}\n")
        rc = subprocess.run(cmd, cwd=str(target_cwd)).returncode
    finally:
        if disabled:
            print(f"\nre-enabling {MARKETPLACE_PLUGIN}...")
            subprocess.run(
                ["claude", "plugin", "enable", MARKETPLACE_PLUGIN],
                capture_output=True,
            )

    return rc


if __name__ == "__main__":
    sys.exit(main())
