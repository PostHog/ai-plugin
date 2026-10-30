# PostHog AI plugin

Official PostHog plugin for AI clients. Access PostHog products directly from your AI coding tool.

## Installation

### Claude Code

1. Install the plugin:
    ```bash
    claude plugin install posthog
    ```

    Or install from this repo as a marketplace:
    ```bash
    claude plugin marketplace add PostHog/ai-plugin
    claude plugin install posthog@posthog
    ```

2. Authenticate via OAuth:
    ```bash
    # Just enter Claude Code anywhere
    claude
    # Then, use the /mcp command within Claude, select plugin:posthog:posthog, and press Enter
    /mcp
    ```
    Then follow the browser prompts to log into PostHog.

3. (Optional) Send Claude Code sessions to PostHog LLM Analytics.

    Add to `~/.claude/settings.json` (global) or `.claude/settings.local.json` (per-project):
    ```json
    {
      "env": {
        "POSTHOG_LLMA_CC_ENABLED": "true",
        "POSTHOG_API_KEY": "phc_...",
        "POSTHOG_HOST": "https://eu.i.posthog.com"
      }
    }
    ```

    Both `POSTHOG_LLMA_CC_ENABLED=true` and `POSTHOG_API_KEY` are required. Sessions are sent when Claude Code exits. Set `POSTHOG_LLMA_PRIVACY_MODE=true` to redact prompt/output content. Add custom properties to all events with `POSTHOG_LLMA_CUSTOM_PROPERTIES` (JSON string, e.g. `'{"ai_product": "my-app"}'`). Set `POSTHOG_AI_PURPOSE` to declare what the session is doing relative to the repo — documented values are `authoring` and `review`, emitted as `$ai_purpose`. Useful when a harness wraps an agent it can't modify (e.g. a CI job running Claude Code as a reviewer); left unset the property is omitted.

#### Session capture without the rest of the plugin

To send Claude Code sessions to PostHog LLM analytics without the skills, the slash commands, or the MCP server, install the capture plugin on its own:

```bash
claude plugin marketplace add PostHog/ai-plugin
claude plugin install posthog-telemetry@posthog
```

It registers one `SessionEnd` hook and nothing else, so it adds nothing to the context of a session. It needs only the Python standard library, and it reads the same environment variables as step 3 above.

Install it instead of the `posthog` plugin, not alongside it. Both register the same hook, so running both parses and uploads every session twice. PostHog dedupes the events themselves, because their UUIDs are derived from the session, but the two hooks race on the status file.

### Cursor

Install from the [Cursor Marketplace](https://cursor.com/marketplace) or add manually in Cursor Settings > Plugins.

The plugin installs the PostHog skills and the MCP server. Claude Code's session capture and the write-command gate don't run in Cursor.

In Cursor IDE, the MCP connection runs through Cursor's hosted service, so Cursor holds your PostHog sign-in and you may need to sign in again after updating the plugin.

Grok Bot (desktop and mobile) lists the same plugin from the Cursor Marketplace. Open **Plugins**, search for **PostHog**, install it, and log into PostHog when prompted.

### Codex

1. Add the marketplace:
    ```bash
    codex plugin marketplace add PostHog/ai-plugin
    ```

2. Install the plugin from inside Codex:
    ```
    codex
    # Then run /plugins, select PostHog, and install
    /plugins
    ```

3. Trust the plugin's hook when Codex asks you to review it at startup, or later from `/hooks`. The hook approves known PostHog reads (`tools`, `search`, `info` and the other read-only `exec` commands, and calls to tools on `hooks/read-tools.txt`) so they run without a prompt. Every other call, including every write, gets Codex's own approval prompt. The `POSTHOG_MCP_EXEC_GATE_*` variables don't apply on Codex. Codex asks before every PostHog call until you trust the hook, and again after each plugin update until you re-trust it. The one exception is `render-ui`, which shows a PostHog chart or view in the conversation and never changes data, so it always runs without a prompt.

    A few Codex settings change this:

    - A `[mcp_servers.posthog]` entry in your own `~/.codex/config.toml` replaces the plugin's server config entirely, including the prompt mode the gate relies on. Remove it, or add `default_tools_approval_mode = "prompt"` and a `[mcp_servers.posthog.tools.render-ui]` table with `approval_mode = "approve"` to it.
    - With approval policy `never` and full access (`--dangerously-bypass-approvals-and-sandbox`), Codex approves MCP calls before the hook runs, so nothing is gated.
    - With approval policy `never` and a restricted sandbox, calls the hook doesn't approve are denied instead of prompted.

### Antigravity

1. Install the plugin:
    ```bash
    agy plugin install https://github.com/PostHog/ai-plugin
    ```

2. Authenticate via OAuth: run `/mcp`, select `posthog_posthog`, and choose **Authenticate**. Open the link it shows, log into PostHog, and paste the authorization code back into Antigravity.

The plugin installs the PostHog skills and the MCP server. Claude Code's session capture and the write-command gate don't run in Antigravity.

### Gemini CLI

```bash
gemini extensions install https://github.com/PostHog/ai-plugin
```

### Grok

1. Install the plugin:
    ```bash
    grok plugin install PostHog/ai-plugin --trust
    ```

2. Authenticate via OAuth:

    On first use of a PostHog tool, Grok prompts you to authorize in your browser. Log into PostHog to connect.

### Claude Cowork

1. Add the marketplace: open **Settings** > **Plugins**, click **Add** > **Add marketplace**, enter `PostHog/ai-plugin`, and click **Sync**.

2. Install the plugin: click **Browse**, select **PostHog**, and install. The plugin stays in sync with this repo automatically.

3. Authenticate via OAuth: on first use of a PostHog tool, follow the browser prompts to log into PostHog.

## How to develop

1. Clone and install the plugin:
    ```bash
    git clone https://github.com/PostHog/ai-plugin
    claude --plugin-dir ./ai-plugin
    ```

2. Authenticate via OAuth:
    ```
    /mcp
    ```
    Then follow the browser prompts to log into PostHog.

## Features

This plugin provides access to 27+ PostHog tools across these categories:

- **Feature flags** - Create, update, and manage feature flags
- **Experiments** - Run and analyze A/B tests
- **Insights** - Query analytics and create visualizations
- **Dashboards** - Manage dashboards and add insights
- **Error tracking** - View and debug errors
- **LLM analytics** - Track AI/LLM costs and usage
- **Documentation** - Search PostHog docs
- And more

### Bundled skills

The plugin also ships 30+ task-specific skills that your AI client loads on demand to follow PostHog best practices — covering HogQL query patterns, experiment creation and lifecycle, feature flags, data warehouse setup and troubleshooting, LLM analytics exploration, session replay diagnostics, and SDK instrumentation. Skills activate automatically when their description matches your request (e.g. "create an experiment", "why isn't my Stripe sync working?", "audit my feature flags"), so you generally don't need to invoke them by name.

### Write gate

A `PreToolUse` hook (`hooks/gate-exec-write.sh`) asks for approval before the PostHog MCP `exec` tool runs a sensitive write, such as a feature-flag change or any delete or destroy. It also asks for:

- `posthog-connection-call` and `posthog-connection-forward`, whatever `POSTHOG_MCP_EXEC_GATE_ALLOW` and `POSTHOG_MCP_EXEC_GATE_DENY` say;
- an `exec` input with more than one `command` field;
- a `command` whose check fails to evaluate.

Outside the Codex approval hook (below), the script passes silently, leaving the normal permission flow, for a `tool_name` it cannot read, a missing or `null` `command`, and a verb other than `call` (such as `tools` or `search`). Known reads, third-party gateway tools and writes outside the default set pass silently too.

In Claude Code's `bypassPermissions` mode (a top-level `permission_mode` of exactly that value) the hook never asks.

On Codex the `PreToolUse` hook is skipped. The Codex approval hook (`hooks/codex-hooks.json`, `hooks/codex-gate-exec-write.sh`) stays active: it approves only known reads, ignores `permission_mode` and the variables below, and leaves every other command to Codex's own prompt.

Three environment variables tune the Claude Code hook:

- `POSTHOG_MCP_EXEC_GATE_DISABLE`: set to a non-empty value other than `0` to turn the gate off, connection calls included. `0` leaves the gate on.
- `POSTHOG_MCP_EXEC_GATE_DENY`: comma-separated globs of PostHog tool names that prompt. Overrides the default set; `*` prompts on every write. Tools in `hooks/read-tools.txt` never prompt, and connection calls prompt whatever it says.
- `POSTHOG_MCP_EXEC_GATE_ALLOW`: comma-separated globs of tools that never prompt. Wins over the deny set, except that connection calls still prompt.

For example, `POSTHOG_MCP_EXEC_GATE_ALLOW="annotation-create"`. See `hooks/gate-exec-write.sh` for the default set.

## Example usage

```
> What feature flags do I have?
> Create a feature flag called new-onboarding for 50% of users

> Show me errors from the last 24 hours
> Which errors are affecting the most users?

> How many users signed up this week?
> What's the conversion rate for the checkout funnel?

> Show me all my experiments
> What are the results of the checkout-flow experiment?

> Create a new dashboard called Product Metrics
> Add the signup funnel insight to the Growth dashboard

> What are the responses to the NPS survey?
> Create a feedback survey for the checkout page

> What's my most triggered event?
> Show me the top 10 pages by pageviews
```

## Plugin usage telemetry

In Claude Code, the plugin sends one anonymous `plugin skill invoked` event to PostHog Cloud each time one of this plugin's skills runs, whether Claude invokes it or you type `/posthog:<skill>`. Skills from other plugins and your own skills aren't counted. Each event contains only:

- `skill`: the skill's name, such as `querying-posthog-data`
- `invocation`: `model` when Claude invoked the skill, `user` when you typed it as a slash command
- `args_present`: whether the skill was invoked with arguments, never the arguments themselves
- `plugin_version`: the installed plugin version
- `permission_mode`: Claude Code's permission mode, such as `default` or `plan`
- `os`: the operating system name from `uname -s`, such as `Darwin` or `Linux`
- `distinct_id`: a random UUID generated once per install and stored in the plugin's data directory
- `$lib`: always `posthog-ai-plugin`
- `$process_person_profile`, `$geoip_disable`, and `$ip`: fixed values (`false`, `true`, and `127.0.0.1`) so PostHog creates no person profile and runs no GeoIP lookup, and the stored event carries no client IP address. The request still reaches PostHog's capture endpoint from your IP, as any HTTPS request does

No event is sent when `POSTHOG_MCP_URL` or `POSTHOG_HOST` points anywhere other than `posthog.com`, so self-hosted users don't report to PostHog Cloud. Like Claude Code's own telemetry, it's also off when Claude Code runs on Amazon Bedrock, Google Cloud's Agent Platform, Microsoft Foundry, or Claude Platform on AWS (`CLAUDE_CODE_USE_BEDROCK`, `CLAUDE_CODE_USE_VERTEX`, `CLAUDE_CODE_USE_FOUNDRY`, or `CLAUDE_CODE_USE_ANTHROPIC_AWS` set to `1`, `true`, `yes`, or `on`). To turn it off, set any of these in your shell or the `env` block of `~/.claude/settings.json`:

```bash
export DO_NOT_TRACK=1
export POSTHOG_PLUGIN_TELEMETRY_DISABLED=1
export DISABLE_TELEMETRY=1
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
```

`DO_NOT_TRACK` and `DISABLE_TELEMETRY` turn off Claude Code's own telemetry too, and `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` turns off all of Claude Code's nonessential traffic. `POSTHOG_PLUGIN_TELEMETRY_DISABLED` turns off only this plugin's telemetry.

## Self-hosted

For self-hosted PostHog instances, set the `POSTHOG_MCP_URL` environment variable to point to your instance:

```bash
export POSTHOG_MCP_URL="https://mcp.your-posthog-instance.com/mcp"
```

## Documentation

- [PostHog MCP documentation](https://posthog.com/docs/model-context-protocol)
- [PostHog API documentation](https://posthog.com/docs/api)

## License

MIT
