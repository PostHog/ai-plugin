> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Other languages metrics installation - Docs

Copy page

# Other languages metrics installation - Docs

> **Note:** Metrics is in alpha. Setup details, including the ingestion endpoint, may change before general availability.

PostHog's application metrics work with any OpenTelemetry-compatible client. If your app or infrastructure already exports OTLP metrics, point the exporter at PostHog. No PostHog packages required.

1.  1

    ## Install OpenTelemetry packages

    Required

    The key requirements are:

    -   Use OTLP (OpenTelemetry Protocol) for metrics export over HTTP
    -   Send metrics to your Metrics endpoint (see configuration step below)
    -   Include your project token in the Authorization header or as a `?token=` query parameter

    Find the OpenTelemetry SDK for your language in the [official registry](https://opentelemetry.io/ecosystem/registry/). If you already run an OpenTelemetry Collector, you can add PostHog as an additional exporter without touching application code.

2.  2

    ## Get your project token

    Required

    You'll need your PostHog project token to authenticate metrics requests. This is the same key you use for capturing events and exceptions with the PostHog SDK.

    > **Important:** Use your **project token** which starts with `phc_`. Do **not** use a personal API key (which starts with `phx_`).

    You can find your project token in [Project Settings](https://app.posthog.com/settings).

3.  3

    ## Configure the exporter

    Required

    Most OpenTelemetry SDKs pick up standard environment variables, so configuration is often no more than:

    Terminal

    PostHog AI

    ```bash
    OTEL_EXPORTER_OTLP_METRICS_ENDPOINT="https://us.i.posthog.com/i/v1/metrics"
    OTEL_EXPORTER_OTLP_METRICS_HEADERS="Authorization=Bearer <ph_project_token>"
    OTEL_SERVICE_NAME="my-app"
    ```

    Set `OTEL_SERVICE_NAME` so metrics from different systems stay easy to tell apart. It's attached to every series and used by the Metrics UI for filtering.

    If you configure the exporter in code instead:

    **Endpoint:**

    PostHog AI

    ```
    https://us.i.posthog.com/i/v1/metrics
    ```

    **Authentication:** Include your project token either as an `Authorization` header:

    PostHog AI

    ```
    Authorization: Bearer <ph_project_token>
    ```

    Or as a query parameter on the endpoint:

    PostHog AI

    ```
    https://us.i.posthog.com/i/v1/metrics?token=<ph_project_token>
    ```

4.  4

    ## Test your setup

    Recommended

    1.  Trigger the code path that records a metric
    2.  Open **Metrics** in the PostHog sidebar and pick your metric from the name picker
    3.  Data points should appear within a minute of sending

    If nothing shows up, check that the endpoint ends in `/i/v1/metrics`, that the token starts with `phc_`, and see the [troubleshooting section](/docs/metrics.md#troubleshooting).

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