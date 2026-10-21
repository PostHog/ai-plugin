> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Django

Canonical URL: https://posthog.com/docs/libraries/django

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.i.posthog.com` instead of `https://us.i.posthog.com` (ingestion host), and use `https://eu.posthog.com` instead of `https://app.posthog.com` (app host for links).

## On this page

- [Beta: integration via LLM](#beta-integration-via-llm)
- [Installation](#installation)
- [Identifying users](#identifying-users)
- [Django contexts middleware](#django-contexts-middleware)
- [Next steps](#next-steps)
- [Supported versions](#supported-versions)

PostHog makes it easy to get data about traffic and usage of your Django app. Integrating PostHog enables analytics, custom events capture, feature flags, error tracking, and more.

This guide walks you through integrating PostHog into your Django app using the [Python SDK](https://posthog.com/docs/libraries/python.md).

## Beta: integration via LLM

Install PostHog for Django in seconds with our wizard by running this prompt with [LLM coding agents](https://posthog.com/blog/envoy-wizard-llm-agent.md) like Cursor and Bolt, or by running it in your terminal.

`npx @posthog/wizard`

Or, to integrate manually, continue with the rest of this guide.

> These docs cover version `7.x` of the Python SDK, which requires Python 3.10 or higher. On Python 3.9? See [supported versions](#supported-versions).

## Installation

To start, run `pip install posthog` to install PostHog’s Python SDK.

Then, configure PostHog in your app config so it's initialized when Django starts:

your\_app/apps.py

```python
from django.apps import AppConfig
import posthog

class YourAppConfig(AppConfig):
    name = 'your_app_name'

    def ready(self):
        posthog.api_key = '<ph_project_token>'
        posthog.host = 'https://us.i.posthog.com'
```

Next, if you haven't done so already, add your `AppConfig` to `INSTALLED_APPS` in `settings.py`:

settings.py

```python
INSTALLED_APPS = [
    # ... other apps
    'your_app_name.apps.YourAppConfig',
]
```

You can find your project token and instance address in [your project settings](https://app.posthog.com/project/settings).

To capture events from any file, import `posthog` and call the method you need. For example:

```python
import posthog
from posthog import identify_context

def some_request(request):
    with posthog.new_context():
        # Django includes request.user for anonymous visitors too. Only identify
        # the context when the visitor is logged in.
        if request.user.is_authenticated:
            identify_context(str(request.user.pk))

        posthog.capture('event_name')
```

Events captured without a context or explicit `distinct_id` are sent as [anonymous events](https://posthog.com/docs/data/anonymous-vs-identified-events.md) with an auto-generated `distinct_id`. See the [Python SDK docs](https://posthog.com/docs/libraries/python.md#person-profiles-and-properties) for more details.

## Identifying users

> **Identifying users is required.** Backend events need a `distinct_id` to associate events with the correct user.
>
> In Python, you can do this through a context. All event captures in the same context will be tagged automatically with the correct `distinct_id`. Typically, you would set a fresh context and identify at the top of each route.
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

## Django contexts middleware

The Python SDK provides a Django middleware that automatically wraps all requests with a [context](https://posthog.com/docs/libraries/python.md#contexts). This middleware extracts session and user information from each request and adds relevant properties to events captured during that request.

### Basic setup

Add the middleware to your Django settings. If your app uses Django authentication, place it after `django.contrib.auth.middleware.AuthenticationMiddleware` so the middleware can use the authenticated Django user as a distinct ID fallback and capture the user's email.

```python
MIDDLEWARE = [
    # ... other middleware
    "posthog.integrations.django.PosthogContextMiddleware",
    # ... other middleware
]
```

The middleware uses the globally configured `posthog` client by default, so you don't need to create or pass it a separate client instance.

The middleware automatically extracts and uses:

-   **Session ID** from the `X-POSTHOG-SESSION-ID` header when you enable `POSTHOG_MW_TRUST_TRACING_HEADERS`
-   **Distinct ID** from the authenticated Django user's `pk` (Django's primary-key alias, which works with custom user models), or from the `X-POSTHOG-DISTINCT-ID` header when you enable `POSTHOG_MW_TRUST_TRACING_HEADERS`
-   **User email** from the authenticated Django user's `email` as `email`
-   **Current URL** as `$current_url`
-   **Request method** as `$request_method`
-   **Request path** as `$request_path`
-   **Forwarded IP address** from `X-Forwarded-For` as `$ip`
-   **User agent** from `User-Agent` as `$user_agent`

The middleware ignores the session and distinct ID headers by default because clients can control them. To use them as analytics context, enable them in your Django settings:

```python
# settings.py
POSTHOG_MW_TRUST_TRACING_HEADERS = True
```

Don't use these headers for authentication or authorization. The middleware sanitizes trusted header values before use. It ignores empty values, removes control characters, trims values, and caps them at 1000 characters.

All events captured during the request (including exceptions) include these properties and are associated with the extracted session and distinct ID.

### Login and signup views

The middleware reads `request.user` once, before your view runs. On a login or signup request the visitor is still anonymous at that point, so the request's context has no distinct ID. Calling `login()` inside the view doesn't change that. Everything captured during that request stays anonymous, including the login event itself.

Identify the context from inside the request once you know who the user is. Django's auth signals are the natural place:

```python
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from posthog import identify_context

@receiver(user_logged_in)
def identify_posthog_user(sender, request, user, **kwargs):
    identify_context(str(user.pk))
```

Every capture later in that request is then attributed to the user who just logged in. Requests made after login don't need this. The middleware sees the authenticated user from the start.

If you're using [PostHog JavaScript Web](https://posthog.com/docs/libraries/js.md) on the frontend, configure [`tracing_headers`](https://posthog.com/docs/libraries/js/config.md#tracing-headers) for your Django backend hostname so browser requests include the session and distinct ID headers. You must also set `POSTHOG_MW_TRUST_TRACING_HEADERS = True` in Django to accept them.

### Exception capture

By default, the middleware captures exceptions and sends them to PostHog's error tracking using the globally configured `posthog` client. This includes Django view exceptions that Django converts into error responses.

Disable this by setting:

```python
# settings.py
POSTHOG_MW_CAPTURE_EXCEPTIONS = False
```

Set `POSTHOG_MW_CAPTURE_EXCEPTIONS = None` to inherit the global client's `enable_exception_autocapture` setting. When you omit `POSTHOG_MW_CAPTURE_EXCEPTIONS`, the middleware preserves the existing Django default and captures exceptions.

### Capture Django REST Framework exceptions

This integration requires version `7.69.0` or later of the Python SDK.

Django REST Framework (DRF) converts many exceptions into responses before Django middleware can observe them. Add PostHog's DRF exception handler to capture these handled errors:

```python
# settings.py
REST_FRAMEWORK = {
    # ... other DRF settings
    "EXCEPTION_HANDLER": "posthog.integrations.drf.exception_handler",
}
```

Keep `PosthogContextMiddleware` enabled. The middleware adds request properties and identity to the active context, while the DRF handler captures handled API exceptions. The handler captures responses with a `5xx` status by default and ignores expected `4xx` responses. If DRF doesn't handle an exception, Django re-raises it and the middleware captures it instead.

If you already use a custom DRF exception handler, wrap it in an application module:

```python
# your_app/exception_handlers.py
from posthog.integrations.drf import create_exception_handler
from your_app.api import existing_exception_handler

exception_handler = create_exception_handler(existing_exception_handler)
```

Then point DRF to the wrapper:

```python
# settings.py
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "your_app.exception_handlers.exception_handler",
}
```

To capture selected `4xx` responses, create a handler with `capture_4xx=True` and an exception filter:

```python
# your_app/exception_handlers.py
from posthog.integrations.drf import create_exception_handler


def capture_auth_errors(exception, response, context):
    return response.status_code >= 500 or response.status_code in {401, 403}


exception_handler = create_exception_handler(
    capture_4xx=True,
    exception_filter=capture_auth_errors,
)
```

The DRF handler follows `POSTHOG_MW_CAPTURE_EXCEPTIONS` and `POSTHOG_MW_REQUEST_FILTER`. You can also pass `capture_exceptions=True` or `capture_exceptions=False` to `create_exception_handler()` to override the middleware setting.

### Add custom properties

Use `POSTHOG_MW_EXTRA_PROPERTIES` to add custom properties to all requests:

```python
# settings.py
def add_user_properties(request):
    # type: (HttpRequest) -> Dict[str, Any]
    properties = {}
    if hasattr(request, "user") and request.user.is_authenticated:
        # Use pk instead of id so this works with custom User primary keys.
        properties["user_id"] = str(request.user.pk)
        properties["email"] = request.user.email
    return properties

POSTHOG_MW_EXTRA_PROPERTIES = add_user_properties
```

### Filter requests

Skip tracking for certain requests using `POSTHOG_MW_REQUEST_FILTER`:

```python
# settings.py
def should_track_request(request):
    # type: (HttpRequest) -> bool
    # Don't track health checks or admin requests
    if request.path.startswith("/health") or request.path.startswith("/admin"):
        return False
    return True

POSTHOG_MW_REQUEST_FILTER = should_track_request
```

### Modify default properties

Use `POSTHOG_MW_PROPERTIES_MAP` to modify or remove default properties:

```python
# settings.py
def customize_properties(properties):
    # type: (Dict[str, Any]) -> Dict[str, Any]
    # Remove URL for privacy
    properties.pop("$current_url", None)
    # Add custom prefix to method
    if "$request_method" in properties:
        properties["http_method"] = properties.pop("$request_method")
    return properties

POSTHOG_MW_PROPERTIES_MAP = customize_properties
```

### Complete configuration example

```python
# settings.py
def add_request_context(request):
    # type: (HttpRequest) -> Dict[str, Any]
    properties = {}
    if hasattr(request, "user") and request.user.is_authenticated:
        properties["user_type"] = "authenticated"
        # Use pk instead of id so this works with custom User primary keys.
        properties["user_id"] = str(request.user.pk)
    else:
        properties["user_type"] = "anonymous"

    # Add request info
    properties["user_agent"] = request.META.get("HTTP_USER_AGENT", "")
    return properties

def filter_tracking(request):
    # type: (HttpRequest) -> bool
    # Skip internal endpoints
    return not request.path.startswith(("/health", "/metrics", "/admin"))

def clean_properties(properties):
    # type: (Dict[str, Any]) -> Dict[str, Any]
    # Remove sensitive data
    properties.pop("user_agent", None)
    return properties

POSTHOG_MW_EXTRA_PROPERTIES = add_request_context
POSTHOG_MW_REQUEST_FILTER = filter_tracking
POSTHOG_MW_PROPERTIES_MAP = clean_properties
POSTHOG_MW_CAPTURE_EXCEPTIONS = True
```

All events captured within the request context automatically include the configured properties. They use the authenticated Django user as the distinct ID, or the session and distinct ID from request headers when you enable `POSTHOG_MW_TRUST_TRACING_HEADERS`.

The middleware supports both sync (WSGI) and async (ASGI) Django applications. In async mode, it uses Django's `request.auser()` API when available to avoid synchronous user access.

## Next steps

For any technical questions for how to integrate specific PostHog features into Django (such as analytics, feature flags, A/B testing, etc.), have a look at our [Python SDK docs](https://posthog.com/docs/libraries/python.md).

Alternatively, the following tutorials can help you get started:

-   [Setting up Django analytics, feature flags, and more](https://posthog.com/tutorials/django-analytics.md)
-   [How to set up A/B tests in Django](https://posthog.com/tutorials/django-ab-tests.md)

## Supported versions

These docs cover version `7.x` of the PostHog Python SDK, which requires Python 3.10 or higher. Python 3.9 is no longer supported on `7.x.x` and higher — pin to the 6.x line with `pip install 'posthog<7'`, where `6.9.3` is the final release.

Everything on this page works the same way on `6.9.3`. Event capture, the context API (`new_context`, `identify_context`, `set_context_session`), and `PosthogContextMiddleware` are identical on `6.9.3` and `7.0.0` — `7.0.0` only dropped Python 3.9 and bumped the optional LLM provider SDKs. That includes the middleware identifying the request context from the `X-POSTHOG-DISTINCT-ID` header and falling back to the authenticated user, which behaves the same across both lines.

Later `7.x` releases add what the 6.x line does not receive, such as the Celery integration, tracing header sanitization, and `set_context_device_id`. They also changed the middleware's own captured properties: `7.x` sends the request IP as `$ip`, where `6.9.3` sends it as `$ip_address`, and `7.x` additionally captures `$request_path`, `$raw_user_agent`, and the authenticated user's `email`.
