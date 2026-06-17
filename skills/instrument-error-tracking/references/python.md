# Python error tracking installation - Docs

1.  1

    ## Install the package

    Required

    Install the PostHog Python library using pip:

    Terminal

    PostHog AI

    ```bash
    pip install posthog
    ```

2.  2

    ## Initialize PostHog

    Required

    Initialize the PostHog client with your project token and host from your project settings:

    Python

    PostHog AI

    ```python
    from posthog import Posthog
    posthog = Posthog(
        project_api_key='<ph_project_token>',
        host='https://us.i.posthog.com'
    )
    ```

    **Django integration**

    If you're using Django, check out our [Django integration](/docs/libraries/django.md) for automatic request tracking.

3.  3

    ## Send events

    Recommended

    Once installed, PostHog will automatically start capturing events. You can also manually send events to test your integration:

    Capture custom events by calling the `capture` method with an event name and properties:

    Python

    PostHog AI

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

    PostHog AI

    ```python
    from posthog import Posthog
    posthog = Posthog("<ph_project_token>", enable_exception_autocapture=True, ...)
    ```

    We recommend setting up and using [contexts](/docs/libraries/python.md#contexts) so that exceptions automatically include distinct IDs, session IDs, and other properties you can set up with tags.

    You can also enable [code variables capture](/docs/error-tracking/code-variables/python.md) to automatically capture the state of local variables when exceptions occur, giving you a debugger-like view of your application.

6.  5

    ## Manually capturing exceptions

    Optional

    For exceptions handled by your application that you would still like sent to PostHog, you can manually call the capture method:

    Python

    PostHog AI

    ```python
    posthog.capture_exception(e, distinct_id="user_distinct_id", properties=additional_properties)
    ```

    You can find a full example of all of this in our [Python (and Flask) error tracking tutorial](/tutorials/python-error-tracking.md).

7.  6

    ## Framework-specific exception capture

    Optional

    Python frameworks often have built-in error handlers. This means PostHog's default exception autocapture won't work and we need to manually capture errors instead. The exact process depends on the framework:

    ## Django

    The Python SDK provides a Django middleware that automatically wraps all requests with a [context](/docs/libraries/python.md#contexts). Add the middleware to your Django settings:

    Python

    PostHog AI

    ```python
    MIDDLEWARE = [
        # ... other middleware
        'posthog.integrations.django.PosthogContextMiddleware',
        # ... other middleware
    ]
    ```

    By default, the middleware captures exceptions and sends them to PostHog. Disable with `POSTHOG_MW_CAPTURE_EXCEPTIONS = False`. Use `POSTHOG_MW_EXTRA_TAGS`, `POSTHOG_MW_REQUEST_FILTER`, and `POSTHOG_MW_TAG_MAP` to customize. See the [Django integration docs](/docs/libraries/django.md) for full configuration.

    ## Flask

    Python

    PostHog AI

    ```python
    from flask import Flask, jsonify
    from posthog import Posthog
    posthog = Posthog('<ph_project_token>', host='https://us.i.posthog.com')
    @app.errorhandler(Exception)
    def handle_exception(e):
        event_id = posthog.capture_exception(e)
        response = jsonify({'message': str(e), 'error_id': event_id})
        response.status_code = 500
        return response
    ```

    ## FastAPI

    Python

    PostHog AI

    ```python
    from fastapi.responses import JSONResponse
    from posthog import Posthog
    posthog = Posthog('<ph_project_token>', host='https://us.i.posthog.com')
    @app.exception_handler(Exception)
    async def http_exception_handler(request, exc):
        posthog.capture_exception(exc)
        return JSONResponse(status_code=500, content={'message': str(exc)})
    ```

8.  ## Verify error tracking

    Recommended

    *Confirm events are being sent to PostHog*

    Before proceeding, let's make sure exception events are being captured and sent to PostHog. You should see events appear in the activity feed.

    ![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_ouxl_f788dd8cd2.png)![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_owae_7c3490822c.png)

    [Check for exceptions in PostHog](https://app.posthog.com/activity/explore)

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better