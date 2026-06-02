# Django - Docs

PostHog makes it easy to get data about traffic and usage of your Django app. Integrating PostHog enables analytics, custom events capture, feature flags, error tracking, and more.

This guide walks you through integrating PostHog into your Django app using the [Python SDK](/docs/libraries/python.md).

## Beta: integration via LLM

Install PostHog for Django in seconds with our wizard by running this prompt with [LLM coding agents](/blog/envoy-wizard-llm-agent.md) like Cursor and Bolt, or by running it in your terminal.

`npx @posthog/wizard@latest`

[Learn more](/wizard.md)

Or, to integrate manually, continue with the rest of this guide.

## Installation

To start, run `pip install posthog` to install PostHog’s Python SDK.

> **Note:** Version `7.x` of the PostHog Python SDK requires Python 3.10 or higher.

Then, configure PostHog in your app config so it's initialized when Django starts:

your\_app/apps.py

PostHog AI

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

PostHog AI

```python
INSTALLED_APPS = [
    # ... other apps
    'your_app_name.apps.YourAppConfig',
]
```

You can find your project token and instance address in [your project settings](https://app.posthog.com/project/settings).

To capture events from any file, import `posthog` and call the method you need. For example:

Python

PostHog AI

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

Events captured without a context or explicit `distinct_id` are sent as [anonymous events](/docs/data/anonymous-vs-identified-events.md) with an auto-generated `distinct_id`. See the [Python SDK docs](/docs/libraries/python.md#person-profiles-and-properties) for more details.

## Identifying users

> **Identifying users is required.** Backend events need a `distinct_id` that matches the ID your frontend uses when calling `posthog.identify()`. Without this, backend events are orphaned — they can't be linked to frontend event captures, [session replays](/docs/session-replay.md), [LLM traces](/docs/ai-engineering.md), or [error tracking](/docs/error-tracking.md).
>
> See our guide on [identifying users](/docs/getting-started/identify-users.md) for how to set this up.

## Django contexts middleware

The Python SDK provides a Django middleware that automatically wraps all requests with a [context](/docs/libraries/python.md#contexts). This middleware extracts session and user information from each request and tags all events captured during that request with relevant metadata.

### Basic setup

Add the middleware to your Django settings. If your app uses Django authentication, place it after `django.contrib.auth.middleware.AuthenticationMiddleware` so the middleware can use the authenticated Django user as a distinct ID fallback and capture the user's email.

Python

PostHog AI

```python
MIDDLEWARE = [
    # ... other middleware
    'posthog.integrations.django.PosthogContextMiddleware',
    # ... other middleware
]
```

The middleware uses the globally configured `posthog` client by default, so you don't need to create or pass it a separate client instance.

The middleware automatically extracts and uses:

-   **Session ID** from the `X-POSTHOG-SESSION-ID` header, if present
-   **Distinct ID** from the `X-POSTHOG-DISTINCT-ID` header, if present, falling back to the authenticated Django user's `pk` (Django's primary-key alias, which works with custom user models)
-   **User email** from the authenticated Django user's `email` as `email`
-   **Current URL** as `$current_url`
-   **Request method** as `$request_method`
-   **Request path** as `$request_path`
-   **Forwarded IP address** from `X-Forwarded-For` as `$ip`
-   **User agent** from `User-Agent` as `$user_agent`

The session and distinct ID headers are sanitized before use. Empty values are ignored, control characters are removed, values are trimmed, and values are capped at 1000 characters.

All events captured during the request (including exceptions) include these properties and are associated with the extracted session and distinct ID.

If you are using PostHog on your frontend, the JavaScript Web SDK will add the session and distinct ID headers automatically if you enable tracing headers.

JavaScript

PostHog AI

```javascript
posthog.init('<ph_project_token>', {
    __add_tracing_headers: ['your-backend-domain.com']
})
```

### Exception capture

By default, the middleware captures exceptions and sends them to PostHog's error tracking using the globally configured `posthog` client. This includes Django view exceptions that Django converts into error responses.

Disable this by setting:

Python

PostHog AI

```python
# settings.py
POSTHOG_MW_CAPTURE_EXCEPTIONS = False
```

### Adding custom tags

Use `POSTHOG_MW_EXTRA_TAGS` to add custom properties to all requests:

Python

PostHog AI

```python
# settings.py
def add_user_tags(request):
    # type: (HttpRequest) -> Dict[str, Any]
    tags = {}
    if hasattr(request, 'user') and request.user.is_authenticated:
        # Use pk instead of id so this works with custom User primary keys.
        tags['user_id'] = str(request.user.pk)
        tags['email'] = request.user.email
    return tags
POSTHOG_MW_EXTRA_TAGS = add_user_tags
```

#### Filtering requests

Skip tracking for certain requests using `POSTHOG_MW_REQUEST_FILTER`:

Python

PostHog AI

```python
# settings.py
def should_track_request(request):
    # type: (HttpRequest) -> bool
    # Don't track health checks or admin requests
    if request.path.startswith('/health') or request.path.startswith('/admin'):
        return False
    return True
POSTHOG_MW_REQUEST_FILTER = should_track_request
```

### Modifying default tags

Use `POSTHOG_MW_TAG_MAP` to modify or remove default tags:

Python

PostHog AI

```python
# settings.py
def customize_tags(tags):
    # type: (Dict[str, Any]) -> Dict[str, Any]
    # Remove URL for privacy
    tags.pop('$current_url', None)
    # Add custom prefix to method
    if '$request_method' in tags:
        tags['http_method'] = tags.pop('$request_method')
    return tags
POSTHOG_MW_TAG_MAP = customize_tags
```

### Complete configuration example

Python

PostHog AI

```python
# settings.py
def add_request_context(request):
    # type: (HttpRequest) -> Dict[str, Any]
    tags = {}
    if hasattr(request, 'user') and request.user.is_authenticated:
        tags['user_type'] = 'authenticated'
        # Use pk instead of id so this works with custom User primary keys.
        tags['user_id'] = str(request.user.pk)
    else:
        tags['user_type'] = 'anonymous'
    # Add request info
    tags['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
    return tags
def filter_tracking(request):
    # type: (HttpRequest) -> bool
    # Skip internal endpoints
    return not request.path.startswith(('/health', '/metrics', '/admin'))
def clean_tags(tags):
    # type: (Dict[str, Any]) -> Dict[str, Any]
    # Remove sensitive data
    tags.pop('user_agent', None)
    return tags
POSTHOG_MW_EXTRA_TAGS = add_request_context
POSTHOG_MW_REQUEST_FILTER = filter_tracking
POSTHOG_MW_TAG_MAP = clean_tags
POSTHOG_MW_CAPTURE_EXCEPTIONS = True
```

All events captured within the request context automatically include the configured tags and are associated with the session and user identified from the request headers or Django authentication.

The middleware supports both sync (WSGI) and async (ASGI) Django applications. In async mode, it uses Django's `request.auser()` API when available to avoid synchronous user access.

## Next steps

For any technical questions for how to integrate specific PostHog features into Django (such as analytics, feature flags, A/B testing, etc.), have a look at our [Python SDK docs](/docs/libraries/python.md).

Alternatively, the following tutorials can help you get started:

-   [Setting up Django analytics, feature flags, and more](/tutorials/django-analytics.md)
-   [How to set up A/B tests in Django](/tutorials/django-ab-tests.md)

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better