# Releasing the PostHog AI plugin

Merging to `main` is not always enough. Some AI clients install the plugin straight from this repo. Others serve their own copy, and someone has to ask them to update it.

| Who | What they run | After a merge |
| --- | --- | --- |
| People who installed from this repo with the README's commands (Claude Code, Claude Cowork, Codex CLI, Gemini CLI, Antigravity, Grok) | This repo. They get a change when their client next updates the plugin. | Nothing |
| People who installed `posthog@claude-plugins-official` in Claude Code | A commit of this repo that Anthropic pins | [Ask Anthropic](#anthropics-claude-code-marketplace) |
| People who installed from Anthropic's directory on claude.ai | A commit of this repo that Anthropic reviewed | [Ask Anthropic](#anthropics-directory-on-claudeai) |
| People who installed from the Cursor Marketplace | Cursor's copy | [Email Cursor](#cursor) |

## Changing the plugin

1. If the change needs a PostHog MCP server change, ship the server change first.
2. Bump the version if people who already have the plugin need the change. Claude Code keeps an installed plugin on its version until the version changes.
   - Use a minor bump, such as 1.2.0 to 1.3.0, in every manifest that has a `version` and in `.claude-plugin/marketplace.json`.
   - Patch bumps belong to the daily sync job. See [`.github/PLUGIN_SYNC.md`](.github/PLUGIN_SYNC.md).
3. Update your branch from `main` right before you merge. The sync job changes the version lines, so an old branch conflicts.
4. Run `python3 -m pytest tests/test_plugin_paths.py`.
5. Merge, then update each copy below that needs the change.

## Anthropic's Claude Code marketplace

[`anthropics/claude-plugins-official`](https://github.com/anthropics/claude-plugins-official) pins the plugin to one commit of this repo. Their bot opens a PR to move the pin, and their staff merge it. PostHog cannot open or merge that PR.

1. Check [the pin](https://github.com/anthropics/claude-plugins-official/blob/main/.claude-plugin/marketplace.json) (search for `posthog`) and any [open bump PR](https://github.com/anthropics/claude-plugins-official/pulls?q=is%3Apr+is%3Aopen+posthog).
2. If the pin is behind, ask in `#ext-posthog-anthropic` (PostHog Slack). Give the commit you want.
3. If an old bump PR is still open, ask them to close it. Their bot does not open a new one while an old one is open.
4. Done when the pin shows your commit.

## Anthropic's directory on claude.ai

The directory on claude.ai is a second, separate listing. It serves claude.ai and Claude Cowork, and reaches Claude Code through account sync. It has its own reviewed commit, which does not follow the marketplace pin above.

1. Check the version on the plugin's page in claude.ai.
2. If it is behind, ask in `#ext-posthog-anthropic` (PostHog Slack).

To do: Anthropic's docs describe a [developer portal](https://claude.com/docs/plugins/submit) where the owner of a listing publishes new versions from a branch. Find out whether PostHog can manage this listing there.

## Cursor

The Cursor Marketplace serves its own copy and re-indexes it on request.

1. Email `marketplace-publishing@cursor.com` with the plugin name (PostHog), the repo (`PostHog/ai-plugin`) and the commit. Ask for a re-index.
2. Done when they confirm.

To do: we are asking Cursor whether the listing can update automatically. Not decided yet.

## Not this plugin: the PostHog listing in ChatGPT and Codex

OpenAI's plugin directory also lists PostHog. That listing is not this plugin. It is a small bundle that points ChatGPT and Codex at the PostHog MCP server, uploaded by hand on OpenAI's platform. Nothing in this repo feeds it, and a merge here never changes it.

Codex users who follow the README install this plugin from this repo. That is a different thing from the directory listing.

The steps are here because the listing has no repo of its own. Use them only when the listing itself changes, such as its description, logo or MCP server URL. Questions go to `#ext-posthog-openai` (PostHog Slack).

1. On OpenAI's platform, open Plugins, then PostHog, and download the zip of the published version.
2. Unzip it, make the change, and raise `version` in the zip's own `.codex-plugin/plugin.json`. Do not copy files from this repo into it.
3. Zip it from a terminal so the hidden files are included: `zip -r posthog-<version>.zip .codex-plugin .mcp.json assets`.
4. Select "Create draft from ZIP" and upload it.
5. Select "Submit for review" and wait for "Approved". Version 2.0.3 took one night.
6. Select "Publish plugin". Approval does not publish.
7. Install it in ChatGPT or Codex and ask one PostHog question.
