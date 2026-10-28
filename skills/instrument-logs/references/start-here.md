> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Getting started with Logs

Canonical URL: https://posthog.com/docs/logs/start-here

## On this page

- [Use your logging client](#use-your-logging-client)
- [Send context-rich logs](#send-context-rich-logs)
- [Search and analyze your logs](#search-and-analyze-your-logs)
- [Analyze log patterns](#analyze-log-patterns)
- [Set up alerts](#set-up-alerts)
- [Use MCP and AI to debug](#use-mcp-and-ai-to-debug)
- [Integrate your product data](#integrate-your-product-data)
- [Use for free](#use-for-free)
- [TL;DR 💸](#tldr-)

## Use your logging client

PostHog Logs works with any OpenTelemetry client. No PostHog-specific packages required. Use the OTel SDKs you already have, point them at PostHog's HTTP endpoint, and drop in your project token.

On the frontend, our [JavaScript web SDK](https://posthog.com/docs/logs/installation/javascript.md), [React Native SDK](https://posthog.com/docs/logs/installation/react-native.md), [iOS SDK](https://posthog.com/docs/logs/installation/ios.md), and [Android SDK](https://posthog.com/docs/logs/installation/android.md) include first-class logging support.

Follow the guides below to set up your logging client:

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/nodejs.svg)Node.js](https://posthog.com/docs/logs/installation/nodejs.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/nodejs.svg)Pino](https://posthog.com/docs/logs/installation/pino.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/nodejs.svg)Winston](https://posthog.com/docs/logs/installation/winston.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/python.svg)Python](https://posthog.com/docs/logs/installation/python.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/go.svg)Go](https://posthog.com/docs/logs/installation/go.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/java.svg)Java](https://posthog.com/docs/logs/installation/java.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/dotnet_logo_7e446176f2.svg).NET](https://posthog.com/docs/logs/installation/dotnet.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/rust.svg)Rust](https://posthog.com/docs/logs/installation/rust.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/frameworks/nextjs.svg)Next.js](https://posthog.com/docs/logs/installation/nextjs.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/js.svg)JavaScript web](https://posthog.com/docs/logs/installation/javascript.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/react.svg)React Native](https://posthog.com/docs/logs/installation/react-native.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/ios.svg)iOS](https://posthog.com/docs/logs/installation/ios.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/Android_robot_bec2fb7318.svg)Android](https://posthog.com/docs/logs/installation/android.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/flutter.svg)Flutter](https://posthog.com/docs/logs/installation/flutter.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/rails_581d31c82d.svg)Ruby on Rails](https://posthog.com/docs/logs/installation/ruby-on-rails.md)

-   [Datadog](https://posthog.com/docs/logs/installation/datadog.md)

-   [Other languages](https://posthog.com/docs/logs/installation/other.md)

[Configure logging client](https://posthog.com/docs/logs/installation.md)

## Send context-rich logs

PostHog ingests logs in the same pattern as OTel's structured logging model: resource attributes, log attributes, and trace context.

Enrich your logs with granular detail and business context for `INFO`, `DEBUG`, `WARN`, and `ERROR` log levels.

```python
import logging

# Configure logging to use OpenTelemetry
logging.basicConfig(level=logging.INFO)
logging.getLogger().addHandler(LoggingHandler())

# Use standard Python logging
logger = logging.getLogger("my-app")
logger.info("User action", extra={"userId": "123", "action": "login"})
logger.warning("Deprecated API used", extra={"endpoint": "/old-api"})
logger.error("Database connection failed", extra={"error": "Connection timeout"})
```

[Learn best practices](https://posthog.com/docs/logs/best-practices.md)

## Search and analyze your logs

Once your logs are flowing into PostHog, you can:

-   **Search through logs** using full-text searches, multiple search tokens, and negative filters
-   **Filter by time ranges** to find specific events
-   **Filter on attributes** for specific resources or events
-   **Correlate logs with events** from your PostHog analytics

![PostHog Logs search interface](https://res.cloudinary.com/dmukukwp6/image/upload/w_1600,c_limit,q_auto,f_auto/logs_light_dd81ff5093.png)

[Learn how to search logs](https://posthog.com/docs/logs/search.md)

## Analyze log patterns

The Patterns view automatically mines your logs to find recurring message templates. Use it to spot noisy log lines consuming your log budget, find new error shapes by their template structure, and see which patterns dominate your log volume.

Expand any pattern and click **View matching logs** to pivot to the Logs view filtered to lines matching that template. The filter lands in the filter bar as a visible, removable chip, and your date range, service, and severity selections carry over.

[Explore log patterns](https://posthog.com/docs/logs/patterns.md)

## Set up alerts

Get notified when your logs match specific conditions. Create alerts to:

-   **Monitor error spikes** — Alert when error log counts exceed a threshold
-   **Track specific services** — Watch for issues in critical services
-   **Filter by attributes** — Set up granular alerts based on log attributes

Configure alerting rules in your project settings to stay on top of issues as they happen.

[Configure log alerts](https://posthog.com/docs/logs/alerts.md)

## Use MCP and AI to debug

Connect the PostHog MCP server and your AI agent can query logs directly. Use Cursor, Claude Code, or any MCP-compatible tool.

Your coding agent pulls the relevant logs it needs to debug and build faster without switching workflows.

Try asking your agent for these:

-   `Show me error logs from the API service in the last hour`
-   `What services are logging errors right now?`
-   `Compare log patterns from today against yesterday and show me what's new`

In the web app, you can also open a single log record and have [PostHog AI explain it](https://posthog.com/docs/logs/explain-logs-ai.md) – what it means, what probably caused it, and what to do next.

[Explore logs with AI](https://posthog.com/docs/logs/surfaces/mcp.md)

## Integrate your product data

With PostHog, your logs live alongside your [Product Analytics](https://posthog.com/docs/product-analytics.md), [Session Replays](https://posthog.com/docs/session-replay.md), [Error Tracking](https://posthog.com/docs/error-tracking.md), and [Dashboards](https://posthog.com/docs/product-analytics/dashboards.md), so you can go from a log line to a user's session to the flag variant they were on without switching tools.

### Session Replay

Log events in PostHog can be connected to the session and user who triggered them. Jump from a log line to a session replay in one click.

![logs and errors](https://res.cloudinary.com/dmukukwp6/image/upload/q_auto,f_auto/SCR_20260427_tlab_c79adf4315.png)

### Product Analytics

Turn log patterns into trends, funnels, and retention insights. Know which logged errors actually hurt user retention vs. which are just noise.

![logs and product analytics](https://res.cloudinary.com/dmukukwp6/image/upload/q_auto,f_auto/SCR_20260427_twkv_8d5e77b42d.png)

### Error Tracking

Logs with `$exception` events become issues you can assign, resolve, and alert on. No separate error tracking tool needed.

![logs and session replay](https://res.cloudinary.com/dmukukwp6/image/upload/q_auto,f_auto/SCR_20260427_tpic_6c27c8b1e0.png)

### Dashboards

Add a Recent logs [widget](https://posthog.com/docs/product-analytics/dashboards.md#adding-widgets) to any dashboard to monitor log entries alongside your other metrics and insights. Filter by severity level and service, and click a row to jump to that log on the Logs page.

## Use for free

PostHog's Logs is built to be cost-effective by default, with a generous free tier and transparent usage-based pricing. Since we don't charge per seat, more than 90% of companies use PostHog for free.

## TL;DR 💸

-   No credit card required to start
-   First 10 GB of ingested logs per month are free
-   Above 10 GB we have usage-based pricing at $0.25/GB with discounts
-   All logs are retained 14 days by default. Set custom retention per service or per source for $0.05/GB per month retained – see [logs pricing](https://posthog.com/docs/logs/pricing.md#retention) for more details
-   Set billing limits to avoid surprise charges (they don't cap custom retention)
-   See our [pricing page](https://posthog.com/docs/logs/pricing.md) for more up-to-date details

---

That's it! You're ready to start integrating.

[Install logs](https://posthog.com/docs/logs/installation.md)

1/8

[**Use your logging client** ***Required***](#quest-item-use-your-logging-client)[**Send context-rich logs** ***Required***](#quest-item-send-context-rich-logs)[**Search and analyze your logs** ***Required***](#quest-item-search-and-analyze-your-logs)[**Analyze log patterns** ***Recommended***](#quest-item-analyze-log-patterns)[**Set up alerts** ***Recommended***](#quest-item-set-up-alerts)[**Use MCP and AI to debug** ***Recommended***](#quest-item-use-mcp-and-ai-to-debug)[**Integrate your product data** ***Recommended***](#quest-item-integrate-your-product-data)[**Use for free** ***Free 10 GB/mo***](#quest-item-use-for-free)

**Use your logging client**

***Required***
