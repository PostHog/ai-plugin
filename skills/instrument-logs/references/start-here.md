# Getting started with logs - Docs

> **New to logging?** Read [Why you need logs](/docs/logs/basics.md) first for a primer on what logs show you that nothing else does.

## Install and configure logging

PostHog logs is a powerful logging solution that works with the OpenTelemetry Protocol (OTLP). You don't need any vendor specific SDKs – just use standard OpenTelemetry libraries.

Install and configure your logging client to send logs to PostHog:

-   Use the HTTP endpoint: `https://us.i.posthog.com/i/v1/logs`
-   Authenticate with your project token (the same token used for events/exceptions)
-   Include the token in the Authorization header or as a `?token=` query parameter
-   Use the standard [OTLP log format](https://opentelemetry.io/docs/specs/otel/logs/data-model/)

[Configure your logging client](/docs/logs/installation.md)

## Search and analyze your logs

Once your logs are flowing into PostHog, you can:

-   **Search through logs** using multiple search tokens, negative filters, and exact phrase matching
-   **Filter by time ranges** to find specific events
-   **Correlate logs with events** from your PostHog analytics

Navigate to the Logs section in your PostHog dashboard to start exploring your log data.

[Learn how to search logs](/docs/logs/search.md)

## Troubleshooting

Common issues you might encounter when setting up logging:

-   **Authentication errors** - Make sure you're using your correct project token
-   **Connection issues** - Verify the HTTP endpoint is accessible
-   **Log format problems** - Ensure you're using the standard [OTLP log format](https://opentelemetry.io/docs/specs/otel/logs/data-model/)

[Troubleshoot common issues](/docs/logs/troubleshooting.md)

## Logging best practices

Learn what to log, how to structure your logs, and the patterns that make logs actually useful in production – including wide events, strategic sampling, and adding business context.

[Read the best practices guide](/docs/logs/best-practices.md)

1/4

[**Install and configure logging** ***Required***](#quest-item-install-and-configure-logging)[**Search and analyze your logs** ***Required***](#quest-item-search-and-analyze-your-logs)[**Troubleshooting** ***Recommended***](#quest-item-troubleshooting)[**Logging best practices** ***Recommended***](#quest-item-logging-best-practices)

**Install and configure logging**

***Required***

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better