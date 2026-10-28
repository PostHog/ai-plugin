> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Getting started with distributed tracing

Canonical URL: https://posthog.com/docs/distributed-tracing/start-here

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.i.posthog.com` instead of `https://us.i.posthog.com` (ingestion host).

## On this page

- [Install a trace exporter](#install-a-trace-exporter)
- [Send context-rich spans](#send-context-rich-spans)
- [Explore your traces](#explore-your-traces)
- [Part of PostHog's observability suite](#part-of-posthogs-observability-suite)

## Install a trace exporter

PostHog Distributed Tracing works with any OpenTelemetry client. Use the OTel SDKs you already have, point your trace exporter at PostHog's HTTP endpoint, and add your project token.

On Node.js and Python you can skip OpenTelemetry entirely: `posthog-node` and `posthog` create and export spans themselves, and spans made inside a request context carry the person and session they belong to. See the [Node.js](https://posthog.com/docs/distributed-tracing/installation/nodejs.md) and [Python](https://posthog.com/docs/distributed-tracing/installation/python.md) guides.

Set these on your OpenTelemetry SDK:

```bash
OTEL_EXPORTER_OTLP_TRACES_ENDPOINT="https://us.i.posthog.com/i/v1/traces"
OTEL_EXPORTER_OTLP_TRACES_HEADERS="Authorization=Bearer <ph_project_token>"
OTEL_SERVICE_NAME="my-app"
```

`<ph_client_api_host>` and `<ph_project_token>` are filled in with your project's values when you're logged in. Use your **project token** (the same one you use for capturing events), not a [personal API key](https://posthog.com/docs/api.md#authentication).

This is a different endpoint from PostHog's AI/LLM tracing (`/i/v0/ai/otel`), which only accepts generative-AI spans. For general application traces, use `/i/v1/traces`.

For language-specific setup, follow one of our installation guides:

[Configure your tracing client](https://posthog.com/docs/distributed-tracing/installation.md)

## Send context-rich spans

PostHog ingests spans using OpenTelemetry's standard model: a trace is a tree of spans, each with a `trace_id`, `span_id`, and `parent_span_id`, plus timing, a service name, and attributes.

Wrap the operations you care about – incoming requests, outgoing calls, database queries – in spans, and enrich them with attributes for business context.

```python
from opentelemetry import trace

tracer = trace.get_tracer("my-app")

with tracer.start_as_current_span("checkout") as span:
    span.set_attribute("user.id", "123")
    span.set_attribute("cart.value", 4200)
    # ... your code ...
```

## Explore your traces

Once spans are flowing into PostHog, you can:

-   **Search and filter spans** by service, status, duration, and attributes
-   **Follow a trace end to end** as a waterfall to see where time goes
-   **Spot slow and failing operations** across your services
-   **View correlated logs** in the span inspector, scoped to a single span or the whole trace

## Part of PostHog's observability suite

Distributed tracing uses the same OpenTelemetry-based ingestion as [Logs](https://posthog.com/docs/logs.md), so a single OTel setup covers both. Your traces also live in the same PostHog project as [Session Replay](https://posthog.com/docs/session-replay.md), [Error Tracking](https://posthog.com/docs/error-tracking.md), and [Product Analytics](https://posthog.com/docs/product-analytics.md) – one platform instead of another observability vendor to run.

1/4

[**Install a trace exporter** ***Required***](#quest-item-install-a-trace-exporter)[**Send context-rich spans** ***Required***](#quest-item-send-context-rich-spans)[**Explore your traces** ***Required***](#quest-item-explore-your-traces)[**Part of PostHog's observability suite** ***Recommended***](#quest-item-part-of-posthogs-observability-suite)

**Install a trace exporter**

***Required***
