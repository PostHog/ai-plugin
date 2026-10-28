> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Why you need distributed tracing

Canonical URL: https://posthog.com/docs/distributed-tracing/basics

## On this page

- [What is a trace?](#what-is-a-trace)
- [What tracing shows you that nothing else does](#what-tracing-shows-you-that-nothing-else-does)
- [When tracing saves you](#when-tracing-saves-you)
- [What good tracing looks like](#what-good-tracing-looks-like)
- [How PostHog makes tracing useful](#how-posthog-makes-tracing-useful)
- [Next steps](#next-steps)

Tracing follows a single request as it travels through your application – across the functions, services, databases, and APIs it touches along the way. Where [Logs](https://posthog.com/docs/logs.md) record what happened at each point, a trace shows you the whole path: what called what, in what order, and how long each step took.

This page covers what a trace is, what it shows you that nothing else does, and when it saves you hours of debugging.

## What is a trace?

A **trace** is the complete journey of one request through your system. It's made up of **spans** – each span is a single unit of work, like an incoming HTTP request, a database query, or a call to a third-party API.

Spans nest into a tree. The incoming request is the root span, and everything it triggers becomes a child span underneath it. Each span records:

-   A **name** and **service** - what ran, and where
-   A **start time** and **duration** - when it happened, and how long it took
-   A **status** - whether it succeeded or failed
-   **Attributes** - any context you attach, like a user ID or a query parameter

Because every span in a request shares the same `trace_id`, you can reconstruct the request as a waterfall and see exactly where the time went and where things broke.

## What tracing shows you that nothing else does

Each PostHog product answers a different question about your application:

| Product | What it tells you | Example |
| --- | --- | --- |
| **[Product Analytics](https://posthog.com/docs/product-analytics.md)** | What users did | "User clicked checkout" |
| **[Logs](https://posthog.com/docs/logs.md)** | What happened at each point | "Inventory service returned 200 with 0 items" |
| **[Error Tracking](https://posthog.com/docs/error-tracking.md)** | What broke | "TypeError: cannot read property 'price' of undefined" |
| **Distributed tracing** | How the request flowed and where time went | "Checkout took 3.2s, and 2.8s of it was spent waiting on the inventory service" |

Errors tell you something broke. Logs tell you what happened at one point. Tracing tells you **how the pieces connected, and where the time and failures actually came from** – across every service a request touched.

In a single process, you can often guess. Once a request fans out across services, queues, and third-party APIs, guessing stops working. Tracing replaces the guesswork with a map.

## When tracing saves you

### A request is slow, but you don't know which part

Without tracing, "the checkout endpoint is slow" sends you back to the code to add timers by hand.

With tracing, you open the trace and read the waterfall top to bottom. The handler is fast and the payment call is fast, but one span sits at 2.8 seconds because the inventory service runs a separate database query for every item in the cart instead of one query for the whole cart. You found the N+1 in seconds.

### A failure crosses service boundaries

A user hits an error on the frontend, but the root cause is three services deep. The error surfaces in one place and originates somewhere else entirely.

With tracing, you follow the `trace_id` from the failed request down through each service it called, and land on the span that actually failed: a downstream auth service returning 401 because a token expired mid-request.

### Latency only happens sometimes

The endpoint is usually fast, but your p99 is terrible and you can't reproduce it. Averages hide the problem.

With tracing, you filter to the slow traces and compare them against the fast ones. The slow traces all share one span: a cache miss that falls through to a cold database query. Now you know what to fix.

### Async and background work disappears

A request kicks off a queue job that runs later. There's no single stack trace that spans the gap between them.

With tracing, context propagates across the boundary, so the job's spans attach to the trace that started them. You see the whole flow, even when it crosses processes and time.

## What good tracing looks like

Useful tracing is about instrumenting the right boundaries, not every line of code.

1.  **Trace the boundaries** – Wrap incoming requests, outgoing calls, and database queries. These are where time is spent and where things fail.

2.  **Give spans descriptive names** – `GET /api/checkout` and `db.query load_cart` tell you what ran at a glance. `handler` and `query` don't.

3.  **Add business context as attributes** – Attach the user ID, the plan, and the [Feature Flag](https://posthog.com/docs/feature-flags.md) variant. When a trace is slow, you want to know *who* it was slow for.

4.  **Propagate context across services** – Pass trace context with every outgoing call so spans from different services join the same trace. This is what makes tracing *distributed*.

## How PostHog makes tracing useful

**No vendor lock-in** - PostHog ingests traces over [OpenTelemetry (OTLP)](https://posthog.com/docs/distributed-tracing/start-here.md). Use standard OTel libraries in any language, with no proprietary SDK. If you already export traces, point them at PostHog and you're done.

**Built on the same pipeline as Logs** - Tracing uses the same OpenTelemetry-based ingestion as [Logs](https://posthog.com/docs/logs.md), so a single OTel setup covers both. When inspecting a span, the **Logs** tab shows correlated logs scoped to that span or the whole trace, and you can deep-link into the full Logs product with filters pre-applied.

**One platform, not another vendor** - Your traces live in the same PostHog project as [Session Replay](https://posthog.com/docs/session-replay.md), [Error Tracking](https://posthog.com/docs/error-tracking.md), and [Product Analytics](https://posthog.com/docs/product-analytics.md), so you have one less observability tool to run and pay for.

**One meter with Logs** - Tracing and Logs bill together on a single ingestion meter with a monthly free tier. See [Tracing pricing](https://posthog.com/tracing/pricing.md).

## Next steps

-   **[Get started](https://posthog.com/docs/distributed-tracing/start-here.md)** - Install an OpenTelemetry exporter and send your first spans
-   **[Logs](https://posthog.com/docs/logs.md)** - Capture what happened at each point, using the same OpenTelemetry setup
-   **[Error Tracking](https://posthog.com/docs/error-tracking.md)** - Turn failures into issues you can assign and resolve
