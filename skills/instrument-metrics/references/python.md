> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Python metrics installation

Canonical URL: https://posthog.com/docs/metrics/installation/python

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.i.posthog.com` instead of `https://us.i.posthog.com` (ingestion host), and use `https://eu.posthog.com` instead of `https://app.posthog.com` (app host for links).

## On this page

- [Install posthog-python](#install-posthog-python)
- [Initialize the client](#initialize-the-client)
- [Record metrics](#record-metrics)
- [Instrument alongside existing metrics](#instrument-alongside-existing-metrics)
- [Flush before exit](#flush-before-exit)
- [Test your setup](#test-your-setup)
- [Next steps](#next-steps)

> **Note:** Metrics is in open alpha. Any team can turn it on — open [Metrics](https://app.posthog.com/metrics) and select **Enable metrics** in the onboarding view. Setup details may change before general availability.

The [posthog-python](https://posthog.com/docs/libraries/python.md) SDK includes the `posthog.metrics` API, so you can record metrics with the same client you use for events and feature flags.

1.  1

    ## Install posthog-python

    Required

    ```bash
    pip install posthog
    ```

    Metrics requires an up-to-date SDK version, so upgrade if you're on an older release.

2.  2

    ## Initialize the client

    Required

    Set a service name so metrics from different systems stay easy to tell apart. It's attached to every series and used by the Metrics UI for filtering.

    ```python
    from posthog import Posthog
    
    posthog = Posthog(
        "<ph_project_token>",
        host="https://us.i.posthog.com",
        metrics={"service_name": "billing-worker"},
    )
    ```

    Use your **project token** (the same one you use for capturing events), not a [personal API key](https://posthog.com/docs/api.md#authentication).

3.  3

    ## Record metrics

    Required

    Use the metric type that matches what you're measuring:

    ```python
    # Counters only go up: things you count
    posthog.metrics.count("invoices.processed", 1, attributes={"plan": "pro"})
    
    # Gauges go up and down: current values
    posthog.metrics.gauge("queue.depth", 42)
    
    # Histograms record distributions: durations, sizes
    posthog.metrics.histogram("job.duration", 187, unit="ms")
    ```

    The client is thread-safe and pre-aggregates: samples fold into per-series aggregates in memory and flush as one OTLP data point per series every few seconds, so recording in hot paths is cheap. A burst of 10k `count()` calls costs one data point on the wire.

    Keep attribute values small and bounded: `route`, `status`, and `plan` are good attributes; user IDs, session IDs, and request IDs are not. Every unique combination creates a new series.

4.  4

    ## Instrument alongside existing metrics

    Optional

    If your service already records metrics with Prometheus, StatsD, or another system, don't rip it out. Add the PostHog call next to the existing one, reusing the same metric name and attributes, so both systems chart the same series while you evaluate.

5.  5

    ## Flush before exit

    Required

    For short-lived processes (cron jobs, CLIs, serverless functions), flush before exiting so the last aggregation window isn't lost:

    ```python
    posthog.metrics.flush()
    ```

6.  6

    ## Test your setup

    Recommended

    1.  Trigger the code path that records a metric
    2.  Open **Metrics** in the PostHog sidebar and pick your metric from the name picker
    3.  Data points should appear within a minute of sending

    [View your metrics in PostHog](https://app.posthog.com/metrics)

8.  ## Next steps

    Checkpoint

    *What you can do with your metrics*

    | Action | Description |
    | --- | --- |
    | **[Why you need metrics](https://posthog.com/docs/metrics/basics.md)** | What metrics show you that events and logs don't |
    | **[Getting started guide](https://posthog.com/docs/metrics/start-here.md)** | Pick the right metric type, add attributes carefully, and chart what matters |
    | **Group and filter** | Group by an attribute for one line per value, or filter with `key=value` chips |
    | **[How metrics works](https://posthog.com/docs/metrics/architecture.md)** | How metrics are ingested, stored, and queried |
    | **Query with SQL** | Every metric lands in the `posthog.metrics` table, queryable from the SQL tab |

    [Continue with the getting started guide](https://posthog.com/docs/metrics/start-here.md)
