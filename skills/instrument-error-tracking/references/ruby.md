# Ruby error tracking installation - Docs

1.  1

    ## Install the gem

    Required

    Add the PostHog Ruby gem to your Gemfile:

    Gemfile

    PostHog AI

    ```ruby
    gem "posthog-ruby"
    ```

2.  2

    ## Configure PostHog

    Required

    Initialize the PostHog client with your project token and host:

    Ruby

    PostHog AI

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

    PostHog AI

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

    PostHog AI

    ```ruby
    begin
      # Code that might raise an exception
      raise StandardError, "Something went wrong"
    rescue => e
      posthog.capture_exception(
        e,
        distinct_id: 'user_distinct_id',
        properties: {
          custom_property: 'custom_value'
        }
      )
    end
    ```

    The `capture_exception` method accepts the following parameters:

    | Param | Type | Description |
    | --- | --- | --- |
    | exception | Exception | The exception object to capture (required) |
    | distinct_id | String | The distinct ID of the user (optional) |
    | properties | Hash | Additional properties to attach to the exception event (optional) |

5.  ## Verify error tracking

    Recommended

    *Confirm events are being sent to PostHog*

    Before proceeding, let's make sure exception events are being captured and sent to PostHog. You should see events appear in the activity feed.

    ![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_ouxl_f788dd8cd2.png)![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_owae_7c3490822c.png)

    [Check for exceptions in PostHog](https://app.posthog.com/activity/explore)

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better