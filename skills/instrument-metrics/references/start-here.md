> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Getting started with metrics

Canonical URL: https://posthog.com/docs/metrics/start-here

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.i.posthog.com` instead of `https://us.i.posthog.com` (ingestion host), and use `https://eu.posthog.com` instead of `https://app.posthog.com` (app host for links).

## On this page

- [Send your first metrics](#send-your-first-metrics)
- [Pick the right metric type](#pick-the-right-metric-type)
- [Add attributes, carefully](#add-attributes-carefully)
- [Verify metrics are arriving](#verify-metrics-are-arriving)
- [Chart what matters](#chart-what-matters)
- [Query with SQL or ask AI](#query-with-sql-or-ask-ai)

**Metrics is in open alpha**

Any team can turn on metrics: open [Metrics](https://app.posthog.com/metrics) in PostHog and select **Enable metrics** in the onboarding view. See [turn on metrics](https://posthog.com/docs/metrics.md#turn-on-metrics) for the full flow. Setup details, including the ingestion endpoint, may change before general availability. During the alpha, PostHog keeps metrics data for 30 days.

## Send your first metrics

There are three ways to get metrics into PostHog, and all take just a few minutes.

If [posthog-js](https://posthog.com/docs/libraries/js.md) is already running on your site, record metrics directly with the `posthog.metrics` API. No new packages, no extra authentication:

```javascript
posthog.metrics.count("checkout.completed");
posthog.metrics.gauge("cart.items", 3);
posthog.metrics.histogram("api.request.duration", 187, { unit: "ms" });
```

If you use OpenTelemetry anywhere else (backend services, infrastructure, an existing Collector), point your OTLP metrics exporter at PostHog. No PostHog packages are required:

```bash
OTEL_EXPORTER_OTLP_METRICS_ENDPOINT="https://us.i.posthog.com/i/v1/metrics"
OTEL_EXPORTER_OTLP_METRICS_HEADERS="Authorization=Bearer <ph_project_token>"
OTEL_SERVICE_NAME="my-app"
```

If you run **Kubernetes** and your pods already expose Prometheus metrics, install the PostHog metrics agent Helm chart to scrape and forward them automatically:

```bash
helm install posthog-metrics-agent oci://ghcr.io/posthog/charts/posthog-metrics-agent \
  --set posthog.apiKey=<ph_project_token>
```

`<ph_client_api_host>` and `<ph_project_token>` are filled in with your project's values when you're logged in. Use your **project token** (the same one you use for capturing events), not a [personal API key](https://posthog.com/docs/api.md#authentication).

For per-platform setup, including the `posthog.metrics` API in [Node.js](https://posthog.com/docs/metrics/installation/nodejs.md) and [Python](https://posthog.com/docs/metrics/installation/python.md), see the [installation guides](https://posthog.com/docs/metrics/installation.md).

## Pick the right metric type

Metrics come in three shapes, and picking the right one determines which aggregations make sense later:

-   **Counters** only go up: requests handled, jobs processed, errors raised. Chart them with `rate` or `increase`.
-   **Gauges** go up and down: queue depth, active connections, memory in use. Chart them with `avg`.
-   **Histograms** record distributions: request durations, payload sizes. Chart them with percentiles like `p95`.

Give each metric a stable, descriptive name (`http.server.duration`, `jobs.processed.total`) and set a service name so metrics from different systems stay easy to tell apart.

## Add attributes, carefully

Attributes let you slice a metric by dimension: route, status code, plan, region. Every unique combination of attribute values creates a new series, so attach dimensions with a small, bounded set of values.

Good attributes: `route`, `status`, `plan`, `queue`. Bad attributes: user IDs, session IDs, request IDs, timestamps. Each of those would create a series per user or per request, which makes charts unreadable and ingestion expensive.

If you need to know what happened for one specific user or request, that's a job for [logs](https://posthog.com/docs/logs.md) or [traces](https://posthog.com/docs/distributed-tracing.md), not metrics.

## Verify metrics are arriving

Open **Metrics** in the PostHog sidebar. The **Overview** tab shows your services, metric names, and active series over the last day, so you can confirm data is landing. In the **Viewer** tab, pick your metric from the name picker and you should see data points within a minute of sending. The viewer recommends an aggregation based on the metric's type, so a counter defaults to `increase` and a gauge to `avg`.

If nothing shows up, check that the endpoint ends in `/i/v1/metrics`, that the token starts with `phc_`, and see the [troubleshooting section](https://posthog.com/docs/metrics.md#troubleshooting).

## Chart what matters

Once data flows, build the views you'll actually watch:

-   **Group by** an attribute to get one line per value, for example request rate per route or queue depth per worker.
-   **Filter** with `key=value` chips to focus on one service, environment, or status.
-   Watch for the **anomaly badge** — when the metric moves against its baseline, it shows the change and the label values that drove it.
-   Turn on **auto-refresh** to update the chart every few seconds while you watch a deploy or an incident.

When a chart is worth keeping, **save it as an insight** or add it to a dashboard — or use **New service dashboard** to build one insight per metric in a single step.

## Query with SQL or ask AI

Every metric lands in the `posthog.metrics` table, so the **SQL** tab in the metrics viewer gives you full query access for anything the chart controls don't cover.

If you use the [PostHog MCP server](https://posthog.com/docs/model-context-protocol.md), your AI tools can query metrics directly: ask your agent to chart a metric, compare error rates between services, or characterize an anomaly, all without leaving your editor.

For the full tour of the viewer — anomaly detection, pivoting into logs and traces, and dashboards — see [Use your metrics](https://posthog.com/docs/metrics/explore.md).

1/6

[**Send your first metrics** ***Required***](#quest-item-send-your-first-metrics)[**Pick the right metric type** ***Required***](#quest-item-pick-the-right-metric-type)[**Add attributes, carefully** ***Required***](#quest-item-add-attributes-carefully)[**Verify metrics are arriving** ***Required***](#quest-item-verify-metrics-are-arriving)[**Chart what matters** ***Recommended***](#quest-item-chart-what-matters)[**Query with SQL or ask AI** ***Optional***](#quest-item-query-with-sql-or-ask-ai)

**Send your first metrics**

***Required***
