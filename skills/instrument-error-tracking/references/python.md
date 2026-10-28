> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Python Error Tracking installation

Canonical URL: https://posthog.com/docs/error-tracking/installation/python

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.i.posthog.com` instead of `https://us.i.posthog.com` (ingestion host), and use `https://eu.posthog.com` instead of `https://app.posthog.com` (app host for links).

## On this page

- [Install with the wizard](#install-with-the-wizard)
- [Install the package](#install-the-package)
- [Initialize PostHog](#initialize-posthog)
- [Send events](#send-events)
- [Verify PostHog is initialized](#verify-posthog-is-initialized)
- [Setting up exception autocapture](#setting-up-exception-autocapture)
- [Manually capturing exceptions](#manually-capturing-exceptions)
- [Framework-specific exception capture](#framework-specific-exception-capture)
- [Verify error tracking](#verify-error-tracking)
- [Link releases](#link-releases)
- [Web framework integrations](#web-framework-integrations)

## Install with the wizard

Run this command in your project directory to add PostHog to your Python project. The wizard detects your framework, installs the SDK, and sets up your first events.

`npx @posthog/wizard`

Or set it up manually by following the rest of this guide.

1.  1

    ## Install the package

    Required

    Install the PostHog Python library using pip:

    Terminal

    ```bash
    pip install posthog
    ```

2.  2

    ## Initialize PostHog

    Required

    Initialize the PostHog client with your project token and host from your project settings:

    Python

    ```python
    from posthog import Posthog
    
    posthog = Posthog(
        project_api_key='<ph_project_token>',
        host='https://us.i.posthog.com'
    )
    ```

    **Django integration**

    If you're using Django, check out our [Django integration](https://posthog.com/docs/libraries/django.md) for automatic request tracking.

3.  3

    ## Send events

    Recommended

    Once installed, PostHog will automatically start capturing events. You can also manually send events to test your integration:

    Capture custom events by calling the `capture` method with an event name and properties:

    Python

    ```python
    import posthog
    posthog.capture('user_signed_up', distinct_id='user_123', properties={'example_property': 'example_value'})
    ```

4.  ## Verify PostHog is initialized

    Recommended

    Before proceeding, enable debug and call `posthog.capture('test_event')` to make sure you can capture events.

5.  4

    ## Setting up exception autocapture

    Recommended

    Exception autocapture can be enabled during initialization of the PostHog client to automatically capture any unhandled exceptions thrown by your Python application. It works by setting Python's built-in exception hooks, such as `sys.excepthook` and `threading.excepthook`.

    Python

    ```python
    from posthog import Posthog
    posthog = Posthog("<ph_project_token>", enable_exception_autocapture=True, ...)
    ```

    We recommend setting up and using [contexts](https://posthog.com/docs/libraries/python.md#contexts) so that exceptions automatically include distinct IDs, session IDs, and other properties you can set up with tags.

    You can also enable [code variables capture](https://posthog.com/docs/error-tracking/code-variables/python.md) to automatically capture the state of local variables when exceptions occur, giving you a debugger-like view of your application.

6.  5

    ## Manually capturing exceptions

    Optional

    For exceptions handled by your application that you would still like sent to PostHog, you can manually call the capture method:

    Python

    ```python
    posthog.capture_exception(e, distinct_id="user_distinct_id", properties=additional_properties)
    ```

    You can find a full example of all of this in our [Python (and Flask) error tracking tutorial](https://posthog.com/tutorials/python-error-tracking.md).

7.  6

    ## Framework-specific exception capture

    Recommended

    Web frameworks catch exceptions raised in your routes and turn them into error responses, so these exceptions never reach the hooks that exception autocapture uses. The Python SDK includes integrations for Django, Flask, and ASGI frameworks such as FastAPI. They capture these exceptions and add request properties to every event captured during a request. The Flask, ASGI, and Django REST Framework integrations require version `7.69.0` or later of the Python SDK.

    ## Django

    Add the Django middleware to your settings. It wraps each request in a [context](https://posthog.com/docs/libraries/python.md#contexts) and captures exceptions raised by your views.

    The middleware sends exceptions through the global `posthog` client. When you create your own client with `Posthog(...)`, set it as `POSTHOG_MW_CLIENT`. Otherwise the middleware sends exceptions to the unconfigured global client, and they don't reach PostHog:

    settings.py

    ```python
    from posthog import Posthog
    
    POSTHOG_MW_CLIENT = Posthog(
        '<ph_project_token>',
        host='https://us.i.posthog.com',
        enable_exception_autocapture=True,
    )
    
    MIDDLEWARE = [
        # ... other middleware
        'posthog.integrations.django.PosthogContextMiddleware',
    ]
    ```

    If you configure the global client instead, with `posthog.api_key` and `posthog.host`, leave `POSTHOG_MW_CLIENT` unset.

    Django REST Framework converts exceptions into error responses before the middleware sees them. If you use it, also add the DRF exception handler:

    settings.py

    ```python
    REST_FRAMEWORK = {
        # ... other DRF settings
        'EXCEPTION_HANDLER': 'posthog.integrations.drf.exception_handler',
    }
    ```

    Set `POSTHOG_MW_CAPTURE_EXCEPTIONS = False` to keep the request context without exception capture. See the [Django integration docs](https://posthog.com/docs/libraries/django.md#exception-capture) for all settings.

    ## Flask

    Register the Flask integration with your app and your client. It captures unhandled exceptions raised by your routes:

    Python

    ```python
    from flask import Flask
    from posthog import Posthog
    from posthog.integrations.flask import PosthogFlaskIntegration
    
    app = Flask(__name__)
    posthog = Posthog(
        '<ph_project_token>',
        host='https://us.i.posthog.com',
        enable_exception_autocapture=True,
    )
    
    PosthogFlaskIntegration(app, client=posthog)
    ```

    The integration doesn't capture expected HTTP exceptions, such as `404 Not Found`, or exceptions that your own error handlers consume. To report an exception that you handle, call `posthog.capture_exception(e)` in the handler. See the [Flask integration docs](https://posthog.com/docs/libraries/flask.md#error-tracking).

    ## FastAPI

    Add the ASGI middleware to your app. It captures exceptions that escape your routes. It works the same way for Starlette, Litestar, and other ASGI frameworks:

    Python

    ```python
    from fastapi import FastAPI
    from posthog import Posthog
    from posthog.integrations.asgi import PosthogASGIMiddleware
    
    posthog = Posthog(
        '<ph_project_token>',
        host='https://us.i.posthog.com',
        enable_exception_autocapture=True,
    )
    
    app = FastAPI()
    app.add_middleware(PosthogASGIMiddleware, client=posthog)
    ```

    The middleware still captures an exception that an `@app.exception_handler(Exception)` catch-all handles. A handler for a specific exception class, such as `@app.exception_handler(ValueError)`, turns that exception into a response before the middleware sees it. To report those exceptions, call `posthog.capture_exception(exc)` in the handler. See the [ASGI middleware docs](https://posthog.com/docs/libraries/python.md#asgi-request-middleware).

8.  ## Verify error tracking

    Recommended

    *Confirm events are being sent to PostHog*

    Before proceeding, let's make sure exception events are being captured and sent to PostHog. You should see events appear in the activity feed.

    ![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_ouxl_f788dd8cd2.png)

    [Check for exceptions in PostHog](https://app.posthog.com/activity/explore)

9.  7

    ## Link releases

    Optional

    Great, you're capturing exceptions! To see which release each exception comes from, give your app the release ID when you deploy.

    Let's continue to the next section.

    [Link releases](https://posthog.com/docs/error-tracking/link-releases/python.md)

## Web framework integrations

The Python SDK includes request context and error tracking integrations for common web frameworks:

-   [Django and Django REST Framework](https://posthog.com/docs/libraries/django.md#capture-django-rest-framework-exceptions)
-   [Flask](https://posthog.com/docs/libraries/flask.md#request-contexts)
-   [ASGI frameworks such as FastAPI, Starlette, and Litestar](https://posthog.com/docs/libraries/python.md#asgi-request-middleware)
