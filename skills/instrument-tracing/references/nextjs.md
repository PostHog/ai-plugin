> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Next.js tracing installation

Canonical URL: https://posthog.com/docs/distributed-tracing/installation/nextjs

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.i.posthog.com` instead of `https://us.i.posthog.com` (ingestion host), and use `https://eu.posthog.com` instead of `https://app.posthog.com` (app host for links).

## On this page

- [Install OpenTelemetry packages](#install-opentelemetry-packages)
- [Get your project token](#get-your-project-token)
- [Enable instrumentation in Next.js](#enable-instrumentation-in-nextjs)
- [Create the instrumentation file](#create-the-instrumentation-file)
- [Create spans](#create-spans)
- [Test your setup](#test-your-setup)
- [Next steps](#next-steps)

> **Already using `posthog-node` on the server?** Route handlers, server actions, and server components can create spans with its own span API instead of OpenTelemetry, with no extra packages – see the [Node.js guide](https://posthog.com/docs/distributed-tracing/installation/nodejs.md). Either way, spans are server-side only: there is no browser span API.

1.  1

    ## Install OpenTelemetry packages

    Required

    For the complete SDK reference, see the [OpenTelemetry JavaScript docs](https://opentelemetry.io/docs/languages/js/).

    ```bash
    npm install @opentelemetry/api @opentelemetry/sdk-trace-node @opentelemetry/sdk-trace-base @opentelemetry/resources @opentelemetry/semantic-conventions @opentelemetry/exporter-trace-otlp-proto
    ```

    `@opentelemetry/exporter-trace-otlp-proto` is the OTLP HTTP/protobuf trace exporter. The similarly named `-otlp-http` package sends HTTP/JSON and `-otlp-grpc` sends gRPC, so pick `-proto` to match this guide.

2.  2

    ## Get your project token

    Required

    You'll need your PostHog project token to authenticate trace requests. This is the same token you use for capturing events with the PostHog SDK.

    > **Important:** Use your **project token** which starts with `phc_`. Do **not** use a personal API key (which starts with `phx_`).

    You can find your project token in [Project settings](https://app.posthog.com/settings).

3.  3

    ## Enable instrumentation in Next.js

    Required

    > **Note:** This step is only needed on Next.js 13.2–14.x. For Next.js 15 and later, `instrumentation.ts` is enabled by default and the `experimental.instrumentationHook` option is deprecated — remove it from your config if it's set.

    On Next.js 14 and earlier, add the following to your `next.config.js` (or `next.config.mjs`) to enable the instrumentation hook:

    ```javascript
    /** @type {import('next').NextConfig} */
    const nextConfig = {
      experimental: {
        instrumentationHook: true,
      },
    }
    
    module.exports = nextConfig
    ```

4.  4

    ## Create the instrumentation file

    Required

    Create an `instrumentation.ts` (or `instrumentation.js`) file in the root of your project (or inside `src/` if you use that folder).

    ```typescript
    import { NodeTracerProvider } from '@opentelemetry/sdk-trace-node'
    import { BatchSpanProcessor } from '@opentelemetry/sdk-trace-base'
    import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-proto'
    import { resourceFromAttributes } from '@opentelemetry/resources'
    import { ATTR_SERVICE_NAME } from '@opentelemetry/semantic-conventions'
    
    // Create the provider outside register() so it can be exported and flushed in route handlers
    export const tracerProvider = new NodeTracerProvider({
      resource: resourceFromAttributes({
        [ATTR_SERVICE_NAME]: 'my-nextjs-app',
      }),
      spanProcessors: [
        new BatchSpanProcessor(
          new OTLPTraceExporter({
            url: 'https://us.i.posthog.com/i/v1/traces',
            headers: {
              Authorization: 'Bearer <ph_project_token>',
            },
          })
        ),
      ],
    })
    
    export function register() {
      if (process.env.NEXT_RUNTIME === 'nodejs') {
        tracerProvider.register()
      }
    }
    ```

    > **Note:** The `tracerProvider` is created outside of `register()` so it can be exported and used to flush spans in route handlers. This pattern is necessary because Route Handlers complete execution before batched spans have a chance to be sent to the collector. By exporting the provider, we can manually flush spans at the end of each request.

    > **Note:** `@opentelemetry/sdk-trace-node` only works in the Node.js runtime. If parts of your app use the [edge runtime](https://nextjs.org/docs/app/api-reference/edge) (e.g. middleware), the [Next.js OpenTelemetry guide](https://nextjs.org/docs/app/guides/open-telemetry) recommends moving Node-only setup into a separate file that `register()` dynamically imports behind the `NEXT_RUNTIME === 'nodejs'` check.

    Alternatively, you can pass the token as a query parameter:

    ```typescript
    new OTLPTraceExporter({
      url: 'https://us.i.posthog.com/i/v1/traces?token=<ph_project_token>',
    })
    ```

5.  5

    ## Create spans

    Required

    Wrap the operations you want to measure in spans, and attach attributes for context. Then flush the provider before the serverless function freezes.

    ```typescript
    import { SpanStatusCode } from '@opentelemetry/api'
    import { after } from 'next/server'
    import { tracerProvider } from '@/instrumentation'
    
    const tracer = tracerProvider.getTracer('my-nextjs-app')
    
    export async function GET() {
      await tracer.startActiveSpan('handle-request', async (span) => {
        try {
          span.setAttribute('endpoint', '/api/example')
          span.setAttribute('method', 'GET')
          // ... do work ...
          span.setStatus({ code: SpanStatusCode.OK })
        } catch (err) {
          span.recordException(err)
          span.setStatus({ code: SpanStatusCode.ERROR })
          throw err
        } finally {
          span.end()
        }
      })
    
      // Ensure spans are flushed before the serverless function freezes
      after(async () => {
        await tracerProvider.forceFlush()
      })
    
      return Response.json({ success: true })
    }
    ```

    > **Important:** Without calling `forceFlush()`, your spans may not be sent. When deploying to a serverless platform like Vercel, Route Handlers complete execution before the OpenTelemetry batch processor has a chance to export spans, and the function freezes before the batch is flushed. The `after()` function from `next/server` runs code after the response is sent, ensuring spans are flushed before the serverless function freezes.

    > **Note:** `after()` is stable in Next.js 15.1+ (available as `unstable_after` in 15.0). On Next.js 14 and earlier, it doesn't exist — flush before returning instead:
    >
    > ```typescript
    > await tracerProvider.forceFlush()
    > return Response.json({ success: true })
    > ```

6.  6

    ## Test your setup

    Recommended

    Once everything is configured, confirm spans are reaching PostHog:

    1.  Run your application and trigger the instrumented code
    2.  Open the PostHog Tracing interface
    3.  Confirm your spans and traces appear

    [View your traces in PostHog](https://app.posthog.com/tracing)

8.  ## Next steps

    Checkpoint

    *What you can do with your traces*

    | Action | Description |
    | --- | --- |
    | **[Why you need distributed tracing](https://posthog.com/docs/distributed-tracing/basics.md)** | What a trace shows you that nothing else does |
    | **Explore traces** | Read a trace as a waterfall to see where time goes |
    | **Filter spans** | Narrow down by service, status, duration, and attributes |
    | **Propagate context** | Pass trace context across services so spans join the same trace |

    [View your traces in PostHog](https://app.posthog.com/tracing)
