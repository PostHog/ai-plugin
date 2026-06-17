# PostHog AI plugin

Official PostHog plugin for AI clients. Access PostHog products directly from your AI coding tool.

## Installation

### Claude Code

1. Install the plugin:
    ```bash
    claude plugin install posthog
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

    Both `POSTHOG_LLMA_CC_ENABLED=true` and `POSTHOG_API_KEY` are required. Sessions are sent when Claude Code exits. Set `POSTHOG_LLMA_PRIVACY_MODE=true` to redact prompt/output content. Add custom properties to all events with `POSTHOG_LLMA_CUSTOM_PROPERTIES` (JSON string, e.g. `'{"ai_product": "my-app"}'`).

### Cursor

Install from the [Cursor Marketplace](https://cursor.com/marketplace) or add manually in Cursor Settings > Plugins.

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
