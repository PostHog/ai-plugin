> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Python

The Python SDK makes it easy to capture events, evaluate feature flags, track errors, and more in your Python apps.

> These docs cover version `7.x` of the Python SDK, which requires Python 3.10 or higher. On Python 3.9? See [supported versions](#supported-versions).

## Installation

Terminal

```bash
pip install posthog
```

**Upgrading to v6**

Version `6.x` of the PostHog Python SDK introduces a new [contexts](/docs/libraries/python.md#contexts) API and breaking changes. If you're upgrading from `5.x` to `6.x`, read the [migration guide](/tutorials/python-v6-migration.md) first to learn more.

In your app, import the `posthog` library and set your project token and host **before** making any calls.

Python

```python
from posthog import Posthog

posthog = Posthog('<ph_project_token>', host='https://us.i.posthog.com')
```

> **Note:** As a rule of thumb, we do not recommend having API keys or tokens in plaintext. Setting it as an environment variable is best.

You can find your project token and instance address in the [project settings](https://app.posthog.com/project/settings) page in PostHog.

## Use the asyncio client

The Python SDK includes an asyncio-native client in version `7.45.0` and later. Continue to use `Posthog` in synchronous apps. For an asyncio app, install the optional async dependencies:

Terminal

```bash
pip install "posthog[async]>=7.45.0"
```

Import `AsyncPosthog`, the customer-facing name for `AsyncClient`. Both names provide the same async context manager and lifecycle methods. Keep one client for the lifetime of your app. For example, use a FastAPI lifespan handler:

Python

```python
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from posthog import AsyncPosthog

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncPosthog(
        os.environ["POSTHOG_PROJECT_TOKEN"],
        host=os.environ["POSTHOG_HOST"],
        secret_key=os.environ.get("POSTHOG_FEATURE_FLAGS_SECURE_API_KEY"),
    ) as posthog:
        app.state.posthog = posthog
        yield

app = FastAPI(lifespan=lifespan)
```

Exiting the context calls `shutdown()`. This flushes buffered events, waits for in-flight operations, stops the workers, and closes the HTTP transport. If you don't use the context manager, call `await posthog.shutdown()` during app shutdown. `await posthog.join()` has the same effect.

### Capture events without blocking the event loop

`capture()` queues an event and returns without waiting for a network request. Don't await it:

Python

```python
posthog.capture(
    "event_name",
    distinct_id="user-distinct-id",
    properties={"source": "fastapi"},
)
```

Use `capture_immediate()` when your code must wait for that event's delivery attempt:

Python

```python
capture_id = await posthog.capture_immediate(
    "event_name",
    distinct_id="user-distinct-id",
)
```

### Evaluate feature flags

Await `evaluate_flags()` once, then use its snapshot with synchronous in-memory accessors. Pass the same snapshot to `capture()` to attach the exact values used for branching without another feature flag request:

Python

```python
flags = await posthog.evaluate_flags("user-distinct-id")

if flags.is_enabled("new-checkout"):
    # Show the new checkout
    pass

posthog.capture(
    "checkout started",
    distinct_id="user-distinct-id",
    flags=flags,
)
```

The snapshot provides synchronous `is_enabled()`, `get_flag()`, and `get_flag_payload()` accessors. The awaited `evaluate_flags()` call also accepts `groups`, `person_properties`, `group_properties`, `disable_geoip`, `flag_keys`, and `device_id` arguments.

### Fetch remote config

Initialize the client with a server-side [feature flags secure API key](/docs/feature-flags/remote-config.md#step-1-find-your-feature-flags-secure-api-key) as `secret_key`, then await the remote config request:

Python

```python
config = await posthog.get_remote_config_payload("landing-page-config")
```

See [Remote config](/docs/feature-flags/remote-config.md) for setup and security details.

## Identifying users

> **Identifying users is required.** Backend events need a `distinct_id` to associate events with the correct user.
>
> In Python, you can do this through a context. All event captures in the same context will be tagged automatically with the correct `distinct_id`. Typically, you would set a fresh context and identify at the top of each route.
>
> Python
>
> ```python
> from posthog import new_context, identify_context, capture
>
> @app.get("/foo")
> def foo(current_user: User = Depends(get_current_user)):
>     with new_context(): # Set context at the top of a route
>         identify_context(current_user.id)
>         capture("foo_viewed")
>     return {"status": "ok"}
> ```
>
> When possible, write a small piece of **middleware** that resolves your authenticated user, wrap a context around the request, and identifies it. Every `capture()` downstream is then attributed *automatically*. The SDK's Django middleware does this automatically and you can replicate it when using the plain Python SDK.

## Capturing events

You can send custom events using `capture`:

Python

```python
# Events captured with no context or explicit distinct_id are marked as personless and have an auto-generated distinct_id:
posthog.capture('some-anon-event')

from posthog import identify_context, new_context

# Use contexts to manage user identification across multiple capture calls
with new_context():
    identify_context('distinct_id_of_the_user')
    posthog.capture('user_signed_up')
    posthog.capture('user_logged_in')
    # You can also capture events with a specific distinct_id
    posthog.capture('some-custom-action', distinct_id='distinct_id_of_the_user')
```

> **Tip:** We recommend using a `[object] [verb]` format for your event names, where `[object]` is the entity that the behavior relates to, and `[verb]` is the behavior itself. For example, `project created`, `user signed up`, or `invite sent`.

> **Tip:** You can define event schemas with typed properties and generate type-safe code using [schema management](/docs/product-analytics/schema-management.md).

### Setting event properties

Optionally, you can include additional information with the event by including a [properties](/docs/data/events.md#event-properties) object:

Python

```python
posthog.capture(
    "user_signed_up",
    distinct_id="distinct_id_of_the_user",
    properties={
        "login_type": "email",
        "is_free_trial": "true"
    }
)
```

### Sending page views

If you're aiming for a backend-only implementation of PostHog and won't be capturing events from your frontend, you can send `pageviews` from your backend like so:

Python

```python
posthog.capture('$pageview', distinct_id="distinct_id_of_the_user", properties={'$current_url': 'https://example.com'})
```

## Person profiles and properties

The Python SDK captures identified events if the current context is identified or if you pass a distinct ID explicitly. These create [person profiles](/docs/data/persons.md). To set [person properties](/docs/product-analytics/person-properties.md) in these profiles, include them when capturing an event:

Python

```python
# Passing a distinct id explicitly
posthog.capture(
    'event_name',
    distinct_id='user-distinct-id',
    properties={
        '$set': {'name': 'Max Hedgehog'},
        '$set_once': {'initial_url': '/blog'}
    }
)

# Using contexts
from posthog import new_context, identify_context
with new_context():
    identify_context('user-distinct-id')
    posthog.capture('event_name')
```

For more details on the difference between `$set` and `$set_once`, see our [person properties docs](/docs/product-analytics/person-properties.md#what-is-the-difference-between-set-and-set_once).

To capture [anonymous events](/docs/data/anonymous-vs-identified-events.md) without person profiles, set the event's `$process_person_profile` property to `False`. Events captured with no context or explicit distinct\_id are marked as personless, and will have an auto-generated distinct\_id:

Python

```python
posthog.capture(
    event='event_name',
    properties={
        '$process_person_profile': False
    }
)
```

## Alias

Sometimes, you want to assign multiple distinct IDs to a single user. This is helpful when your primary distinct ID is inaccessible. For example, if a distinct ID used on the frontend is not available in your backend.

In this case, you can use `alias` to assign another distinct ID to the same user.

Python

```python
posthog.alias(previous_id='distinct_id', distinct_id='alias_id')
```

We strongly recommend reading our docs on [alias](/docs/product-analytics/identify.md#alias-assigning-multiple-distinct-ids-to-the-same-user) to best understand how to correctly use this method.

## Contexts

The Python SDK uses nested contexts for managing state that's shared across events. Contexts are the recommended way to manage things like "which user is taking this action" (through `identify_context`), rather than manually passing user state through your apps stack.

When events (including exceptions) are captured in a context, the event uses the user [distinct ID](/docs/getting-started/identify-users.md), [session ID](/docs/data/sessions.md), and tags that are (optionally) set in the context. This is useful for adding properties to multiple events during a single user's interaction with your product.

You can enter a context using the `with` statement:

Python

```python
from posthog import new_context, tag, set_context_session, identify_context

with new_context():
    tag("transaction_id", "abc123")
    tag("some_arbitrary_value", {"tags": "can be dicts"})

    # Sessions are UUIDv7 values and used to track a sequence of events that occur within a single user session
    # See https://posthog.com/docs/data/sessions
    set_context_session(session_id)

    # Setting the context-level distinct ID. See below for more details.
    identify_context(user_id)

    # This event is captured with the distinct ID, session ID, and tags set above
    posthog.capture("order_processed")
```

Contexts are persisted across function calls. If you enter one and then call a function and capture an event in the called function, it uses the context tags and session ID set in the parent context:

Python

```python
from posthog import new_context, tag

def some_function():
    # When called from `outer_function`, this event is captured with the property some-key="value-4"
    posthog.capture("order_processed")


def outer_function():
    with new_context():
        tag("some-key", "value-4")
        some_function()
```

Contexts are nested, so tags added to a parent context are inherited by child contexts. If you set the same tag in both a parent and child context, the child context's value overrides the parent's at event capture (but the parent context won't be affected). This nesting also applies to session IDs and distinct IDs.

Python

```python
from posthog import new_context, tag

with new_context():
    tag("some-key", "value-1")
    tag("some-other-key", "another-value")
    with new_context():
        tag("some-key", "value-2")
        # This event is captured with some-key="value-2" and some-other-key="another-value"
        posthog.capture("order_processed")

    # This event is captured with some-key="value-1" and some-other-key="another-value"
    posthog.capture("order_processed")
```

You can disable this nesting behavior by passing `fresh=True` to `new_context`:

Python

```python
from posthog import new_context, tag

with new_context(fresh=True):
    tag("some-key", "value-2")
    # This event only has the property some-key="value-2" from the fresh context
    posthog.capture("order_processed")
```

> **Note:** Distinct IDs, session IDs, and properties passed directly to calls to `capture` and related functions override context state in the final event captured.

### Contexts and user identification

Contexts can be associated with a distinct ID by calling `posthog.identify_context`:

Python

```python
from posthog import identify_context

identify_context("distinct-id")
```

Within a context associated with a distinct ID, all events captured are associated with that user. You can override the distinct ID for a specific event by passing a `distinct_id` argument to `capture`:

Python

```python
from posthog import new_context, identify_context

with new_context():
    identify_context("distinct-id")
    posthog.capture("order_processed") # will be associated with distinct-id
    posthog.capture("order_processed", distinct_id="another-distinct-id") # will be associated with another-distinct-id
```

It's recommended to pass the currently active distinct ID from the frontend to the backend, using the `X-POSTHOG-DISTINCT-ID` header. If you're using our Django middleware, this is extracted and associated with the request handler context automatically.

You can read more about identifying users in the [user identification documentation](/docs/product-analytics/identify.md).

### Contexts and sessions

Contexts can be associated with a session ID by calling `posthog.set_context_session`. When linking backend events to frontend sessions, use the session ID from the frontend SDK (PostHog session IDs are UUIDv7 strings).

Python

```python
from posthog import new_context, set_context_session
with new_context():
    set_context_session(request.get_header("X-POSTHOG-SESSION-ID"))
```

**Using PostHog on your frontend too?**

If you're using the PostHog JavaScript Web SDK on your frontend, it generates a session ID for you. Configure [`tracing_headers`](/docs/libraries/js/config.md#tracing-headers) for your backend hostname to add the session and distinct ID headers to browser requests automatically.

You need to extract the header in your request handler (if you're using our Django middleware integration, this happens automatically).

If you associate a context with a session, you'll be able to do things like:

-   See backend events on the session timeline when viewing session replays
-   View session replays for users that triggered a backend exception in error tracking

You can read more about sessions in the [session tracking](/docs/data/sessions.md) documentation.

### Exception capture

By default exceptions raised within a context are captured and available in the [error tracking](/docs/error-tracking.md) dashboard. You can override this behavior by passing `capture_exceptions=False` to `new_context`:

Python

```python
from posthog import new_context, tag

with new_context(capture_exceptions=False):
    tag("transaction_id", "abc123")
    tag("some_arbitrary_value", {"tags": "can be dicts"})

    # This event will be captured with the tags set above
    posthog.capture("order_processed")
    # This exception will not be captured
    raise Exception("Order processing failed")
```

### Decorating functions

The SDK exposes a function decorator. It takes the same `fresh` and `capture_exceptions` arguments as `new_context` and provides a handy way to mark a whole function as being in a new context. For example:

Python

```python
from posthog import scoped, identify_context

@scoped(fresh=True)
def process_order(user, order_id):
    identify_context(user.distinct_id)
    posthog.capture("order_processed") # Associated with the user
    raise Exception("Order processing failed") # This exception is also captured and associated with the user
```

## Group analytics

Group analytics allows you to associate an event with a group (e.g. teams, organizations, etc.). Read the [Group Analytics](/docs/user-guides/group-analytics.md) guide for more information.

> **Note:** This is a paid feature and is not available on the open-source or free cloud plan. Learn more on our [pricing page](/pricing.md).

To capture an event and associate it with a group:

Python

```python
posthog.capture('some_event', groups={'company': 'company_id_in_your_db'})
```

To update properties on a group:

Python

```python
posthog.group_identify('company', 'company_id_in_your_db', {
    'name': 'Awesome Inc.',
    'employees': 11
})
```

The `name` is a special property which is used in the PostHog UI for the name of the group. If you don't specify a `name` property, the group ID will be used instead.

## Feature flags

The examples in this section use the synchronous `Posthog` client. For `AsyncPosthog`, use the [awaited feature flag example](#evaluate-feature-flags). The returned snapshot uses the same accessors.

PostHog's [feature flags](/docs/feature-flags.md) enable you to safely deploy and roll back new features as well as target specific users and groups with them.

There are two steps to implement feature flags in Python:

### Step 1: Evaluate flags once

Call `posthog.evaluate_flags()` once for the user, then read values from the returned snapshot.

#### Boolean feature flags

Python

```python
flags = posthog.evaluate_flags("distinct_id_of_your_user")

if flags.is_enabled("flag-key"):
    # Do something differently for this user
    # Optional: fetch the payload
    matched_flag_payload = flags.get_flag_payload("flag-key")
```

#### Multivariate feature flags

Python

```python
flags = posthog.evaluate_flags("distinct_id_of_your_user")

enabled_variant = flags.get_flag("flag-key")

if enabled_variant == "variant-key":  # replace "variant-key" with the key of your variant
    # Do something differently for this user
    # Optional: fetch the payload
    matched_flag_payload = flags.get_flag_payload("flag-key")
```

`flags.get_flag()` returns the variant string for multivariate flags, `True` for enabled boolean flags, `False` for disabled flags, and `None` when the flag wasn't returned by the evaluation.

> **Note:** `posthog.feature_enabled()`, `posthog.get_feature_flag()`, `posthog.get_feature_flag_payload()`, and `posthog.capture(send_feature_flags=True)` still work during the migration period, but they're deprecated. Prefer `posthog.evaluate_flags()` for new code.

### Step 2: Include feature flag information when capturing events

If you want use your feature flag to breakdown or filter events in your [insights](/docs/product-analytics/insights.md), you'll need to include feature flag information in those events. This ensures that the feature flag value is attributed correctly to the event.

> **Note:** This step is only required for events captured using our server-side SDKs or [API](/docs/api.md).

There are two methods you can use to include feature flag information in your events:

#### Method 1: Pass the evaluated flags snapshot to `capture()`

Pass the same `flags` object that you used for branching. This attaches the exact flag values from that evaluation and doesn't make another `/flags` request.

Python

```python
flags = posthog.evaluate_flags("distinct_id_of_your_user")

if flags.is_enabled("flag-key"):
    # Do something differently for this user
    pass

posthog.capture(
    "event_name",
    distinct_id="distinct_id_of_your_user",
    flags=flags,
)
```

By default, this attaches every flag in the snapshot using `$feature/<flag-key>` properties and `$active_feature_flags`.

To reduce event property bloat, pass a filtered snapshot:

Python

```python
# Attach only flags accessed with is_enabled() or get_flag() before this call
posthog.capture(
    "event_name",
    distinct_id="distinct_id_of_your_user",
    flags=flags.only_accessed(),
)

# Attach only specific flags
posthog.capture(
    "event_name",
    distinct_id="distinct_id_of_your_user",
    flags=flags.only(["checkout-flow", "new-dashboard"]),
)
```

`only_accessed()` is order-dependent. If you call it before accessing any flags with `is_enabled()` or `get_flag()`, no feature flag properties are attached.

#### Method 2: Include the `$feature/feature_flag_name` property manually

In the event properties, include `$feature/feature_flag_name: variant_key`:

Python

```python
posthog.capture(
    "event_name",
    distinct_id="distinct_id_of_the_user",
    properties={
        # Replace feature-flag-key with your flag key and "variant-key" with the key of your variant
        "$feature/feature-flag-key": "variant-key",
    },
)
```

### Evaluating only specific flags

By default, `posthog.evaluate_flags()` evaluates every flag for the user. If you only need a few flags, pass `flag_keys` to request only those flags:

Python

```python
flags = posthog.evaluate_flags(
    "distinct_id_of_your_user",
    flag_keys=["checkout-flow", "new-dashboard"],
)
```

### Sending `$feature_flag_called` events

Capturing `$feature_flag_called` events enables PostHog to know when a flag was accessed by a user and provide [analytics and insights](/docs/product-analytics/insights.md) on the flag. With `posthog.evaluate_flags()`, the SDK sends this event when you call `flags.is_enabled()` or `flags.get_flag()` for a flag.

The SDK deduplicates these events per `(distinct_id, flag, value)` in a local cache. If you reinitialize the PostHog client, the cache resets and `$feature_flag_called` events may be sent again. PostHog handles duplicates, so duplicate `$feature_flag_called` events don't affect your analytics.

`flags.get_flag_payload()` doesn't send `$feature_flag_called` events and doesn't count as an access for `only_accessed()`.

### Advanced: Overriding server properties

Sometimes, you may want to evaluate feature flags using [person properties](/docs/product-analytics/person-properties.md), [groups](/docs/product-analytics/group-analytics.md), or group properties that haven't been ingested yet, or were set incorrectly earlier.

You can provide properties to evaluate the flag with by using the `person properties`, `groups`, and `group properties` arguments. PostHog will then use these values to evaluate the flag, instead of any properties currently stored on your PostHog server.

For example:

Python

```python
flags = posthog.evaluate_flags(
    "distinct_id_of_the_user",
    person_properties={"property_name": "value"},
    groups={
        "your_group_type": "your_group_id",
        "another_group_type": "your_group_id",
    },
    group_properties={
        "your_group_type": {"group_property_name": "value"},
        "another_group_type": {"group_property_name": "value"},
    },
)

if flags.is_enabled("flag-key"):
    # Do something differently for this user
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

You can configure the `feature_flags_request_timeout_seconds` parameter when initializing your PostHog client to set a flag request timeout. This helps prevent your code from being blocked if PostHog's servers are too slow to respond. By default, this is set to 3 seconds.

Python

```python
posthog = Posthog(
    "<ph_project_token>",
    host="https://us.i.posthog.com",
    feature_flags_request_timeout_seconds=3,  # Time in seconds. Defaults to 3.
)
```

### Local evaluation

Evaluating feature flags requires making a request to PostHog for each flag. However, you can improve performance by evaluating flags locally. Instead of making a request for each flag, PostHog will periodically request and store feature flag definitions locally, enabling you to evaluate flags without making additional requests.

It is best practice to use local evaluation flags when possible, since this enables you to resolve flags faster and with fewer API calls.

For details on how to implement local evaluation, see our [local evaluation guide](/docs/feature-flags/local-evaluation.md).

#### Distributed environments

In multi-worker or edge environments, you can implement custom caching for flag definitions using Redis, Cloudflare KV, or other storage backends. This enables sharing definitions across workers and coordinating fetches. See our guide for [local evaluation in distributed environments](/docs/feature-flags/local-evaluation/distributed-environments?tab=Python.md) for details.

## Experiments (A/B tests)

Since [experiments](/docs/experiments/start-here.md) use feature flags, the code for running an experiment is very similar to the feature flags code. This example uses the synchronous `Posthog` client:

Python

```python
flags = posthog.evaluate_flags("user_distinct_id")
variant = flags.get_flag("experiment-feature-flag-key")

if variant == "variant-name":
    # Do something
```

With `AsyncPosthog`, await the evaluation: `flags = await posthog.evaluate_flags("user_distinct_id")`. The remaining snapshot access is the same.

It's also possible to [run experiments without using feature flags](/docs/experiments/running-experiments-without-feature-flags.md).

## AI Observability

Our Python SDK includes a built-in AI Observability feature. It enables you to capture LLM usage, performance, and more. Check out our [analytics docs](/docs/ai-observability.md) for more details on setting it up.

## Error tracking

You can [autocapture exceptions](/docs/error-tracking/installation.md) by setting the `enable_exception_autocapture` argument to `True` when initializing the PostHog client.

Python

```python
from posthog import Posthog

posthog = Posthog("<ph_project_token>", enable_exception_autocapture=True, ...)
```

You can also manually capture exceptions using the `capture_exception` method:

Python

```python
posthog.capture_exception(e, distinct_id='user_distinct_id', properties=additional_properties)
```

Contexts automatically capture exceptions thrown inside them, unless disable it by passing `capture_exceptions=False` to `new_context()`.

### Code variables capture

The Python SDK can automatically capture the state of local variables when an exception occurs. This gives you a debugger-like view of your application state at the time of the error:

Python

```python
posthog = Posthog(
    "<ph_project_token>",
    enable_exception_autocapture=True,
    capture_exception_code_variables=True,
)
```

You can configure which variables are captured, masked, or ignored. See the [code variables documentation](/docs/error-tracking/code-variables/python.md) for detailed configuration options.

## Distributed tracing

> Requires `posthog` version 7.58.0 or later.

**The span API is experimental**

Tracing is new in the Python SDK and its API can still change in a minor release. Spans you send are kept – it's the SDK surface that isn't frozen yet.

Tracing records **spans** – timed units of work – so you can see where time went in a request and how work fans out across your services. Spans created inside a [context](#contexts) automatically carry the person and session they belong to, so a slow trace links back to the person who experienced it.

Tracing is off until you set the `traces` option. No OpenTelemetry dependency is required. For what you can do with spans once they arrive, see [Distributed tracing](/docs/distributed-tracing/start-here.md).

Python

```python
from posthog import Posthog

posthog = Posthog(
    "<ph_project_token>",
    host="https://us.i.posthog.com",
    traces={"service_name": "checkout-api"},
)
```

If you use the module-level API instead, set `posthog.traces = {"service_name": "checkout-api"}` alongside your other options, before you start the first span.

Set `service_name` – PostHog groups operations by service and span name.

Tracing is available on the synchronous `Posthog` client and the module-level API. `AsyncPosthog` doesn't support it yet.

### Creating spans

`start_span` returns a span. Use it in a `with` block to make it the active span for the block and end it when the block exits. Spans started inside the block nest underneath it automatically.

Python

```python
with posthog.start_span("POST /checkout", kind="server") as span:
    span.set_attribute("plan", user.plan)

    with posthog.start_span("create-order"):
        order = create_order(cart)
    with posthog.start_span("charge-card"):
        stripe.charge(order)
```

If an exception escapes the block, the span records it, its status is set to `error`, and the exception propagates unchanged. `KeyboardInterrupt`, `GeneratorExit`, and `asyncio.CancelledError` still end the span but aren't recorded as failures.

The recorded exception includes the stack trace, which contains file paths from your server. If you'd rather those didn't leave your process, remove `exception.stacktrace` in [`before_span_send`](#scrubbing-and-dropping-spans).

For work that can't wrap a block, call `start_span` without `with`. **A span started this way isn't active**, so spans started afterwards aren't its children unless you pass `parent` explicitly – and you must call `end()` yourself.

Python

```python
span = posthog.start_span("background-sync", attributes={"queue": "emails"})
try:
    # Explicitly parent a child to a span that isn't active.
    child = posthog.start_span("send-batch", parent=span)
    child.end()
finally:
    span.end()
```

`get_active_span()` returns the span active in the current context, or `None` when there isn't one.

The active span is tracked with [`contextvars`](https://docs.python.org/3/library/contextvars.html), so it carries across `await` in asyncio code. Threads don't reliably inherit it – pass `parent=span` to continue the trace in a thread you start or a `ThreadPoolExecutor` task. A forked child process starts with no active span, so pass `parent` there too.

`start_span` always returns a usable span, even when tracing is off, so your code never needs to check whether tracing is enabled.

### Span names and attributes

Span names should be low-cardinality operation names – `GET /users/:id`, not `GET /users/123`. Variable values belong in attributes. Strings, booleans, integers, and floats keep their type. Lists and dictionaries are sent as arrays and maps, but PostHog stores them as serialized strings. Setting an attribute to `None` removes it, and any other value is converted to a string.

Python

```python
with posthog.start_span("GET /users/:id", kind="server") as span:
    span.set_attributes({"user.id": user_id, "db.rows": len(rows)})
    span.add_event("cache-miss")

    if not rows:
        span.set_status("error", "user not found")
```

| Method | Description |
| --- | --- |
| `set_attribute(key, value)` | Set a single attribute |
| `set_attributes(attributes)` | Merge several attributes at once |
| `add_event(name, attributes=None, timestamp=None)` | Record a timestamped event within the span |
| `set_status(code, message=None)` | Set the outcome: `"ok"` or `"error"`. `"ok"` is final – an exception raised later in the `with` block doesn't override it |
| `record_exception(exception)` | Attach an exception event carrying the type, message, and – for a raised exception – stack trace, and set status to `error`. Use it for exceptions you catch and handle |
| `update_name(name)` | Replace the span name, e.g. once a route template resolves |
| `traceparent()` | This span's W3C `traceparent` header value, or `None` |
| `tracestate()` | This span's W3C `tracestate` value, or `None` when it has none |
| `end(end_time=None)` | End the span and queue it for export. A `with` block does this for you |

Every method except `traceparent()`, `tracestate()`, and `end()` returns the span, so calls chain. Calls after `end()` are ignored.

`start_span` takes these keyword arguments:

| Argument | Description |
| --- | --- |
| `kind` | What the work is: `"internal"` (default), `"server"` for an inbound request, `"client"` for an outbound call, `"producer"` or `"consumer"` for queue work |
| `attributes` | Attributes to set at span start |
| `parent` | A span, or an inbound W3C `traceparent` string to continue a trace another service started. Defaults to the active span |
| `tracestate` | The W3C `tracestate` accompanying a `traceparent` string. Ignored when `parent` is a span, which inherits its parent's |
| `start_time` | Backdate the span's start, as a `datetime` or seconds since the epoch. The server clamps a start more than 24 hours old to receive time; with `debug` on, the SDK prints a debug message when you pass one |

### Tracing across services

Spans use [W3C Trace Context](https://www.w3.org/TR/trace-context/), so a trace can span several services. Pass an inbound `traceparent` header as `parent` to continue a trace another service started, and send `span.traceparent()` onward when you call out.

app.py

```python
import requests
from flask import request


@app.post("/checkout")
def checkout():
    with posthog.start_span(
        "POST /checkout",
        kind="server",
        parent=request.headers.get("traceparent"),
    ) as span:
        traceparent = span.traceparent()

        requests.post(
            "https://payments.internal/charge",
            headers={"traceparent": traceparent} if traceparent else {},
        )

        return {"status": "ok"}
```

A malformed `traceparent` starts a new trace rather than raising. A missing one (`None`) falls back to the active span, if there is one.

A continued trace propagates the sampled flag it was handed, so a downstream sampler sees the decision the head service made. PostHog itself doesn't sample – a span is recorded and exported whichever way that flag is set.

### Linking traces to people and sessions

Spans created inside a [context](#contexts) that has a distinct ID or session ID automatically carry `posthogDistinctId` and `sessionId` attributes, which is what makes a trace reachable from a person or a Session Replay recording. In Django, the [contexts middleware](/docs/libraries/django.md#django-contexts-middleware) sets these for every request. Elsewhere, set them yourself:

Python

```python
from posthog import new_context, identify_context, set_context_session

with new_context():
    identify_context(user.id)
    set_context_session(session_id)

    with posthog.start_span("POST /checkout"):
        process_order()
```

Spans created outside a context with those values omit the attributes.

### Scrubbing and dropping spans

`before_span_send` runs on every finished span before it's queued for export. It receives the span as a dict with `name`, `kind`, `status`, `attributes`, `events`, `start_time_ns`, `end_time_ns`, `trace_id`, `span_id`, and `parent_span_id`. Edit it and return it, or return `None` to drop the span entirely.

Python

```python
def scrub_spans(span):
    if span["attributes"].get("http.route") == "/health":
        return None

    span["attributes"].pop("http.request.header.authorization", None)
    return span


posthog = Posthog(
    "<ph_project_token>",
    host="https://us.i.posthog.com",
    traces={
        "service_name": "checkout-api",
        "before_span_send": scrub_spans,
    },
)
```

Attributes are plain Python values, not the OTLP wire encoding. The hook runs after PostHog attaches `posthogDistinctId` and `sessionId`, so those are visible to the hook and can be scrubbed too. An exception's stack trace is on its event, under `event["attributes"]["exception.stacktrace"]`.

-   `trace_id`, `span_id`, and `parent_span_id` are read-only. Rewriting them would orphan child spans that have already been exported, so changes are reverted.
-   A hook that raises drops the span rather than exporting it without scrubbing.
-   Pass a list to run several hooks in order. The first one to return `None` stops the chain.
-   The hook must be a regular function. An `async` hook drops every span.
-   If an entry isn't callable, tracing turns off for the client rather than exporting spans the hook was meant to scrub.

### Span limits

A span is capped at 128 attributes and 128 events, each event at 128 attributes, and each string attribute value at 8192 characters. The endpoint rejects a span that's too large, and a rejected span is lost whole rather than truncated, so the caps bound a span before it gets there.

Past the cap, the earliest attributes and events are kept and the number dropped is reported alongside the span, so a truncated span reads as truncated rather than as quietly incomplete. The attributes PostHog attaches itself – `posthogDistinctId` and `sessionId` – don't count toward the cap and are never dropped, so a span at the limit still links back to its person and session.

The event cap is absolute: an `exception` event the SDK records for you spends an ordinary slot like any other. A span that fills its events and then raises keeps its `error` status but not the exception detail, and reports the loss as a dropped event. Raise `max_events_per_span` on spans that record many events and can also fail.

The length bound reaches inside a value, including strings nested in lists and dictionaries, and applies to `exception.stacktrace` like any other attribute – a long stack trace keeps its last 8192 characters. All four caps are re-applied after `before_span_send`, so a hook that enriches a span can't push it back over.

### Configuration

| Option | Default | Description |
| --- | --- | --- |
| `service_name` | – | Name of the service producing spans. Set this |
| `service_version` | – | Version of the service |
| `environment` | – | Deployment environment, e.g. `production` |
| `resource_attributes` | – | Extra OTLP resource attributes. Takes precedence over the fields above |
| `flush_interval` | `5` | Seconds between exports of queued spans |
| `max_export_batch_size` | `512` | Maximum spans per request |
| `max_queue_size` | `2048` | Maximum spans held in memory. Spans beyond this are dropped |
| `max_live_spans` | `10000` | Maximum spans open at once. At the limit `start_span` returns a span that isn't recorded |
| `max_span_age` | `3600` | Once `max_live_spans` is reached, spans open longer than this many seconds are treated as leaked and never exported |
| `before_span_send` | – | Edit or drop each finished span before export. Return `None` to drop it |
| `max_attributes_per_span` | `128` | Maximum attributes you set on one span |
| `max_events_per_span` | `128` | Maximum events on one span |
| `max_attribute_value_length` | `8192` | Maximum characters in a string attribute value |

An invalid value falls back to its default with a warning. The exception is `before_span_send`: an entry that isn't callable turns tracing off.

### Shutdown and short-lived processes

Spans are exported on a background interval, even with `sync_mode` on. Both `flush()` and `shutdown()` export spans that have already ended. A span still open at `flush()` is exported once it ends; a span still open at `shutdown()` is discarded with a warning, so end your spans before shutting down – a `with` block does this for you. `shutdown()` gives queued spans up to 30 seconds to send.

In a serverless handler, call `flush()` before returning. Events and spans are flushed concurrently, so it costs one round trip, not two.

Python

```python
def handler(event, context):
    with posthog.start_span("handler"):
        do_work()
    posthog.flush()
```

A script that exits without calling `shutdown()` still gets a brief best-effort flush at exit, but don't rely on it for spans you need.

## GeoIP properties

Before posthog-python v3.0, we added GeoIP properties to all incoming events by default. We also used these properties for feature flag evaluation, based on the IP address of the request. This isn't ideal since they are created based on your server IP address, rather than the user's, leading to incorrect location resolution.

As of posthog-python v3.0, the default now is to disregard the server IP, not add the GeoIP properties, and not use the values for feature flag evaluations.

You can go back to previous behavior by doing setting the `disable_geoip` argument in your initialization to `False`:

Python

```python
posthog = Posthog('api_key', disable_geoip=False)
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

Python

```python
posthog.capture('test_event', disable_geoip=True|False)
```

## Debug mode

If you're not seeing the expected events being captured, the feature flags being evaluated, or the surveys being shown, you can enable debug mode to see what's happening.

You can enable debug mode by setting the `debug` option to `True` in the `PostHog` object. This will enable verbose logs about the inner workings of the SDK.

Python

```python
posthog.debug = True
```

## Disabling requests during tests

You can disable requests during tests by setting the `disabled` option to `True` in the `PostHog` object. This means no events will be captured or no requests will be sent to PostHog.

Python

```python
if settings.TEST:
    posthog.disabled = True
```

## Connection configuration

The SDK uses HTTP connection pooling internally for better performance. These settings typically need not be changed, but in some environments, such as when running behind NAT gateways, pooled connections may be terminated non-gracefully, causing request failures.

You can configure connection behavior in several ways. The following settings should be called during initialization, before any API requests are made.

### Enable TCP keepalive

TCP keepalive probes help prevent idle connections from being dropped by network infrastructure. This is the recommended approach for most cases where idle connections are terminated.

Python

```python
import posthog

posthog.enable_keep_alive()
```

This enables TCP keepalive with sensible defaults (60 second idle time, 60 second probe interval, 3 probes before timeout).

### Disable connection pooling

If you need each request to use a fresh connection, you can disable connection reuse entirely. This will incur additional overhead per request but may be desirable in some circumstances.

Python

```python
import posthog

posthog.disable_connection_reuse()
```

### Custom HTTP socket options

For advanced use cases, you can configure arbitrary socket options on the underlying HTTP connection.

Python

```python
import socket
import posthog

posthog.set_socket_options([
    (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
    # Add additional socket options as needed
])
```

Pass `None` to `set_socket_options()` to reset to default behavior.

## Filtering or modifying events before sending

Use `before_send` to modify or drop events before they are queued for delivery. Return the modified event dictionary to send it, or `None` to drop it.

Python

```python
from typing import Any

import posthog


def scrub_pii(event: dict[str, Any]) -> dict[str, Any] | None:
    properties = event.get("properties", {})

    if "email" in properties:
        email = properties["email"]
        properties["email"] = f"***@{email.split('@', 1)[1]}" if "@" in email else "***"

    if event.get("event") == "test_event":
        return None

    return event


client = posthog.Client(
    "<ph_project_api_key>",
    before_send=scrub_pii,
)
```

If your callback raises an exception, the SDK logs the error and continues with the original unmodified event.

## Historical migrations

You can use the Python or Node SDK to run [historical migrations](/docs/migrate.md) of data into PostHog. To do so, set the `historical_migration` option to `true` when initializing the client.

### Python

```python
from posthog import Posthog
from datetime import datetime

posthog = Posthog(
    '<ph_project_token>',
    host='https://us.i.posthog.com',
    debug=True,
    historical_migration=True
)

events = [
  {
    "event": "batched_event_name",
    "distinct_id": "user_id",
    "timestamp": datetime.fromisoformat("2024-04-02T12:00:00+00:00"),
    "properties": {"account_type": "pro"}
  },
  {
    "event": "batched_event_name",
    "distinct_id": "user_id",
    "timestamp": datetime.fromisoformat("2024-04-03T09:30:00+00:00"),
    "properties": {"account_type": "pro"}
  }
]

for event in events:
  posthog.capture(
    event["event"],
    distinct_id=event["distinct_id"],
    properties=event["properties"],
    timestamp=event["timestamp"],
  )

posthog.shutdown()
```

### Node.js

```javascript
import { PostHog } from 'posthog-node'

const client = new PostHog(
    '<ph_project_token>',
    {
      host: 'https://us.i.posthog.com',
      historicalMigration: true
    }
)

client.debug()

client.capture({
    event: "batched_event_name",
    distinctId: "user_id",
    properties: {},
    timestamp: new Date("2024-04-03T12:00:00Z")
})

client.capture({
    event: "batched_event_name",
    distinctId: "user_id",
    properties: {},
    timestamp: new Date("2024-04-03T13:00:00Z")
})

await client.shutdown()
```

## Serverless environments (Render/Lambda/...)

### Synchronous `Posthog`

By default, the synchronous `Posthog` client buffers events before sending them to the capture endpoint. This can lead to lost events if the platform terminates the Python process before the buffer is fully flushed. To avoid this, you can either:

-   Call `posthog.shutdown()` before the process ends. This blocking call attempts to deliver queued events and cleans up the client.
-   Enable `sync_mode` when initializing the client so each `posthog.capture()` call attempts delivery before it returns.

If you use [distributed tracing](#distributed-tracing), `sync_mode` doesn't apply to spans. Call `posthog.flush()` before the handler returns – see [Shutdown and short-lived processes](#shutdown-and-short-lived-processes).

### Asyncio `AsyncPosthog`

Keep one `AsyncPosthog` client for the lifetime of your application. Use buffered `capture()` by default, or `await capture_immediate()` when one invocation must wait for an event's delivery attempt. Call `await posthog.shutdown()` once during application cleanup. Don't shut down the client after each request.

## Django

See our [Django docs](/docs/libraries/django.md) for how to set up PostHog in Django. Our library includes a [contexts middleware](/docs/libraries/django.md#django-contexts-middleware) that can automatically capture distinct IDs, session IDs, and other properties you can set up with tags.

## Alternative name

As our open source project [PostHog](https://github.com/PostHog/posthog) shares the same module name, we created a special `posthoganalytics` package, mostly for internal use to avoid module collision. It is the exact same.

## Thank you

This library is largely based on the `analytics-python` package.

## Supported versions

These docs cover version `7.x` of the PostHog Python SDK, which requires Python 3.10 or higher. Python 3.9 is no longer supported on `7.x.x` and higher — pin to the 6.x line with `pip install 'posthog<7'`, where `6.9.3` is the final release.

Everything on this page works the same way on `6.9.3`. Event capture, the context API (`new_context`, `identify_context`, `set_context_session`), and `PosthogContextMiddleware` are identical on `6.9.3` and `7.0.0` — `7.0.0` only dropped Python 3.9 and bumped the optional LLM provider SDKs. That includes the middleware identifying the request context from the `X-POSTHOG-DISTINCT-ID` header and falling back to the authenticated user, which behaves the same across both lines.

Later `7.x` releases add what the 6.x line does not receive, such as the Celery integration, tracing header sanitization, and `set_context_device_id`. They also changed the middleware's own captured properties: `7.x` sends the request IP as `$ip`, where `6.9.3` sends it as `$ip_address`, and `7.x` additionally captures `$request_path`, `$raw_user_agent`, and the authenticated user's `email`.

### Still have questions?

Ask PostHog AI

### Was this page useful?

HelpfulCould be better