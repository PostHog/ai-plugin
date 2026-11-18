# Releasing the PostHog AI plugin

Merging to `main` is not always enough. Some AI clients install the plugin straight from this repo. Others serve their own copy, and someone has to ask them to update it.

| Who | Updates on its own? | After a merge |
| --- | --- | --- |
| People who installed from this repo with the README's commands (Claude Code, Claude Cowork, Codex CLI, Gemini CLI, Antigravity, Grok) | Yes | Nothing |
| People who installed from Anthropic's plugin directory (`claude plugin install posthog`) | No | [Ask Anthropic](#anthropic) |
| People who installed from the Cursor Marketplace | No | [Email Cursor](#cursor) |
| People who installed from OpenAI's plugin directory (ChatGPT and Codex) | No | [Upload a new zip](#openai-chatgpt-and-codex) |

## Changing the plugin

1. If the change needs a PostHog MCP server change, ship the server change first.
2. Bump the version if people who already have the plugin need the change. An installed plugin only updates when its version changes.
   - Use a minor bump, such as 1.2.0 to 1.3.0, in every manifest that has a `version` and in `.claude-plugin/marketplace.json`.
   - Patch bumps belong to the daily sync job. See [`.github/PLUGIN_SYNC.md`](.github/PLUGIN_SYNC.md).
3. Update your branch from `main` right before you merge. The sync job changes the version lines, so an old branch conflicts.
4. Run `python3 -m pytest tests/test_plugin_paths.py`.
5. Merge, then update each copy below that needs the change.

## Anthropic

Anthropic's directory pins the plugin to one commit of this repo. Their bot opens a PR to move the pin, and their staff merge it. PostHog cannot open or merge that PR.

1. Check [the pin](https://github.com/anthropics/claude-plugins-official/blob/main/.claude-plugin/marketplace.json) (search for `posthog`) and any [open bump PR](https://github.com/anthropics/claude-plugins-official/pulls?q=is%3Apr+is%3Aopen+posthog).
2. If the pin is behind, ask in `#ext-posthog-anthropic` (PostHog Slack). Give the commit you want.
3. If an old bump PR is still open, ask them to close it. Their bot does not open a new one while an old one is open.
4. Done when the pin shows your commit.

## Cursor

The Cursor Marketplace serves its own copy and re-indexes it on request.

1. Email `marketplace-publishing@cursor.com` with the plugin name (PostHog), the repo (`PostHog/ai-plugin`) and the commit. Ask for a re-index.
2. Done when they confirm.

Ask for real releases, not for every patch bump.

## OpenAI (ChatGPT and Codex)

The plugin in OpenAI's directory is a zip uploaded on OpenAI's platform. It is not built from this repo, so a merge here does not change it. Questions go to `#ext-posthog-openai` (PostHog Slack).

1. On OpenAI's platform, open Plugins, then PostHog, and download the zip of the published version.
2. Unzip it, make the change, and raise `version` in `.codex-plugin/plugin.json`.
3. Zip it from a terminal so the hidden files are included: `zip -r posthog-<version>.zip .codex-plugin .mcp.json assets`.
4. Select "Create draft from ZIP" and upload it.
5. Select "Submit for review" and wait for "Approved". Version 2.0.3 took one night.
6. Select "Publish plugin". Approval does not publish.
7. Install it in ChatGPT or Codex and ask one PostHog question.
