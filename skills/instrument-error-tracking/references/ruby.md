> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Ruby Error Tracking installation

Canonical URL: https://posthog.com/docs/error-tracking/installation/ruby

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.i.posthog.com` instead of `https://us.i.posthog.com` (ingestion host), and use `https://eu.posthog.com` instead of `https://app.posthog.com` (app host for links).

## On this page

- [Install with the wizard](#install-with-the-wizard)
- [Install the gem](#install-the-gem)
- [Configure PostHog](#configure-posthog)
- [Send events](#send-events)
- [Manually capture exceptions](#manually-capture-exceptions)
- [Verify error tracking](#verify-error-tracking)
- [Link releases](#link-releases)

## Install with the wizard

Run this command in your project directory to add PostHog to your Ruby project. The wizard detects your framework, installs the SDK, and sets up your first events.

`npx @posthog/wizard`

Or set it up manually by following the rest of this guide.

1.  1

    ## Install the gem

    Required

    Add the PostHog Ruby gem to your Gemfile:

    Gemfile

    ```ruby
    gem "posthog-ruby"
    ```

2.  2

    ## Configure PostHog

    Required

    Initialize the PostHog client with your project token and host:

    Ruby

    ```ruby
    require 'posthog'
    
    posthog = PostHog::Client.new({
        api_key: "<ph_project_token>",
        host: "https://us.i.posthog.com",
        on_error: Proc.new { |status, msg| print msg }
    })
    ```

3.  3

    ## Send events

    Recommended

    Once installed, you can manually send events to test your integration:

    Ruby

    ```ruby
    posthog.capture({
        distinct_id: 'user_123',
        event: 'button_clicked',
        properties: {
            button_name: 'signup'
        }
    })
    ```

4.  4

    ## Manually capture exceptions

    Required

    > **Using Ruby on Rails?** The `posthog-rails` gem provides automatic exception capture for controllers and background jobs. Select "Ruby on Rails" from the SDK list for setup instructions.

    To capture exceptions in your Ruby application, use the `capture_exception` method:

    Ruby

    ```ruby
    begin
      # Code that might raise an exception
      raise StandardError, "Something went wrong"
    rescue => e
      posthog.capture_exception(
        e,
        'user_distinct_id',
        {
          custom_property: 'custom_value'
        }
      )
    end
    ```

    The `capture_exception` method accepts the following parameters:

    | Param | Type | Description |
    | --- | --- | --- |
    | `exception` | `Exception` | The exception object to capture (required) |
    | `distinct_id` | `String` | The distinct ID of the user (optional) |
    | `additional_properties` | `Hash` | Additional properties to attach to the exception event (optional) |

5.  ## Verify error tracking

    Recommended

    *Confirm events are being sent to PostHog*

    Before proceeding, let's make sure exception events are being captured and sent to PostHog. You should see events appear in the activity feed.

    ![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_ouxl_f788dd8cd2.png)

    [Check for exceptions in PostHog](https://app.posthog.com/activity/explore)

6.  5

    ## Link releases

    Optional

    Great, you're capturing exceptions! To see which release each exception comes from, give your app the release ID when you deploy.

    Let's continue to the next section.

    [Link releases](https://posthog.com/docs/error-tracking/link-releases/ruby.md)
