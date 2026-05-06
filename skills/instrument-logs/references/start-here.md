# Getting started with Logs - Docs

## Use your logging client

PostHog Logs works with any OpenTelemetry client. No PostHog-specific packages required. Use the OTel SDKs you already have, point them at PostHog's HTTP endpoint, and drop in your project token.

On the frontend, our [JavaScript web SDK](/docs/logs/installation/javascript.md) and [React Native SDK](/docs/logs/installation/react-native.md) include first-class logging support.

Follow the guides below to set up your logging client:

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/nodejs.svg)Node.js](/docs/logs/installation/nodejs.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/python.svg)Python](/docs/logs/installation/python.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/go.svg)Go](/docs/logs/installation/go.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/java.svg)Java](/docs/logs/installation/java.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/frameworks/nextjs.svg)Next.js](/docs/logs/installation/nextjs.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/js.svg)JavaScript web](/docs/logs/installation/javascript.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/react.svg)React Native](/docs/logs/installation/react-native.md)

-   [Datadog](/docs/logs/installation/datadog.md)

-   [Other languages](/docs/logs/installation/other.md)

[Configure logging client](/docs/logs/installation.md)

## Send context-rich logs

PostHog ingests logs in the same pattern as OTel's structured logging model: resource attributes, log attributes, and trace context.

Enrich your logs with granular detail and business context for `INFO`, `DEBUG`, `WARN`, and `ERROR` log levels.

Python

PostHog AI

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

[Learn best practices](/docs/logs/best-practices.md)

## Search and analyze your logs

Once your logs are flowing into PostHog, you can:

-   **Search through logs** using full-text searches, multiple search tokens, and negative filters
-   **Filter by time ranges** to find specific events
-   **Filter on attributes** for specific resources or events
-   **Correlate logs with events** from your PostHog analytics

![PostHog Logs search interface](https://res.cloudinary.com/dmukukwp6/image/upload/w_1600,c_limit,q_auto,f_auto/logs_light_dd81ff5093.png)![PostHog Logs search interface](https://res.cloudinary.com/dmukukwp6/image/upload/w_1600,c_limit,q_auto,f_auto/logs_dark_d7135f1b22.png)

[Learn how to search logs](/docs/logs/search.md)

## Set up alerts

Get notified when your logs match specific conditions. Create alerts to:

-   **Monitor error spikes** — Alert when error log counts exceed a threshold
-   **Track specific services** — Watch for issues in critical services
-   **Filter by attributes** — Set up granular alerts based on log attributes

Configure alerting rules in your project settings to stay on top of issues as they happen.

[Configure log alerts](/docs/logs/alerts.md)

## Use MCP and AI to debug

Connect the PostHog MCP server and your AI agent can query logs directly. Use Cursor, Claude Code, or any MCP-compatible tool.

Your coding agent pulls the relevant logs it needs to debug and build faster without switching workflows.

You can also ask [PostHog AI](/docs/posthog-ai.md) to search and analyze your logs.

![PostHog AI logs](https://res.cloudinary.com/dmukukwp6/image/upload/q_auto,f_auto/SCR_20260427_shqt_e667a5a091.png)![PostHog AI logs](https://res.cloudinary.com/dmukukwp6/image/upload/q_auto,f_auto/SCR_20260427_shuk_901780b9f1.png)

Try out these prompts:

-   [`Show me error logs from the API service in the last hour`](https://app.posthog.com/#panel=max:Show%20me%20error%20logs%20from%20the%20API%20service%20in%20the%20last%20hour)
-   [`Find all logs related to authentication failures today`](https://app.posthog.com/#panel=max:Find%20all%20logs%20related%20to%20authentication%20failures%20today)
-   [`Show logs from the payment service around 2pm yesterday`](https://app.posthog.com/#panel=max:Show%20logs%20from%20the%20payment%20service%20around%202pm%20yesterday)

[Explore logs with AI](/docs/logs/debug-logs-mcp.md)

## Integrate your product data

With PostHog, your logs live alongside your [Product Analytics](/docs/product-analytics.md), [Session Replays](/docs/session-replay.md), and [Error Tracking](/docs/error-tracking.md), so you can go from a log line to a user's session to the flag variant they were on without switching tools.

### Session Replay

Log events in PostHog can be connected to the session and user who triggered them. Jump from a log line to a session replay in one click.

![logs and errors](https://res.cloudinary.com/dmukukwp6/image/upload/q_auto,f_auto/SCR_20260427_tlab_c79adf4315.png)![logs and errors](https://res.cloudinary.com/dmukukwp6/image/upload/q_auto,f_auto/SCR_20260427_tpbx_e2154c4155.png)

### Product Analytics

Turn log patterns into trends, funnels, and retention insights. Know which logged errors actually hurt user retention vs. which are just noise.

![logs and product analytics](https://res.cloudinary.com/dmukukwp6/image/upload/q_auto,f_auto/SCR_20260427_twkv_8d5e77b42d.png)![logs and product analytics](https://res.cloudinary.com/dmukukwp6/image/upload/q_auto,f_auto/SCR_20260427_twoz_4e12550875.png)

### Error Tracking

Logs with `$exception` events become issues you can assign, resolve, and alert on. No separate error tracking tool needed.

![logs and session replay](https://res.cloudinary.com/dmukukwp6/image/upload/q_auto,f_auto/SCR_20260427_tpic_6c27c8b1e0.png)![logs and session replay](https://res.cloudinary.com/dmukukwp6/image/upload/q_auto,f_auto/SCR_20260427_tlie_6ffdbd4369.png)

## Use for free

PostHog's Logs is built to be cost-effective by default, with a generous free tier and transparent usage-based pricing. Since we don't charge per seat, more than 90% of companies use PostHog for free.

## TL;DR 💸

-   No credit card required to start
-   First 50 GB of ingested logs per month are free
-   Above 50 GB we have usage-based pricing at $0.25/GB with discounts
-   Set billing limits to avoid surprise charges
-   See our [pricing page](/docs/logs/pricing.md) for more up-to-date details

---

That's it! You're ready to start integrating.

[Install logs](/docs/logs/installation.md)

1/7

[**Use your logging client** ***Required***](#quest-item-use-your-logging-client)[**Send context-rich logs** ***Required***](#quest-item-send-context-rich-logs)[**Search and analyze your logs** ***Required***](#quest-item-search-and-analyze-your-logs)[**Set up alerts** ***Recommended***](#quest-item-set-up-alerts)[**Use MCP and AI to debug** ***Recommended***](#quest-item-use-mcp-and-ai-to-debug)[**Integrate your product data** ***Recommended***](#quest-item-integrate-your-product-data)[**Use for free** ***Free 50 GB/mo***](#quest-item-use-for-free)

**Use your logging client**

***Required***

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better