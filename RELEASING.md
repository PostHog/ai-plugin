# Releasing the PostHog AI plugin

How a change in this repo reaches people, and what to do by hand. Written after the 1.2.0 release in November 2026.

## What this repo ships

- One plugin, with a manifest for each client: Claude Code, Cursor, Codex, Gemini CLI and Antigravity.
- No skills. The PostHog MCP server serves skills on demand through `learn`, and `tests/test_plugin_paths.py` fails if a skill is added here.
- A second plugin, `posthog-telemetry`, with its own version.

## Where each client gets the plugin

Merging to `main` is not a release for everyone. Four listings hold their own copy.

| Client | Source | How a release reaches it |
| --- | --- | --- |
| Claude Code, Anthropic's marketplace | `anthropics/claude-plugins-official`, pinned to a commit of this repo | A bot opens a bump PR there and Anthropic merges it. The bot skips a plugin that already has an open bump PR, so a stale one blocks later bumps. Ask in `#ext-posthog-anthropic`. |
| claude.ai plugin listing | A copy that Anthropic holds | Ask in `#ext-posthog-anthropic`. In November 2026 it was older than the marketplace pin. |
| Cursor Marketplace | A copy that Cursor indexes from this repo | Email `marketplace-publishing@cursor.com` with the plugin name, the repo and the commit, and ask for a re-index. |
| ChatGPT and Codex directory plugin | A zip uploaded on OpenAI's plugin page. Not built from this repo. | See [ChatGPT and Codex directory plugin](#chatgpt-and-codex-directory-plugin). |
| Claude Code with this repo added as a marketplace, Codex, Gemini CLI, Antigravity | This repo | No listing to update. People install from the repo. |

## The daily sync job

`.github/workflows/sync-plugin-files.yml` runs every day at 12:00 UTC and on demand. [`.github/PLUGIN_SYNC.md`](.github/PLUGIN_SYNC.md) covers its setup.

- When something changed, it bumps the patch version in every manifest and opens a PR that merges itself once the checks pass.
- Run it by hand: `gh workflow run sync-plugin-files.yml --repo PostHog/ai-plugin --ref main`.

## Releasing a change by hand

1. If the change depends on the MCP server, land the server change first and confirm it is live in production.
2. Bring the branch up to date with `main` right before the merge. The sync job commits to `main`, so an older branch conflicts on the version lines.
3. Keep every client manifest on the same version, and keep `.claude-plugin/marketplace.json` equal to the manifests. `tests/test_plugin_paths.py` checks both.
4. Use a minor version for a hand-made release, so it is not a patch number the sync job also produces.
5. Run `python3 -m pytest tests/test_plugin_paths.py` and `claude plugin validate .`.
6. Merge, then run the sync job by hand and watch its PR merge.
7. Ask each listing that holds its own copy to update (table above).

## Rules that are easy to break

- **Claude Code header.** Claude Code ties a saved PostHog sign-in to the static headers in `.mcp.json`. A changed static header signs the user out. Keep the static `plugin` value there, and send any new value through `headersHelper` and `claude-code-headers.json`.
- **The helper must work on every OS.** The `claude-code` CI job installs the plugin with the real CLI on Linux, macOS and Windows and checks the header a server receives.
- **A broken helper fails silently.** Claude Code falls back to the static header with no error, so the server sees the old value.
- **Other clients** send the consumer value directly. Test a real sign-in when a header value changes.
- **Cursor needs `"placement": "server"`** in `mcp.json`. `tests/test_plugin_paths.py` checks it.

## ChatGPT and Codex directory plugin

- The listing is a zip: `.codex-plugin/plugin.json`, `.mcp.json` and assets. Download the current version from OpenAI's plugin page before you change it.
- A new version is four steps on that page: "Create draft from ZIP", "Submit for review", wait for "Approved", then "Publish plugin". Approval does not publish. The last click is manual.
- The review of 2.0.3 took one night.
- A finding on the draft can be non-blocking. The submit dialog lists which ones are.
- OpenAI also scans the MCP server's tools. A tool definition with a finding stays unpublished until "Request manual review" is pressed on the plugin page.
- Questions go to `#ext-posthog-openai`.

## After a release

- Check the MCP server's events for the `x-posthog-mcp-consumer` value the new plugin sends, by client.
- Check that `learn` still serves skills in production.
