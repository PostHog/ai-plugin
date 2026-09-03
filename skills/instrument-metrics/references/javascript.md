> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# JavaScript (web) metrics installation - Docs

Copy page

# JavaScript (web) metrics installation - Docs

> **Note:** Metrics is in alpha. Setup details may change before general availability.

If [posthog-js](/docs/libraries/js.md) is already running on your site, you can record metrics directly with the `posthog.metrics` API. No new packages, no extra authentication.

1.  1

    ## Install posthog-js

    Required

    If you haven't already, [install posthog-js](/docs/libraries/js.md#installation) via the snippet or npm and initialize it with your project token. Metrics requires an up-to-date SDK version, so upgrade if you're on an older release.

    There is no metrics-specific setup required: the metrics API authenticates with the same project token the SDK already uses. Optionally, set a service name so your metrics are easy to find and filter:

    JavaScript

    PostHog AI

    ```javascript
    posthog.init('<ph_project_api_key>', {
        api_host: 'https://us.i.posthog.com',
        metrics: {
            serviceName: 'storefront-web',
            environment: 'production',
        },
    })
    ```

2.  2

    ## Record metrics

    Required

    Use the metric type that matches what you're measuring:

    JavaScript

    PostHog AI

    ```javascript
    // Counters only go up: things you count
    posthog.metrics.count('checkout.completed')
    // Gauges go up and down: current values
    posthog.metrics.gauge('cart.items', 3)
    // Histograms record distributions: durations, sizes
    posthog.metrics.histogram('api.request.duration', 187, { unit: 'ms' })
    ```

    Add attributes to slice a metric by dimension, keeping the set of values small and bounded:

    JavaScript

    PostHog AI

    ```javascript
    posthog.metrics.count('checkout.completed', 1, { attributes: { plan: 'pro' } })
    ```

    Good attributes: `route`, `status`, `plan`. Bad attributes: user IDs, session IDs, request IDs. Every unique combination of attribute values creates a new series, so high-cardinality dimensions belong in [logs](/docs/logs.md) or [traces](/docs/distributed-tracing.md), not metrics.

    Samples aggregate in memory and flush as one data point per series every few seconds, so recording in hot paths is cheap.

3.  3

    ## Instrument alongside existing metrics

    Optional

    If your app already records metrics with another system, don't rip it out. Add the PostHog call next to the existing one, reusing the same metric name and attributes, so both systems chart the same series while you evaluate.

4.  4

    ## Test your setup

    Recommended

    1.  Trigger the code path that records a metric
    2.  Open **Metrics** in the PostHog sidebar and pick your metric from the name picker
    3.  Data points should appear within a minute of sending

    [View your metrics in PostHog](https://app.posthog.com/metrics)

6.  ## Next steps

    Checkpoint

    *What you can do with your metrics*

    | Action | Description |
    | --- | --- |
    | [Why you need metrics](/docs/metrics/basics.md) | What metrics show you that events and logs don't |
    | [Getting started guide](/docs/metrics/start-here.md) | Pick the right metric type, add attributes carefully, and chart what matters |
    | Group and filter | Group by an attribute for one line per value, or filter with key=value chips |
    | [How metrics works](/docs/metrics/architecture.md) | How metrics are ingested, stored, and queried |
    | Query with SQL | Every metric lands in the posthog.metrics table, queryable from the SQL tab |

    [Continue with the getting started guide](/docs/metrics/start-here.md)

### Still have questions?

Ask PostHog AI

### Was this page useful?

HelpfulCould be better