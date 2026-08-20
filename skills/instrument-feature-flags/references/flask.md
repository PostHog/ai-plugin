> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Flask - Docs

Copy page

# Flask - Docs

PostHog makes it easy to get data about traffic and usage of your Flask app. Integrating PostHog enables analytics, custom events capture, feature flags, error tracking, and more.

This guide walks you through integrating PostHog into your Flask app using the [Python SDK](/docs/libraries/python.md).

> These docs cover version `7.x` of the Python SDK, which requires Python 3.10 or higher. On Python 3.9? See [supported versions](#supported-versions).

## Installation

To start, run `pip install posthog` to install PostHog’s Python SDK.

Then, initialize PostHog where you'd like to use it. For example, here's how to capture an event in a simple route:

app.py

PostHog AI

```python
from flask import Flask
from posthog import Posthog
app = Flask(__name__)
posthog = Posthog(
    '<ph_project_token>',
    host='https://us.i.posthog.com',
)
@app.route('/api/dashboard', methods=['POST'])
def api_dashboard():
    posthog.capture(
        'dashboard_api_called',
        distinct_id='distinct_id_of_your_user',
    )
    return '', 204
```

You can find your project token and instance address in [your project settings](https://app.posthog.com/project/settings).

## Identifying users

> **Identifying users is required.** Backend events need a `distinct_id` to associate events with the correct user.
>
> In Python, you can do this through a context. All event captures in the same context will be tagged automatically with the correct `distinct_id`. Typically, you would set a fresh context and identify at the top of each route.
>
> Python
>
> PostHog AI
>
> ```python
> from posthog import new_context, identify_context, capture
> @app.get("/foo")
> def foo(current_user: User = Depends(get_current_user)):
>     with new_context(): # Set context at the top of a route
>         identify_context(current_user.id)
>         capture("foo_viewed")
>     return {"status": "ok"}
> ```
>
> When possible, write a small piece of **middleware** that resolves your authenticated user, wrap a context around the request, and identifies it. Every `capture()` downstream is then attributed *automatically*. The SDK's Django middleware does this automatically and you can replicate it when using the plain Python SDK.

## Request contexts

Use [contexts](/docs/libraries/python.md#contexts) to share identity, session IDs, and tags across multiple captures during a request.

If you're using [PostHog JavaScript Web](/docs/libraries/js.md) on the frontend, configure [`tracing_headers`](/docs/libraries/js/config.md#tracing-headers) for your Flask backend hostname so browser requests include the session and distinct ID headers.

Then read the incoming headers in your Flask request handler. Tracing headers are client-controlled analytics context, not authentication or authorization, so prefer your authenticated user ID when one is available:

Python

PostHog AI

```python
from flask import request, session
from posthog import identify_context, set_context_session, tag
@app.route('/api/dashboard', methods=['POST'])
def api_dashboard():
    with posthog.new_context(fresh=True):
        distinct_id = session.get('user_id') or request.headers.get('X-POSTHOG-DISTINCT-ID')
        if distinct_id:
            identify_context(str(distinct_id))
        session_id = request.headers.get('X-POSTHOG-SESSION-ID')
        if session_id:
            set_context_session(session_id)
        tag('$current_url', request.url)
        tag('$request_method', request.method)
        tag('$request_path', request.path)
        posthog.capture('dashboard_api_called')
    return '', 204
```

Events captured without a context or explicit `distinct_id` are sent as [anonymous events](/docs/data/anonymous-vs-identified-events.md) with an auto-generated `distinct_id`. See the [Python SDK docs](/docs/libraries/python.md#person-profiles-and-properties) for more details.

## Error tracking

Flask has built-in error handlers. This means PostHog’s default exception autocapture won’t work and we need to manually capture errors instead using `capture_exception()`:

Python

PostHog AI

```python
from flask import Flask, jsonify
from posthog import Posthog
app = Flask(__name__)
posthog = Posthog('<ph_project_token>', host='https://us.i.posthog.com')
@app.errorhandler(Exception)
def handle_exception(e):
    # Capture methods, including capture_exception, return the UUID of the captured event,
    # which you can use to find specific errors users encountered
    event_id = posthog.capture_exception(e)
    # You can show the event ID to your user, and ask them to include it in bug reports
    response = jsonify({'message': str(e), 'error_id': event_id})
    response.status_code = 500
    return response
```

## Next steps

For any technical questions for how to integrate specific PostHog features into Flask (such as analytics, feature flags, A/B testing, etc.), have a look at our [Python SDK docs](/docs/libraries/python.md).

Alternatively, the following tutorials can help you get started:

-   [How to set up analytics in Python and Flask](/tutorials/python-analytics.md)
-   [How to set up feature flags in Python and Flask](/tutorials/python-feature-flags.md)
-   [How to set up A/B tests in Python and Flask](/tutorials/python-ab-testing.md)

## Supported versions

These docs cover version `7.x` of the PostHog Python SDK, which requires Python 3.10 or higher. Python 3.9 is no longer supported on `7.x.x` and higher — pin to the 6.x line with `pip install 'posthog<7'`, where `6.9.3` is the final release.

Everything on this page works the same way on `6.9.3`. Event capture, the context API (`new_context`, `identify_context`, `set_context_session`), and `PosthogContextMiddleware` are identical on `6.9.3` and `7.0.0` — `7.0.0` only dropped Python 3.9 and bumped the optional LLM provider SDKs. That includes the middleware identifying the request context from the `X-POSTHOG-DISTINCT-ID` header and falling back to the authenticated user, which behaves the same across both lines.

Later `7.x` releases add what the 6.x line does not receive, such as the Celery integration, tracing header sanitization, and `set_context_device_id`. They also changed the middleware's own captured properties: `7.x` sends the request IP as `$ip`, where `6.9.3` sends it as `$ip_address`, and `7.x` additionally captures `$request_path`, `$raw_user_agent`, and the authenticated user's `email`.

### Still have questions?

Ask PostHog AI

### Was this page useful?

HelpfulCould be better