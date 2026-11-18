# Releasing the PostHog AI plugin

A merge to `main` reaches some people and not others. Three companies keep their own copy of the plugin, and each one updates it in a different way.

This page has:

- [Who gets a merge, and who needs a person](#who-gets-a-merge-and-who-needs-a-person)
- Runbooks:
  - [Ship a change in this repo](#runbook-ship-a-change-in-this-repo)
  - [Update Anthropic's copy](#runbook-update-anthropics-copy)
  - [Update Cursor's copy](#runbook-update-cursors-copy)
  - [Release the ChatGPT and Codex directory plugin](#runbook-release-the-chatgpt-and-codex-directory-plugin)
  - [Change the consumer header](#runbook-change-the-consumer-header)
- [Check a release](#check-a-release)
- [Contacts](#contacts)

## Who gets a merge, and who needs a person

| Where people install from | Gets a merge to `main`? | What to do |
| --- | --- | --- |
| This repo: Claude Code (`posthog@posthog`), Claude Cowork, Codex CLI, Gemini CLI, Antigravity, Grok | Yes | Nothing. See the note on versions below. |
| Anthropic's marketplace (`claude plugin install posthog`) | No. It is pinned to a commit of this repo. | [Update Anthropic's copy](#runbook-update-anthropics-copy) |
| The plugin listing in claude.ai | No. Anthropic holds a separate copy. | [Update Anthropic's copy](#runbook-update-anthropics-copy) |
| Cursor Marketplace, which Grok Bot also lists | No. Cursor serves a copy and re-indexes it on request. | [Update Cursor's copy](#runbook-update-cursors-copy) |
| ChatGPT and Codex plugin directory | No. It is a separate zip, not built from this repo. | [Release the directory plugin](#runbook-release-the-chatgpt-and-codex-directory-plugin) |

**Versions.** Claude Code keeps an installed plugin on its version until the version changes. So a change with no version bump reaches new installs, and reaches existing Claude Code installs only at the next bump. The daily sync job bumps the patch version when its generated files change. [`.github/PLUGIN_SYNC.md`](.github/PLUGIN_SYNC.md) describes that job.

## Runbook: ship a change in this repo

1. If the change depends on the PostHog MCP server, merge the server change first and confirm it is live in production.
2. Decide on a version bump. Bump when existing installs need the change now.
   - Use a minor version, such as 1.2.0 to 1.3.0. The sync job owns patch versions.
   - Set the same version in `.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`, `.codex-plugin/plugin.json` and `gemini-extension.json`, and in the `posthog` entry of `.claude-plugin/marketplace.json`.
3. Update the branch from `main` right before you merge. The sync job commits version lines to `main`, so an older branch conflicts on them.
4. Run `python3 -m pytest tests/test_plugin_paths.py` and `claude plugin validate .`.
5. Merge.
6. Work through the runbooks below for each copy that needs the change.
7. [Check the release](#check-a-release).

## Runbook: update Anthropic's copy

**How it works**

- [`anthropics/claude-plugins-official`](https://github.com/anthropics/claude-plugins-official) pins the plugin to one commit of this repo, in [`.claude-plugin/marketplace.json`](https://github.com/anthropics/claude-plugins-official/blob/main/.claude-plugin/marketplace.json).
- A bot there opens a bump PR each night when this repo has moved. Anthropic staff merge it.
- The bot skips a plugin that already has an open bump PR. One stale PR blocks every later bump.
- That repo closes PRs from outside Anthropic, so PostHog cannot open the bump.
- The plugin listing in claude.ai is a second copy. It does not follow the pin, and nothing public shows its source.

**Steps**

1. Read the pin: search for `posthog` in the marketplace file above and note `source.sha`.
2. Look for an [open bump PR](https://github.com/anthropics/claude-plugins-official/pulls?q=is%3Apr+is%3Aopen+posthog).
3. Ask Anthropic ([Contacts](#contacts)). Give them the current pin, the commit you want, and the number of the open bump PR. If that PR points at an old commit, ask them to close it so the bot opens a new one.
4. Ask in the same message for the claude.ai listing to be updated.
5. Done when `source.sha` is the commit you asked for.

Anthropic's developer portal can list a plugin from a branch it follows, with no bump PR ([their docs](https://claude.com/docs/plugins/submit)). In November 2026 this plugin was not set up that way.

## Runbook: update Cursor's copy

**How it works**

- The Cursor Marketplace serves a copy of this repo. It does not follow `main`.
- Cursor re-indexes the copy when asked by email.

**Steps**

1. Email `marketplace-publishing@cursor.com`. Give the plugin name (PostHog), the repo (`PostHog/ai-plugin`) and the commit. Ask for a re-index.
2. Done when Cursor's reply confirms it, and the [release check](#check-a-release) shows Cursor on the new version.

Ask for real releases, not for every patch bump from the sync job.

## Runbook: release the ChatGPT and Codex directory plugin

**How it works**

- The PostHog plugin in OpenAI's directory is a zip uploaded on OpenAI's platform. It is not built from this repo, and a merge here does not change it.
- The zip holds `.codex-plugin/plugin.json`, `.mcp.json` and `assets/`.
- This is not the Codex CLI install in the README. That one reads this repo.

**Steps**

1. On OpenAI's platform, open Plugins, then PostHog, and download the zip of the published version.
2. Unzip it and make the change. Raise `version` in `.codex-plugin/plugin.json`.
3. Check that `.mcp.json` holds the server URL and nothing else. No keys, no tokens.
4. Zip it from a terminal, so the hidden files are included: `zip -r posthog-<version>.zip .codex-plugin .mcp.json assets`. Finder hides files that start with a dot.
5. Select "Create draft from ZIP" and upload it.
6. Read the findings on the draft. The submit dialog says which ones do not block.
7. Select "Submit for review" and wait for the version to show "Approved". Version 2.0.3 took one night.
8. Select "Publish plugin". Approval does not publish.
9. Install the plugin in ChatGPT or Codex and ask one PostHog question.

OpenAI also scans the MCP server's tools. A tool with a finding stays unpublished until someone selects "Request manual review" for it on the plugin page.

## Runbook: change the consumer header

Every client config in this repo sends the header `x-posthog-mcp-consumer`. The MCP server reads it to tell which plugin a call comes from, and it serves skills through `learn` based on the value. The value today is `plugin-learn`.

Change it rarely. A wrong change signs people out.

**Why Claude Code is different**

- Claude Code ties a saved PostHog sign-in to the `type`, `url` and `headers` in `.mcp.json`. Changing any of them signs every Claude Code user out.
- So `.mcp.json` keeps the old value, `plugin`, and never changes.
- The real value is in `claude-code-headers.json`. Claude Code reads it through `headersHelper`, which is not part of the sign-in.
- If the helper fails, Claude Code sends `plugin` and shows no error.

**Steps**

1. Merge the MCP server change that handles the new value first.
2. Change the value in `claude-code-headers.json` (Claude Code), `mcp.json` (Cursor), `codex-mcp.json` (Codex), `mcp_config.json` (Antigravity) and `gemini-extension.json` (Gemini CLI).
3. Change `CONSUMER_HEADERS` in `tests/test_plugin_paths.py`. The tests fail until every file matches.
4. Leave `.mcp.json` alone. A test fails if its sign-in fields change.
5. Sign in with a real PostHog account in at least one client other than Claude Code, before and after the change. Clients differ on whether a new value needs a new sign-in.
6. The `claude-code` CI job installs the plugin with the real CLI on Linux, macOS and Windows and checks the header a server receives. It must pass.

## Check a release

- In the MCP server's events, split tool calls by the `x-posthog-mcp-consumer` value and by client. The new value should appear for each client you released to.
- Ask an agent on the new plugin to load a skill. `learn` should answer.

## Contacts

For PostHog staff.

| Who | Where |
| --- | --- |
| Anthropic | `#ext-posthog-anthropic` in PostHog's Slack |
| Cursor | `marketplace-publishing@cursor.com` |
| OpenAI | `#ext-posthog-openai` in PostHog's Slack |
