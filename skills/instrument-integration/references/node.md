> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Node.js

If you're working with Node.js (versions 20+), the official `posthog-node` library is the simplest way to integrate your software with PostHog. This library uses an internal queue to make calls fast and non-blocking. It also batches requests and flushes asynchronously, making it perfect to use in any part of your web app or other server-side application that needs performance. And in addition to event capture, [feature flags](/docs/feature-flags.md) are supported as well.

## Installation

Run either `npm` or `yarn` in terminal to add it to your project:

### npm

```bash
npm install posthog-node --save
```

### Yarn

```bash
yarn add posthog-node
```

### pnpm

```bash
pnpm add posthog-node
```

### Bun

```bash
bun add posthog-node
```

In your app, set your project token **before** making any calls.

Node.js

```javascript
import { PostHog } from 'posthog-node'

const client = new PostHog(
    '<ph_project_token>',
    { host: 'https://us.i.posthog.com' }
)

await client.shutdown()
```

You can find your project token and instance address in the [project settings](https://app.posthog.com/project/settings) page in PostHog.

> **Note:** As a rule of thumb, we do not recommend hardcoding API keys or tokens. Setting it as an environment variable is preferred.

## Identifying users

> **Identifying users is required.** Backend events need a `distinct_id` that matches the ID your frontend uses when calling `posthog.identify()`. Without this, backend events are orphaned — they can't be linked to frontend event captures, [session replays](/docs/session-replay.md), [LLM traces](/docs/ai-engineering.md), or [error tracking](/docs/error-tracking.md).
>
> See our guide on [identifying users](/docs/getting-started/identify-users.md) for how to set this up.

### Options

| Variable | Description | Default value |
| --- | --- | --- |
| `host` | Your PostHog host | `https://us.i.posthog.com/` |
| `flushAt` | After how many capture calls we should flush the queue (in one batch) | `20` |
| `flushInterval` | After how many ms we should flush the queue | `10000` |
| `personalApiKey` | An optional [personal API key](/docs/api/overview.md#personal-api-keys-recommended) for evaluating feature flags locally. Note: Providing this will trigger periodic calls to the feature flags service, even if you're not using feature flags. | `null` |
| `featureFlagsPollingInterval` | Interval in milliseconds specifying how often feature flags should be fetched from the PostHog API | `300000` |
| `requestTimeout` | Timeout in milliseconds for any calls | `10000` |
| `maxCacheSize` | Maximum size of cache that deduplicates $feature\_flag\_called calls per user. | `50000` |
| `disableGeoip` | When true, disables automatic GeoIP resolution for events and feature flags. | `true` |
| `isServer` | Controls the `$is_server` event property. Keep the default for server-side events. Set to `false` when using `posthog-node` from a client-like runtime, CLI, or desktop app so device OS attribution is handled normally. | `true` |
| `evaluationContexts` | Evaluation context tags that constrain which feature flags are evaluated. When set, only flags with matching evaluation context tags (or no evaluation context tags) will be returned. This helps reduce unnecessary flag evaluations and improves performance. See [evaluation contexts documentation](/docs/feature-flags/evaluation-contexts.md) for more details. Available in version 5.23.0+. The legacy parameter `evaluationEnvironments` (version 5.10.0+) is also supported for backward compatibility. | `undefined` |

> **Note:** When using PostHog in an AWS Lambda function or a similar serverless function environment, make sure you set `flushAt` to `1` and `flushInterval` to `0`. Also, remember to always call `await posthog.shutdown()` at the end to flush and send all pending events.

## Capturing events

You can send custom events using `capture`:

Node.js

```javascript
client.capture({
    distinctId: 'distinct_id_of_the_user',
    event: 'user signed up',
})
```

> **Tip:** We recommend using a `[object] [verb]` format for your event names, where `[object]` is the entity that the behavior relates to, and `[verb]` is the behavior itself. For example, `project created`, `user signed up`, or `invite sent`.

### Setting event properties

Optionally, you can include additional information with the event by including a [properties](/docs/data/events.md#event-properties) object:

Node.js

```javascript
client.capture({
  distinctId: 'distinct_id_of_the_user',
  event: 'user signed up',
  properties: {
    login_type: 'email',
    is_free_trial: true,
  },
})
```

### Capturing pageviews

If you're aiming for a backend-only implementation of PostHog and won't be capturing events from your frontend, you can send `$pageview` events from your backend like so:

Node.js

```javascript
client.capture({
  distinctId: 'distinct_id_of_the_user',
  event: '$pageview',
  properties: {
    $current_url: 'https://example.com',
  },
})
```

## Person profiles and properties

The Node SDK captures identified events by default. These create [person profiles](/docs/data/persons.md). To set [person properties](/docs/product-analytics/person-properties.md) in these profiles, include them when capturing an event using `$set` and `$set_once`:

Node.js

```javascript
client.capture({
  distinctId: 'distinct_id_of_the_user',
  event: 'movie_played',
  properties: {
    $set: { name: 'Max Hedgehog'  },
    $set_once: { initial_url: '/blog' },
  },
})
```

For more details on the difference between `$set` and `$set_once`, see our [person properties docs](/docs/product-analytics/person-properties.md#what-is-the-difference-between-set-and-set_once).

You can also use helper methods to set or remove person properties without hand-building `$set`, `$set_once`, or `$unset` payloads. See [person properties](/docs/product-analytics/person-properties.md) for examples.

To capture [anonymous events](/docs/data/anonymous-vs-identified-events.md) without person profiles, set the event's `$process_person_profile` property to `false`:

Node.js

```javascript
client.capture({
  distinctId: 'distinct_id_of_the_user',
  event: 'movie_played',
  properties: {
    $process_person_profile: false,
  },
})
```

## Alias

Sometimes, you want to assign multiple distinct IDs to a single user. This is helpful when your primary distinct ID is inaccessible. For example, if a distinct ID used on the frontend is not available in your backend.

In this case, you can use `alias` to assign another distinct ID to the same user.

Node.js

```javascript
client.alias({
  distinctId: 'distinct_id',
  alias: 'alias_id',
})
```

We strongly recommend reading our docs on [alias](/docs/product-analytics/identify.md#alias-assigning-multiple-distinct-ids-to-the-same-user) to best understand how to correctly use this method.

## Super properties

> Requires `posthog-node` version >= 5.25.0.

Super properties are properties that are automatically included with every event captured by the client. Use `register` to set them:

Node.js

```javascript
client.register({
  app_version: '1.2.0',
  environment: 'production',
})

// Both events include app_version and environment
client.capture({
  distinctId: 'distinct_id',
  event: 'page_viewed',
})
client.capture({
  distinctId: 'distinct_id',
  event: 'button_clicked',
})
```

If an event sets a property with the same key as a super property, the event's property takes precedence:

Node.js

```javascript
client.register({ environment: 'production' })

// This event is captured with environment='staging'
client.capture({
  distinctId: 'distinct_id',
  event: 'page_viewed',
  properties: { environment: 'staging' },
})
```

To remove a super property, use `unregister`:

Node.js

```javascript
client.unregister('environment')
```

Super properties are **global** — they apply to every event for the lifetime of the client instance. For properties that should only apply to a specific scope (e.g. a single request or transaction), use [contexts](#contexts) instead.

## Contexts

> Requires `posthog-node` version >= 5.17.0.

The Node SDK uses nested contexts for managing state that's shared across events. Contexts are useful for adding properties to multiple events (including exceptions) during a single user's interaction with your product.

You can enter a context using `withContext`:

Node.js

```javascript
posthog.withContext(
  {
    distinctId: 'user-123',
    properties: { transactionId: 'abc123' }
  },
  () => {
    // This event is captured with the distinct ID and properties set above
    posthog.capture({ event: 'order_processed' })
  }
)
```

Contexts are persisted across function calls. If you enter one and then call a function and capture an event in the called function, it uses the context properties set in the parent context:

Node.js

```javascript
function someFunction() {
  // When called from `outerFunction`, this event is captured
  // with transactionId='abc123'
  posthog.capture({ event: 'order_processed' })
}

function outerFunction() {
  posthog.withContext(
    { properties: { transactionId: 'abc123' } },
    () => {
      someFunction()
    }
  )
}
```

By default, each context inherits from parent contexts. To disable nesting (where child contexts is fresh and has no properties), pass `{ fresh: true }`:

Node.js

```javascript
posthog.withContext(
  {
    properties: {
      someKey: 'value-1',
      someOtherKey: 'another-value'
    }
  },
  () => {
    posthog.withContext(
      { properties: { someKey: 'value-2' } },
      () => {
        // Captured with someKey='value-2', someOtherKey='another-value'
        posthog.capture({ event: 'order_processed' })
      },
    )

    // Captured with someKey='value-1', someOtherKey='another-value'
    posthog.capture({ event: 'order_completed' })
  }
)
```

> **Note:** Properties passed directly to `capture` calls override context state in the final event.

### Identification context

Contexts can be associated with a distinct ID:

Node.js

```javascript
posthog.withContext(
  { distinctId: 'user-123' },
  () => {
    // Associated with "user-123"
    posthog.capture({ event: 'order_processed' })

    // Overrides to "another-user"
    posthog.capture({
      distinctId: 'another-user',
      event: 'order_processed'
    })
  }
)
```

### Session context

Node.js

```javascript
posthog.withContext(
  { sessionId: 'some-session' },
  () => {
    // Associated with session "some-session"
    posthog.capture({ event: 'image_uploaded' })

    // Overrides to "next-session"
    posthog.capture({
      event: 'image_uploaded',
      properties: { $sessionId: 'next-session' }
    })
  }
)
```

### Custom context parameters

Node.js

```javascript
posthog.withContext(
  { flightNumber: 'TAC313' },
  () => {
    // Associated with flightNumber TAC313
    posthog.capture({ event: 'flight_cancelled' })

    // Overrides to PL7714
    posthog.capture({
      event: 'flight_cancelled',
      properties: { flightNumber: 'PL7714' }
    })
  }
)
```

## Add request context to Express

> Requires `posthog-node` version >= 5.31.0.

If you use Express, add request-scoped PostHog context with the built-in middleware helpers. Register `setupExpressRequestContext` before your routes so events captured during a request automatically use the incoming session and distinct ID headers. Register `setupExpressErrorHandler` after your routes if you want to send Express errors to PostHog Error Tracking.

server.ts

```typescript
import express from 'express'
import { PostHog, setupExpressRequestContext, setupExpressErrorHandler } from 'posthog-node'

const app = express()
const posthog = new PostHog('<ph_project_token>', {
  host: 'https://us.i.posthog.com',
})

// Register before routes.
setupExpressRequestContext(posthog, app)

app.post('/checkout', (req, res) => {
  posthog.capture({ event: 'checkout_started' })
  res.json({ status: 'ok' })
})

// Optional: register after routes to capture Express errors.
setupExpressErrorHandler(posthog, app)
```

The request context middleware reads the following incoming headers:

| Header | Context property | Description |
| --- | --- | --- |
| `x-posthog-session-id` | `sessionId` | Links server events to a client session |
| `x-posthog-distinct-id` | `distinctId` | Sets the event distinct ID |

It also automatically adds request metadata as event properties:

-   `$current_url` – the request URL
-   `$request_method` – the HTTP method (GET, POST, etc.)
-   `$request_path` – the request path
-   `$user_agent` – the user agent string
-   `$ip` – the client IP (parsed from `x-forwarded-for` if behind a proxy)

Properties and `distinctId` passed directly to `capture` take precedence over request context. Tracing headers are client-controlled analytics context, not authentication or authorization. Pass an authenticated `distinctId` explicitly for security-sensitive server-side decisions.

### Send headers from the client

If you're using [PostHog JS](/docs/libraries/js.md) on the frontend, configure [`tracing_headers`](/docs/libraries/js/config.md#tracing-headers) for your Express backend hostname so browser requests include `X-POSTHOG-SESSION-ID` and `X-POSTHOG-DISTINCT-ID`, which the Express middleware reads automatically.

## Add request context and error capture to Fastify

See the [Fastify guide](/docs/libraries/fastify.md) for installation, request context, event capture, error handling, and shutdown.

## Distributed tracing

> Requires `posthog-node` version >= 5.52.0.

**The span API is experimental**

Tracing is new in `posthog-node` and its API can still change in a minor release. Spans you send are kept – it's the SDK surface that isn't frozen yet.

Tracing records **spans** – timed units of work – so you can see where time went in a request and how work fans out across your services. Spans created inside a request context automatically carry the person and session they belong to, so a slow trace links back to the person who experienced it.

Tracing is off until you set the `traces` option. No OpenTelemetry dependency is required. For what you can do with spans once they arrive, see [Distributed tracing](/docs/distributed-tracing/start-here.md).

server.ts

```typescript
import { PostHog } from 'posthog-node'

const posthog = new PostHog('<ph_project_token>', {
  host: 'https://us.i.posthog.com',
  traces: {
    serviceName: 'checkout-api',
  },
})
```

Set `serviceName` – PostHog groups operations by service and span name.

### Creating spans

`withSpan` runs a callback with a span active for its duration and ends the span for you: at return for a synchronous callback, when the promise settles for an async one. Spans created inside the callback nest underneath it automatically.

TypeScript

```typescript
await posthog.withSpan('POST /checkout', async (span) => {
  span.setAttribute('plan', user.plan)

  const order = await posthog.withSpan('create-order', () => createOrder(cart))
  await posthog.withSpan('charge-card', () => stripe.charge(order))

  return order
})
```

If the callback throws or rejects, the span records the exception, its status is set to `error`, and your original error propagates unchanged.

The recorded exception includes the stack trace, which contains file paths from your server. If you'd rather those didn't leave your process, delete `exception.stacktrace` in [`beforeSpanSend`](#scrubbing-and-dropping-spans).

Use `startSpan` for work that can't wrap a callback. **`startSpan` does not make the span active**, so spans created afterwards are not its children unless you pass `parent` explicitly – and you must call `end()` yourself.

TypeScript

```typescript
const span = posthog.startSpan('background-sync', { attributes: { queue: 'emails' } })

// Explicitly parent a child to a span that isn't active.
const child = posthog.startSpan('send-batch', { parent: span })
child.end()

span.end()
```

`getActiveSpan()` returns the span currently active on this execution path, or `null` outside any `withSpan` callback.

### Span names and attributes

Span names should be low-cardinality operation names – `GET /users/:id`, not `GET /users/123`. Variable values belong in attributes, which accept strings, numbers, booleans, BigInt values, and arrays of those.

TypeScript

```typescript
await posthog.withSpan('GET /users/:id', { kind: 'server' }, async (span) => {
  span.setAttributes({ 'user.id': id, 'db.rows': rows.length })
  span.addEvent('cache-miss')

  if (rows.length === 0) {
    span.setStatus('error', 'user not found')
  }
})
```

| Method | Description |
| --- | --- |
| `setAttribute(key, value)` | Set a single attribute |
| `setAttributes(attributes)` | Merge several attributes at once |
| `addEvent(name, attributes?, timestamp?)` | Record a timestamped event within the span |
| `setStatus(status, message?)` | Set the outcome: `'ok'` or `'error'` |
| `recordException(error)` | Attach an exception event carrying the type, message, and stack, and set status to `error` |
| `updateName(name)` | Replace the span name, e.g. once a route template resolves |
| `traceparent()` | This span's W3C `traceparent` header value |
| `tracestate()` | This span's W3C `tracestate` value, or `null` when it has none |
| `end(endTime?)` | End the span and queue it for export |

Both `withSpan` and `startSpan` take the same options:

| Option | Description |
| --- | --- |
| `kind` | What the work is: `'internal'` (default), `'server'` for an inbound request, `'client'` for an outbound call, `'producer'` or `'consumer'` for queue work |
| `attributes` | Attributes to set at span start |
| `parent` | A span handle, or an inbound W3C `traceparent` string to continue a trace another service started |
| `tracestate` | The W3C `tracestate` accompanying a `traceparent` string. Ignored when `parent` is a span handle, which inherits its parent's |
| `startTime` | Backdate the span's start, as a millisecond epoch or a `Date`. The server clamps a start more than 24 hours old to receive time; with `debug` on, the SDK warns when you pass one |

### Tracing across services

Spans use [W3C Trace Context](https://www.w3.org/TR/trace-context/), so a trace can span several services. Pass an inbound `traceparent` header as `parent` to continue a trace another service started, and send `span.traceparent()` onward when you call out.

server.ts

```typescript
app.post('/checkout', async (req, res) => {
  await posthog.withSpan('POST /checkout', { kind: 'server', parent: req.get('traceparent') }, async (span) => {
    const traceparent = span.traceparent()

    await fetch('https://payments.internal/charge', {
      method: 'POST',
      headers: traceparent ? { traceparent } : {},
    })

    res.json({ status: 'ok' })
  })
})
```

A missing or malformed `traceparent` starts a new trace rather than throwing.

A continued trace propagates the sampled flag it was handed, so a downstream sampler sees the decision the head service made. PostHog itself doesn't sample – a span is recorded and exported whichever way that flag is set.

### Linking traces to people and sessions

Spans created inside a PostHog request context automatically carry `posthogDistinctId` and `sessionId` attributes, which is what makes a trace reachable from a person or a Session Replay recording. Use the [Express middleware](#add-request-context-to-express) or [`withContext`](#contexts):

TypeScript

```typescript
posthog.withContext({ distinctId: user.id, sessionId }, async () => {
  await posthog.withSpan('POST /checkout', () => processOrder())
})
```

Spans created outside a request context omit those attributes.

### Scrubbing and dropping spans

`beforeSpanSend` runs on every finished span before it's queued for export. Edit the span in place to strip attributes you don't want leaving your process, or return `null` to drop the span entirely.

TypeScript

```typescript
const posthog = new PostHog('<ph_project_token>', {
  host: 'https://us.i.posthog.com',
  traces: {
    serviceName: 'checkout-api',
    beforeSpanSend: (span) => {
      if (span.attributes['http.route'] === '/health') return null

      delete span.attributes['http.request.header.authorization']
      return span
    },
  },
})
```

The hook sees plain values rather than the OTLP wire encoding, so `span.attributes.userId` reads as `42`, not `{ intValue: '42' }`. It runs after PostHog attaches `posthogDistinctId` and `sessionId`, so those are visible to the hook and can be scrubbed too.

-   `traceId`, `spanId`, and `parentSpanId` are read-only. Rewriting them would orphan child spans that have already been exported, so assignments are ignored.
-   A hook that throws drops the span rather than exporting it without scrubbing.
-   Pass an array to run several hooks left to right. The first one to return `null` stops the chain.

### Span limits

A span is capped at 128 attributes and 128 events, each event at 128 attributes, and each string attribute value at 8192 characters. The endpoint rejects a span that's too large, and a rejected span is lost whole rather than truncated, so the caps bound a span before it gets there.

Past the cap, the earliest attributes and events are kept and the number dropped is reported alongside the span, so a truncated span reads as truncated rather than as quietly incomplete. The attributes PostHog attaches itself – `posthogDistinctId` and `sessionId` – don't count toward the cap and are never dropped, so a span at the limit still links back to its person and session.

The event cap is absolute: an `exception` event the SDK records for you spends an ordinary slot like any other. A span that fills its events and then throws keeps its `error` status but not the exception detail, and reports the loss in `droppedEventsCount`. Raise `maxEventsPerSpan` on spans that record many events and can also fail.

The length bound reaches inside a value, including strings nested in arrays and objects, and applies to `exception.stacktrace` like any other attribute. All four caps are re-applied after `beforeSpanSend`, so a hook that enriches a span can't push it back over.

### Configuration

| Option | Default | Description |
| --- | --- | --- |
| `serviceName` | – | Name of the service producing spans. Set this |
| `serviceVersion` | – | Version of the service |
| `environment` | – | Deployment environment, e.g. `production` |
| `resourceAttributes` | – | Extra OTLP resource attributes. Takes precedence over the fields above |
| `flushIntervalMs` | `5000` | How often queued spans are exported |
| `maxExportBatchSize` | `512` | Maximum spans per request |
| `maxQueueSize` | `2048` | Maximum spans held in memory. Spans beyond this are dropped |
| `maxLiveSpans` | `10000` | Maximum spans open at once. At the limit `startSpan` returns an inert handle |
| `maxSpanAgeMs` | `3600000` | A span still open after this is treated as leaked and never exported |
| `beforeSpanSend` | – | Edit or drop each finished span before export. Return `null` to drop it |
| `maxAttributesPerSpan` | `128` | Maximum attributes you set on one span |
| `maxEventsPerSpan` | `128` | Maximum events on one span |
| `maxAttributeValueLength` | `8192` | Maximum characters in a string attribute value |

### Shutdown and short-lived processes

Both `flush()` and `shutdown()` export spans that have already ended. A span still open at `flush()` is exported once it ends; a span still open at `shutdown()` is discarded, so end your spans before shutting down – `withSpan` does this for you.

In a serverless handler, call `flush()`: the container is reused across invocations, so `shutdown()` would throw away the connection pool and the flag cache. Events and spans are flushed concurrently, so it costs one round trip, not two.

TypeScript

```typescript
export const handler = async () => {
  await posthog.withSpan('handler', () => doWork())
  await posthog.flush()
}
```

**Edge runtimes**

On edge runtimes, spans nest across `await` only when you pass `parent` explicitly. The Node runtime tracks the active span with `AsyncLocalStorage`; the edge build cannot, so after an `await`, `getActiveSpan()` returns `null` and a new span starts a new trace. Pass the span your callback receives instead:

TypeScript

```typescript
await posthog.withSpan('handler', async (span) => {
  const user = await loadUser()
  await posthog.withSpan('render', { parent: span }, () => render(user))
})
```

## Feature flags

PostHog's [feature flags](/docs/feature-flags.md) enable you to safely deploy and roll back new features as well as target specific users and groups with them.

There are two steps to implement feature flags in Node:

### Step 1: Evaluate flags once

Call `client.evaluateFlags()` once for the user, then read values from the returned snapshot.

#### Boolean feature flags

Node.js

```javascript
const flags = await client.evaluateFlags('distinct_id_of_your_user')

if (flags.isEnabled('flag-key')) {
    // Do something differently for this user
    // Optional: fetch the payload
    const matchedFlagPayload = flags.getFlagPayload('flag-key')
}
```

#### Multivariate feature flags

Node.js

```javascript
const flags = await client.evaluateFlags('distinct_id_of_your_user')
const enabledVariant = flags.getFlag('flag-key')

if (enabledVariant === 'variant-key') { // replace 'variant-key' with the key of your variant
    // Do something differently for this user
    // Optional: fetch the payload
    const matchedFlagPayload = flags.getFlagPayload('flag-key')
}
```

`flags.getFlag()` returns the variant string for multivariate flags, `true` for enabled boolean flags, `false` for disabled flags, and `undefined` when the flag wasn't returned by the evaluation.

> **Note:** `client.isFeatureEnabled()`, `client.getFeatureFlag()`, `client.getFeatureFlagPayload()`, and `capture({ sendFeatureFlags: true })` still work during the migration period, but they're deprecated. Prefer `evaluateFlags()` for new code.

### Step 2: Include feature flag information when capturing events

If you want use your feature flag to breakdown or filter events in your [insights](/docs/product-analytics/insights.md), you'll need to include feature flag information in those events. This ensures that the feature flag value is attributed correctly to the event.

> **Note:** This step is only required for events captured using our server-side SDKs or [API](/docs/api.md).

There are two methods you can use to include feature flag information in your events:

#### Method 1: Pass the evaluated flags snapshot to `capture()`

Pass the same `flags` object that you used for branching. This attaches the exact flag values from that evaluation and doesn't make another `/flags` request.

Node.js

```javascript
const flags = await client.evaluateFlags('distinct_id_of_your_user')

if (flags.isEnabled('flag-key')) {
    // Do something differently for this user
}

client.capture({
    distinctId: 'distinct_id_of_your_user',
    event: 'event_name',
    flags,
})
```

By default, this attaches every flag in the snapshot using `$feature/<flag-key>` properties and `$active_feature_flags`.

To reduce event property bloat, pass a filtered snapshot:

Node.js

```javascript
// Attach only flags accessed with isEnabled() or getFlag() before this call
client.capture({
    distinctId: 'distinct_id_of_your_user',
    event: 'event_name',
    flags: flags.onlyAccessed(),
})

// Attach only specific flags
client.capture({
    distinctId: 'distinct_id_of_your_user',
    event: 'event_name',
    flags: flags.only(['checkout-flow', 'new-dashboard']),
})
```

`onlyAccessed()` is order-dependent. If you call it before accessing any flags with `isEnabled()` or `getFlag()`, no feature flag properties are attached.

#### Method 2: Include the `$feature/feature_flag_name` property manually

In the event properties, include `$feature/feature_flag_name: variant_key`:

Node.js

```javascript
client.capture({
    distinctId: 'distinct_id_of_your_user',
    event: 'event_name',
    properties: {
        // Replace feature-flag-key with your flag key and 'variant-key' with the key of your variant
        '$feature/feature-flag-key': 'variant-key',
    },
})
```

### Evaluating only specific flags

By default, `evaluateFlags()` evaluates every flag for the user. If you only need a few flags, pass `flagKeys` to request only those flags:

Node.js

```javascript
const flags = await client.evaluateFlags('distinct_id_of_your_user', {
    flagKeys: ['checkout-flow', 'new-dashboard'],
})
```

### Sending `$feature_flag_called` events

Capturing `$feature_flag_called` events enables PostHog to know when a flag was accessed by a user and provide [analytics and insights](/docs/product-analytics/insights.md) on the flag. With `evaluateFlags()`, the SDK sends this event when you call `flags.isEnabled()` or `flags.getFlag()` for a flag.

The SDK deduplicates these events per `(distinct_id, flag, value)` in a local cache. If you reinitialize the PostHog client, the cache resets and `$feature_flag_called` events may be sent again. PostHog handles duplicates, so duplicate `$feature_flag_called` events don't affect your analytics.

`flags.getFlagPayload()` doesn't send `$feature_flag_called` events and doesn't count as an access for `onlyAccessed()`.

### Advanced: Overriding server properties

Sometimes, you may want to evaluate feature flags using [person properties](/docs/product-analytics/person-properties.md), [groups](/docs/product-analytics/group-analytics.md), or group properties that haven't been ingested yet, or were set incorrectly earlier.

You can provide properties to evaluate the flag with by using the `person properties`, `groups`, and `group properties` arguments. PostHog will then use these values to evaluate the flag, instead of any properties currently stored on your PostHog server.

For example:

Node.js

```javascript
const flags = await client.evaluateFlags('distinct_id_of_the_user', {
    personProperties: {
        property_name: 'value',
    },
    groups: {
        your_group_type: 'your_group_id',
        another_group_type: 'your_group_id',
    },
    groupProperties: {
        your_group_type: {
            group_property_name: 'value',
        },
        another_group_type: {
            group_property_name: 'value',
        },
    },
})

if (flags.isEnabled('flag-key')) {
    // Do something differently for this user
}
```

### Overriding GeoIP properties

By default, a user's GeoIP properties are set using the IP address they use to capture events on the frontend. You may want to override the these properties when evaluating feature flags. A common reason to do this is when you're not using PostHog on your frontend, so the user has no GeoIP properties.

You can override GeoIP properties by including them in the `person_properties` parameter when evaluating feature flags. This is useful when you're evaluating flags on your backend and want to use the client's location instead of your server's location.

The following GeoIP properties can be overridden:

-   `$geoip_country_code`
-   `$geoip_country_name`
-   `$geoip_city_name`
-   `$geoip_city_confidence`
-   `$geoip_continent_code`
-   `$geoip_continent_name`
-   `$geoip_latitude`
-   `$geoip_longitude`
-   `$geoip_postal_code`
-   `$geoip_subdivision_1_code`
-   `$geoip_subdivision_1_name`
-   `$geoip_subdivision_2_code`
-   `$geoip_subdivision_2_name`
-   `$geoip_subdivision_3_code`
-   `$geoip_subdivision_3_name`
-   `$geoip_time_zone`

Simply include any of these properties in the `person_properties` parameter alongside your other person properties when calling feature flags.

### Request timeout

You can configure the `featureFlagsRequestTimeoutMs` parameter when initializing your PostHog client to set a flag request timeout. This helps prevent your code from being blocked if PostHog's servers are too slow to respond. By default, this is set to 3 seconds.

JavaScript

```javascript
const client = new PostHog('<ph_project_token>', {
    host: 'https://us.i.posthog.com',
    featureFlagsRequestTimeoutMs: 3000, // Time in milliseconds. Defaults to 3000 (3 seconds).
})
```

> **Note:** For remote config flags, see the [remote config documentation](/docs/feature-flags/remote-config.md). Remote config requires the [Feature Flags secure API key](/docs/feature-flags/remote-config.md#step-1-find-your-feature-flags-secure-api-key) passed as the `personalApiKey` option.

### Local evaluation

Evaluating feature flags requires making a request to PostHog for each flag. However, you can improve performance by evaluating flags locally. Instead of making a request for each flag, PostHog will periodically request and store feature flag definitions locally, enabling you to evaluate flags without making additional requests.

It is best practice to use local evaluation flags when possible, since this enables you to resolve flags faster and with fewer API calls.

For details on how to implement local evaluation, see our [local evaluation guide](/docs/feature-flags/local-evaluation.md).

Node.js

```javascript
const flags = await client.evaluateFlags('user distinct id', {
    groups: { organization: 'google' },
    groupProperties: { organization: { is_authorized: true } },
})

const flagValue = flags.getFlag('flag-key')
```

#### Reloading feature flags

When initializing PostHog, you can configure the interval at which feature flags are polled (fetched from the server). However, if you need to force a reload, you can use `reloadFeatureFlags`:

Node.js

```javascript
await client.reloadFeatureFlags()

// Do something with feature flags here
```

#### Distributed environments

In multi-worker or edge environments, you can implement custom caching for flag definitions using Redis, Cloudflare KV, or other storage backends. This enables sharing definitions across workers and coordinating fetches. See our guide for [local evaluation in distributed environments](/docs/feature-flags/local-evaluation/distributed-environments?tab=Node.js.md) for details.

## Experiments (A/B tests)

Since [experiments](/docs/experiments/start-here.md) use feature flags, the code for running an experiment is very similar to the feature flags code:

Node.js

```javascript
const flags = await client.evaluateFlags('user_distinct_id')
const variant = flags.getFlag('experiment-feature-flag-key')

if (variant === 'variant-name') {
  // Do something
}
```

It's also possible to [run experiments without using feature flags](/docs/experiments/running-experiments-without-feature-flags.md).

## Group analytics

Group analytics enable you to associate an event with a group (e.g. teams, organizations, etc.). Read the [group analytics guide](/docs/product-analytics/group-analytics.md) for more information.

To create a group or update its properties, use `groupIdentify`:

Node.js

```javascript
client.groupIdentify({
  groupType: 'company',
  groupKey: 'company_id_in_your_db',
  properties: {
    name: 'Awesome Inc',
    employees: 11,
  },
  // optional distinct ID to associate event with an existing person
  distinctId: 'xyz'
})
```

`name` is a special property which is used in the PostHog UI for the name of the group. If you don't specify a `name` property, the group ID is used instead.

If the optional `distinctId` parameter is not provided in the group identify call, it defaults to `${groupType}_${groupKey}` (e.g., `$company_company_id_in_your_db` in the example above). This default behavior results in each group appearing as a separate person in PostHog. To avoid this, it's often more practical to use a consistent `distinctId`, such as `group_identifier`.

Once a group is created, you can use the `capture` method and pass in the `groups` parameter to capture an event with group analytics.

Node.js

```javascript
client.capture({
  event: 'some_event',
  distinctId: 'user_distinct_id',
  groups: { company: 'company_id_in_your_db' },
})
```

## GeoIP properties

Before `posthog-node` v3.0, we added GeoIP properties to all incoming events by default. We also used these properties for feature flag evaluation, based on the IP address of the request. This isn't ideal since they are created based on your server IP address, rather than the user's, leading to incorrect location resolution.

As of `posthog-node` v3.0, the default now is to disregard the server IP, not add the GeoIP properties, and not use the values for feature flag evaluations.

You can go back to previous behavior by setting `disableGeoip` to false in your initialization:

Node.js

```javascript
const posthog = new PostHog('<ph_project_token>', {
  host: 'https://us.i.posthog.com',
  disableGeoip: false
})
```

The list of properties that this overrides:

1.  `$geoip_city_name`
2.  `$geoip_country_name`
3.  `$geoip_country_code`
4.  `$geoip_continent_name`
5.  `$geoip_continent_code`
6.  `$geoip_postal_code`
7.  `$geoip_time_zone`

You can also explicitly chose to enable or disable GeoIP for a single capture request like so:

Node.js

```javascript
client.capture({
  distinctId: distinctId,
  event: 'your_event',
  disableGeoip: `true`,
})
```

## Shutdown

You should call `shutdown` on your program's exit to exit cleanly:

Node.js

```javascript
// Stop pending pollers and flush any remaining events
await client.shutdown()
```

## Debug mode

If you're not seeing the expected events being captured, the feature flags being evaluated, or the surveys being shown, you can enable debug mode to see what's happening.

You can enable debug mode by calling the `debug()` method in your code. This will enable verbose logs about the inner workings of the SDK.

Node.js

```javascript
client.debug()
```

## Handling errors thrown by the SDK

If you are experiencing issues with the SDK it could be a number of things from an incorrectly configured API key, to some other network related issues.

The SDK does not throw errors for things happening in the background to ensure it doesn't affect your process. You can however hook into the errors to get more information:

Node.js

```javascript
client.on("error", (err) => {
  // Whatever handling you want
  console.error("PostHog had an error!", err)
})
```

## Short-lived processes like serverless environments

The Node SDK is designed to queue and batch requests in the background to optimize API calls and network time. As serverless environments like AWS Lambda or [Vercel Functions](/docs/libraries/vercel.md) are short-lived, we provide a few options to ensure all events are captured.

First, we recommend using the `captureImmediate` method instead of `capture` to ensure the event is captured before the function shuts down. It guarantees the HTTP request finishes before your function continues (or shuts down).

Second, we recommend setting `flushAt` to `1` and `flushInterval` to `0` to ensure the events are sent immediately. These set the queue to flush immediately, both in terms of events and time.

Third, we provide a method `shutdown()` which can be awaited to ensure all queued events are sent to the API. For example:

Node.js

```javascript
export const handler() {
  client.capture({
    distinctId: 'distinct_id_of_the_user',
    event: 'thing_happened'
  })

  client.capture({
    distinctId: 'distinct_id_of_the_user',
    event: 'other_thing_happened'
  })

  // So far 2 events are queued but not sent

  // Calling shutdown, flushed the queue but batched into 1 API call for maximum efficiency
  await client.shutdown()
}
```

This is also useful for shutting down a standard Node.js app.

## AI Observability

You can capture LLM usage and performance data by combining the `posthog-node` and `@posthog/ai` libraries. These work with LLM providers like OpenAI and Vercel's AI SDKs. Learn more in our [AI Observability docs](/docs/ai-observability.md).

## Error tracking

You can capture errors using the `posthog-node` library. This enables you to see stack traces, source code, and watch associated session recordings to improve your application stability. Learn more in our [error tracking docs](/docs/error-tracking/installation/node.md).

## Upgrading from V1 to V2

V2.x.x of the Node.js library is completely rewritten in Typescript and is based on a new JS core shared with other JavaScript based libraries with the goal of ensuring new features and fixes reach the different libraries at the same pace.

With the release of V2, the API was kept mostly the same but with some small changes and deprecations:

1.  The minimum PostHog version requirement is 1.38
2.  The `callback` parameter passed as an optional last argument to most of the methods is no longer supported
3.  The method signature for `isFeatureEnabled` and `getFeatureFlag` is slightly modified. See the above documentation for each method for more details.
4.  For specific changes, [see the CHANGELOG](https://github.com/PostHog/posthog-js/blob/main/packages/node/CHANGELOG.md)

### Still have questions?

Ask PostHog AI

### Was this page useful?

HelpfulCould be better