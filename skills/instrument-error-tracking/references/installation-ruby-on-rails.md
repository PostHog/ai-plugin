> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Ruby on Rails Error Tracking installation

Canonical URL: https://posthog.com/docs/error-tracking/installation/ruby-on-rails

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.i.posthog.com` instead of `https://us.i.posthog.com` (ingestion host), and use `https://eu.posthog.com` instead of `https://app.posthog.com` (app host for links).

## On this page

- [Install with the wizard](#install-with-the-wizard)
- [Install the gems](#install-the-gems)
- [Generate the initializer](#generate-the-initializer)
- [Configure PostHog](#configure-posthog)
- [Send events](#send-events)
- [Configure error tracking](#configure-error-tracking)
- [Automatic exception capture](#automatic-exception-capture)
- [Background jobs](#background-jobs)
- [Manually capture exceptions](#manually-capture-exceptions)
- [Verify error tracking](#verify-error-tracking)
- [Link releases](#link-releases)
- [Controller exception helper](#controller-exception-helper)
- [Streaming exceptions](#streaming-exceptions)
- [Action Cable exceptions](#action-cable-exceptions)
- [Rails runner exceptions](#rails-runner-exceptions)
- [Active Job context and retries](#active-job-context-and-retries)
- [Rails 7.0+ error reporter](#rails-70-error-reporter)
- [User context](#user-context)
- [Excluded exceptions](#excluded-exceptions)
- [Trace and release correlation](#trace-and-release-correlation)

## Install with the wizard

Run this command in your project directory to add PostHog to your Rails project. The wizard detects your framework, installs the SDK, and sets up your first events.

`npx @posthog/wizard`

Or set it up manually by following the rest of this guide.

1.  1

    ## Install the gems

    Required

    Add the `posthog-ruby` and `posthog-rails` gems to your Gemfile:

    Gemfile

    ```ruby
    gem "posthog-ruby", "~> 3.0"
    gem "posthog-rails", "~> 3.0"
    ```

    Then run:

    Terminal

    ```bash
    bundle install
    ```

2.  2

    ## Generate the initializer

    Required

    Run the install generator to create the PostHog initializer:

    Terminal

    ```bash
    rails generate posthog:install
    ```

    This will create `config/initializers/posthog.rb` with sensible defaults and documentation.

3.  3

    ## Configure PostHog

    Required

    Update `config/initializers/posthog.rb` with your project token and host:

    config/initializers/posthog.rb

    ```ruby
    PostHog.init do |config|
      config.api_key = '<ph_project_token>'
      config.host = 'https://us.i.posthog.com'
    end
    ```

4.  4

    ## Send events

    Recommended

    Once installed, you can manually send events to test your integration:

    Ruby

    ```ruby
    PostHog.capture({
        distinct_id: 'user_123',
        event: 'button_clicked',
        properties: {
            button_name: 'signup'
        }
    })
    ```

5.  5

    ## Configure error tracking

    Required

    Update `config/initializers/posthog.rb` to enable automatic exception capture:

    config/initializers/posthog.rb

    ```ruby
    PostHog::Rails.configure do |config|
      config.auto_capture_exceptions = true
      config.report_rescued_exceptions = true
      config.auto_instrument_active_job = true
      config.capture_user_context = true
      config.current_user_method = :current_user
    end
    ```

6.  6

    ## Automatic exception capture

    Recommended

    With `auto_capture_exceptions` enabled, exceptions are automatically captured from your controllers:

    app/controllers/posts\_controller.rb

    ```ruby
    class PostsController < ApplicationController
      def show
        @post = Post.find(params[:id])
        # Any exception here is automatically captured
      end
    end
    ```

7.  7

    ## Background jobs

    Optional

    When `auto_instrument_active_job` is enabled, ActiveJob exceptions are automatically captured:

    app/jobs/email\_job.rb

    ```ruby
    class EmailJob < ApplicationJob
      def perform(user_id)
        user = User.find(user_id)
        UserMailer.welcome(user).deliver_now
        # Exceptions are automatically captured with job context
      end
    end
    ```

8.  8

    ## Manually capture exceptions

    Optional

    You can also manually capture exceptions that you handle in your application:

    Ruby

    ```ruby
    PostHog.capture_exception(
      exception,
      current_user.id,
      { custom_property: 'value' }
    )
    ```

9.  ## Verify error tracking

    Recommended

    *Confirm events are being sent to PostHog*

    Before proceeding, let's make sure exception events are being captured and sent to PostHog. You should see events appear in the activity feed.

    ![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_ouxl_f788dd8cd2.png)

    [Check for exceptions in PostHog](https://app.posthog.com/activity/explore)

10.  9

     ## Link releases

     Optional

     Great, you're capturing exceptions! To see which release each exception comes from, give your app the release ID when you deploy.

     Let's continue to the next section.

     [Link releases](https://posthog.com/docs/error-tracking/link-releases/ruby.md)

The sections below cover additional capture options and user context.

## Controller exception helper

From `posthog-rails` 3.24.0, use `capture_exception` in controllers to report handled errors. It includes the current user and filtered request context:

```ruby
class PaymentsController < ApplicationController
  def create
    PaymentService.charge(params[:order_id])
    head :created
  rescue PaymentService::Error => error
    capture_exception(error, nil, { payment_provider: "stripe" })
    head :bad_gateway
  end
end
```

Manual capture works without `auto_capture_exceptions` and ignores automatic exception exclusions. Explicit identity and properties override the request defaults. Check custom properties for sensitive data.

Outside controllers, use `PostHog.capture_exception`. See [Ruby exception capture](https://posthog.com/docs/libraries/ruby.md#exception-capture) for arguments, feature flag snapshots, and duplicate prevention.

## Streaming exceptions

From version 3.21.0, `auto_capture_exceptions` also captures errors from `ActionController::Live` and ActionView streaming templates.

## Action Cable exceptions

From version 3.22.0, `auto_capture_exceptions` captures unhandled connection, channel lifecycle, and channel action errors. Reports include filtered channel parameters and action data. Review your application's and connection's `filter_parameters` for sensitive data.

Use `current_user_method` and `user_id_method` to identify connection users. The controller-only `current_user_resolver` does not apply.

Errors handled by `rescue_from` are not captured, even with `report_rescued_exceptions = true`.

## Rails runner exceptions

From version 3.24.0, `auto_capture_exceptions` reports terminating `rails runner` errors and nonzero exits as fatal exceptions. Successful exits and signals such as Ctrl-C or SIGTERM are not reported.

Capture runs before SDK shutdown without changing the exit status. Forced termination and `exit!` cannot be captured.

## Active Job context and retries

From version 3.20.0, queued jobs also retain the request's PostHog session and distinct IDs. Job events and logs use these IDs unless a job identity extractor overrides the distinct ID.

### Report retry failures

From version 3.24.0, also enable `report_active_job_retries` to capture failed attempts that Active Job retries:

config/initializers/posthog.rb

```ruby
PostHog::Rails.configure do |config|
  config.auto_instrument_active_job = true
  config.report_active_job_retries = true
end
```

This defaults to `false` and requires `auto_instrument_active_job`. Retry reports use the job's identity and filtered arguments. Exception exclusions still apply, and retry scheduling does not change.

### Associating jobs with users

By default, PostHog extracts a `distinct_id` from job arguments by looking for a `user_id` key in hash arguments:

```ruby
# PostHog will automatically use options[:user_id] as the distinct_id
ProcessOrderJob.perform_later(order.id, user_id: current_user.id)
```

For more control, use the `posthog_distinct_id` class method. The proc or block receives the same arguments as `perform`:

```ruby
class SendWelcomeEmailJob < ApplicationJob
  posthog_distinct_id ->(user, _options) { user.id }

  def perform(user, options = {})
    UserMailer.welcome(user).deliver_now
  end
end
```

## Rails 7.0+ error reporter

With `auto_capture_exceptions = true`, errors reported through `Rails.error` are sent to PostHog:

```ruby
Rails.error.report(exception, handled: true, context: { user_id: current_user.id })
```

PostHog automatically extracts the user's distinct ID from `user_id` or `distinct_id` in the context hash. Other context keys are included as properties on the exception event.

## User context

Controller exception reports use the authenticated user's ID before client-supplied tracing headers.

If your user method has a different name, configure it:

```ruby
PostHog::Rails.config.current_user_method = :logged_in_user
```

For request-local authentication, set `current_user_resolver` instead. It takes precedence over `current_user_method`:

```ruby
PostHog::Rails.configure do |config|
  config.current_user_resolver = -> { Current.user }
end
```

The resolver can accept the controller as an argument.

### User ID extraction

PostHog checks `posthog_distinct_id`, `distinct_id`, `id`, `pk`, and `uuid`, in that order. Hash-like users can provide `id`, `pk`, or `uuid` keys.

You can configure a specific method:

```ruby
PostHog::Rails.config.user_id_method = :email
```

## Excluded exceptions

Automatic capture excludes the following exceptions by default:

-   `AbstractController::ActionNotFound`
-   `ActionController::BadRequest`
-   `ActionController::InvalidAuthenticityToken`
-   `ActionController::InvalidCrossOriginRequest`
-   `ActionController::MethodNotAllowed`
-   `ActionController::NotImplemented`
-   `ActionController::ParameterMissing`
-   `ActionController::RoutingError`
-   `ActionController::UnknownFormat`
-   `ActionController::UnknownHttpMethod`
-   `ActionDispatch::Http::MimeNegotiation::InvalidType`
-   `ActionDispatch::Http::Parameters::ParseError`
-   `ActiveRecord::RecordNotFound`
-   `ActiveRecord::RecordNotUnique`

Add more with:

```ruby
PostHog::Rails.config.excluded_exceptions = ["MyException"]
```

## Trace and release correlation

See [Rails trace context](https://posthog.com/docs/libraries/ruby-on-rails.md#trace-context) to connect errors with application traces.

Set `POSTHOG_RELEASE_ID` before client initialization to [link errors to a release](https://posthog.com/docs/error-tracking/link-releases/ruby.md).
