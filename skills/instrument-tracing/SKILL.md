---
name: instrument-tracing
description: >-
  Add PostHog distributed tracing to see how requests flow through services and
  where time goes. Use after implementing features or reviewing PRs to ensure
  request entry points, outbound calls, and background jobs produce spans, or
  when asked to add tracing or spans. Also handles pointing existing
  OpenTelemetry tracing at PostHog and initial OTLP exporter setup.
metadata:
  author: PostHog
---

# Add PostHog distributed tracing

Use this skill to add PostHog distributed tracing for new or changed code. Use it after implementing features or reviewing PRs to ensure request entry points, outbound calls, and background jobs produce spans, when the user asks to add tracing or spans, or to point existing OpenTelemetry tracing at PostHog. Supports any platform or language.

Supported platforms: Node.js, Next.js, Python (including Django, FastAPI, and Flask), Go, Java, .NET, PHP, Ruby, and any language via OpenTelemetry (OTLP).

PostHog tracing uses the standard OpenTelemetry SDK and an OTLP HTTP trace exporter. It does not need a PostHog SDK.

## Instructions

Follow these steps IN ORDER:

STEP 1: Analyze the codebase and detect the platform.
  - Detect the language, framework, and existing tracing setup.
  - Look for dependency files and project files (package.json, requirements.txt, pyproject.toml, go.mod, pom.xml, build.gradle, *.csproj, Gemfile, composer.json, etc.).
  - Look for lockfiles (pnpm-lock.yaml, package-lock.json, yarn.lock, bun.lockb, poetry.lock, uv.lock, go.sum, Gemfile.lock, composer.lock, etc.) to determine the package manager.
  - Look for existing tracing: an OpenTelemetry tracer provider, an `instrumentation.ts` file, an `opentelemetry-instrument` launch command, an OpenTelemetry Collector config, a Java agent flag, or another vendor's tracing agent.
  - Check whether a PostHog SDK (posthog-js, posthog-node, posthog-python) is already installed. You need this only for STEP 6.

STEP 2: Choose the capture path.
  - If the codebase already exports OpenTelemetry traces, point the existing OTLP trace exporter (or Collector) at PostHog. Reuse the existing tracer provider. If it exports to another tracing backend, ask the user before you add PostHog as a second destination.
  - Otherwise, add the OpenTelemetry SDK with an OTLP HTTP trace exporter and auto-instrumentation. Auto-instrumentation creates spans for HTTP servers, frameworks, and database drivers without code changes.
  - Read the platform reference that matches the detected stack now. Use its "With OpenTelemetry" section. If no reference matches, use the general installation reference.

STEP 3: Install dependencies. (Skip if the codebase already exports OpenTelemetry traces.)
  - Install the OpenTelemetry SDK, the OTLP HTTP/protobuf trace exporter, and the auto-instrumentation for the detected stack:
    - Node.js and Next.js: the packages from the platform reference, plus `@opentelemetry/auto-instrumentations-node`.
    - Python: `opentelemetry-distro` and `opentelemetry-exporter-otlp-proto-http`, then run `opentelemetry-bootstrap -a install`. It installs the instrumentation packages for the libraries the app already uses. Do not install `opentelemetry-instrumentation-all`.
    - Go: the packages from the platform reference, plus the contrib instrumentation for each library, such as `go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp`.
    - Java: the zero-code `opentelemetry-javaagent.jar`. It needs no dependency changes.
    - .NET: `OpenTelemetry`, `OpenTelemetry.Exporter.OpenTelemetryProtocol`, and `OpenTelemetry.Extensions.Hosting`, plus `OpenTelemetry.Instrumentation.AspNetCore` and `OpenTelemetry.Instrumentation.Http`.
    - PHP: the packages from the platform reference. For auto-instrumentation, the `opentelemetry` PHP extension (from PECL) and the `open-telemetry/opentelemetry-auto-*` package for the framework, such as `open-telemetry/opentelemetry-auto-slim`.
    - Ruby: `opentelemetry-sdk`, `opentelemetry-exporter-otlp`, and `opentelemetry-instrumentation-all`, enabled with `c.use_all`.
  - Do not manually edit dependency files — use the package manager's install command.

STEP 4: Configure the OTLP trace exporter.
  - Send spans over OTLP HTTP/protobuf to `/i/v1/traces` on the PostHog host, with the project token in an `Authorization: Bearer` header. Do not use `/i/v0/ai/otel`. That endpoint accepts only LLM spans.
  - With environment variables, set the full path in `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` and the header in `OTEL_EXPORTER_OTLP_TRACES_HEADERS` (`Authorization=Bearer <token>`). Do not set the base `OTEL_EXPORTER_OTLP_ENDPOINT` for PostHog. It appends its own `/v1/traces` path.
  - Set `OTEL_EXPORTER_OTLP_TRACES_PROTOCOL=http/protobuf` where the SDK or agent defaults to gRPC. This applies to the Java agent, .NET, and Python with `opentelemetry-distro`.
  - Python with `opentelemetry-distro`: start the app with `opentelemetry-instrument` (for example, `opentelemetry-instrument python app.py`). It builds the tracer provider from the environment variables, so do not also build a provider in code. The distro also turns on OTLP metric and log export. Set `OTEL_METRICS_EXPORTER=none` and `OTEL_LOGS_EXPORTER=none` unless the app already sends those signals somewhere.
  - Set a service name (`service.name`, or `OTEL_SERVICE_NAME`) so spans are easy to find in the Tracing UI.
  - Start the provider before the application loads its frameworks, so auto-instrumentation can patch them. In Next.js, register the provider in `instrumentation.ts` behind the `NEXT_RUNTIME === 'nodejs'` check.
  - Follow the platform-specific reference for the exact configuration.
  - You must read a file immediately before attempting to write it.

STEP 5: Add spans where they belong.
  - Auto-instrumentation covers request entry points and most outbound calls. Add manual spans with the OpenTelemetry tracer API only where it has no coverage: background job handlers, queue consumers, and slow internal steps the user cares about.
  - Use low-cardinality span names like `GET /users/:id`, not `GET /users/123`. Put variable values in attributes.
  - Pass the W3C `traceparent` header on calls between services, so spans from each service join one trace.
  - Do not alter the fundamental architecture of existing files. Make additions minimal and targeted.

STEP 6: Link spans to people and sessions. (Optional.)
  - A span joins a person and a Session Replay recording through the `posthogDistinctId` and `sessionId` span attributes.
  - If the app uses posthog-js, enable `tracing_headers` for your API hosts. The browser then sends `X-POSTHOG-DISTINCT-ID` and `X-POSTHOG-SESSION-ID` headers on each request.
  - With OpenTelemetry only, copy these values onto spans yourself. In the request handler or a middleware, read the two headers and set them as the `posthogDistinctId` and `sessionId` attributes on the active request span. Skip a header that is missing or empty.
  - If the app already uses the PostHog SDK, it can add these attributes for you. Do not install the PostHog SDK only for this step.
    - Python: add `PostHogContextSpanProcessor` from `posthog.integrations.otel` to the tracer provider. It copies the distinct ID and session ID from the active PostHog context onto each new span. Django's contexts middleware reads the headers and sets that context.
    - Node.js and Python: spans created with the PostHog SDK span API (`posthog.withSpan`, `posthog.start_span`) inside a PostHog request context get these attributes automatically. This needs `posthog-node` 5.52.0 or later, or `posthog` 7.58.0 or later, with the `traces` option set. These spans go through the PostHog SDK, not the OpenTelemetry provider. Use this only for apps that do not run OpenTelemetry.

STEP 7: Set up environment variables.
  - Check if the project already has PostHog environment variables configured (e.g. in `.env`, `.env.local`, or framework-specific env files). If valid values already exist, skip this step.
  - If the PostHog project token is missing, use the PostHog MCP server's `projects-get` tool to retrieve the project's `api_token`. If multiple projects are returned, ask the user which project to use. If the MCP server is not connected or not authenticated, ask the user for their PostHog project token instead.
  - Use the project token (it starts with `phc_`). Do not use a personal API key (it starts with `phx_`).
  - For the PostHog host URL: check the `projects-get` MCP response for a `region` field — `US` maps to `https://us.i.posthog.com`, `EU` maps to `https://eu.i.posthog.com`. If the region is not available from the MCP response or from existing project configuration, ask the user: "Are you on PostHog US Cloud or EU Cloud?" Do not assume US Cloud.
  - For the OTLP traces endpoint, use `https://us.i.posthog.com/i/v1/traces` (US) or `https://eu.i.posthog.com/i/v1/traces` (EU), matching the region determined above, with the project token as an `Authorization: Bearer` header.
  - Write these values to the appropriate env file using the framework's naming convention.
  - Reference these environment variables in code instead of hardcoding them.

STEP 8: Flush spans in short-lived processes.
  - The batch processor exports spans on an interval. A script, cron job, or serverless function can stop before the batch is sent.
  - On Vercel and other serverless platforms, call the provider's `forceFlush()` before the function returns. In Next.js 15.1 and later, call it inside `after()` from `next/server`.
  - On AWS Lambda, call `forceFlush()` at the end of each invocation. Do not call `shutdown()` there, because the runtime reuses the container. Call `shutdown()` only when the process exits.

STEP 9: Verify spans arrive.
  - Run the application and trigger the instrumented code.
  - Open Tracing in the PostHog sidebar and filter by the service name. Spans should appear within a minute of sending.
  - If no spans appear, check the endpoint path, the `Bearer` token, the exporter protocol, and the flush step.

## Reference files

- `references/nodejs.md` - Node.js tracing installation
- `references/nextjs.md` - Next.js tracing installation
- `references/python.md` - Python tracing installation
- `references/go.md` - Go tracing installation
- `references/java.md` - Java tracing installation
- `references/dotnet.md` - .net tracing installation
- `references/php.md` - Php tracing installation
- `references/ruby.md` - Ruby tracing installation
- `references/installation.md` - Install tracing
- `references/start-here.md` - Getting started with distributed tracing
- `references/basics.md` - Why you need distributed tracing
- `references/COMMANDMENTS.md` - Framework-specific rules the integration must follow

Each platform reference contains specific OpenTelemetry setup, OTLP configuration, and integration patterns. Find the one matching the user's stack.

## Key principles

- **OpenTelemetry first**: PostHog traces use the OpenTelemetry protocol. Use the OpenTelemetry SDK with auto-instrumentation, and reuse an existing tracer provider when there is one. The PostHog SDK is optional.
- **Environment variables**: Always use environment variables for PostHog keys and OpenTelemetry endpoints. Never hardcode them.
- **Minimal changes**: Add PostHog trace export alongside existing code. Don't replace or restructure existing tracing.
- **Boundaries, not every function**: A few spans at request entry, outbound calls, and background jobs are better than a span around every function.
- **No secrets in attributes**: Never put tokens, passwords, or other secrets in span names or attributes.
