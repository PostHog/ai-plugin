# PostHog ruby-on-rails Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/ruby-on-rails

---

## README.md

# PostHog Ruby on Rails example

This is a [Ruby on Rails](https://rubyonrails.org) example demonstrating PostHog integration with product analytics, error tracking (auto-instrumentation), feature flags, user identification, and ActiveJob instrumentation via the `posthog-rails` gem.

## Features

- **Product analytics**: Track user events and behaviors with `PostHog.capture`
- **Error tracking (auto)**: Unhandled exceptions captured automatically by `posthog-rails`
- **Error tracking (manual)**: Handled errors captured with `PostHog.capture_exception`
- **Rails.error integration**: Rails 7+ error reporting captured automatically
- **ActiveJob instrumentation**: Background job failures captured automatically
- **User identification**: Associate events with authenticated users via `PostHog.identify`
- **Feature flags**: Control feature rollouts with `PostHog.evaluate_flags`
- **User context**: Exceptions automatically associated with `current_user`
- **Request context**: request metadata (and, from the browser, the PostHog session and distinct ID) attached to backend events
- **Frontend tracking**: posthog-js captures pageviews and session replay alongside backend events

## Getting started

### 1. Install dependencies

```bash
bundle install
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env and add your PostHog project token
```

If `POSTHOG_PROJECT_TOKEN` is missing the app still boots: PostHog stays disabled, every PostHog call is a no-op, and development logs a warning naming the variable.

Get your PostHog project token from your [PostHog project settings](https://app.posthog.com/project/settings).

### 3. Setup database

```bash
bin/rails db:create db:migrate db:seed
```

### 4. Run the development server

```bash
bin/rails server
```

Open [http://localhost:3000](http://localhost:3000) with your browser. Login with `admin@example.com` / `admin`.

## Project structure

```
ruby-on-rails/
├── config/
│   ├── routes.rb                        # URL routing
│   └── initializers/
│       └── posthog.rb                   # PostHog + posthog-rails configuration
├── app/
│   ├── controllers/
│   │   ├── application_controller.rb    # Base controller with current_user
│   │   ├── sessions_controller.rb       # Login/logout with PostHog identify
│   │   ├── registrations_controller.rb  # Signup with PostHog identify
│   │   ├── dashboard_controller.rb      # Feature flags + ActiveJob demo
│   │   ├── burritos_controller.rb       # Custom event tracking
│   │   ├── profiles_controller.rb       # Page view tracking
│   │   └── errors_controller.rb         # Error tracking demos
│   ├── jobs/
│   │   └── example_job.rb              # ActiveJob auto-instrumentation demo
│   ├── models/
│   │   └── user.rb                     # posthog_distinct_id + posthog_properties
│   └── views/
│       ├── layouts/application.html.erb # Base layout with posthog-js snippet
│       ├── sessions/new.html.erb        # Login page
│       ├── registrations/new.html.erb   # Signup page
│       ├── dashboard/show.html.erb      # Feature flags demo
│       ├── burritos/show.html.erb       # Event tracking demo
│       └── profiles/show.html.erb       # Error tracking demo
├── db/
│   ├── migrate/                         # Database migrations
│   └── seeds.rb                         # Default admin user
├── .env.example                         # Environment variable template
├── Gemfile                              # Ruby dependencies
└── README.md                            # This file
```

## Key integration points

### PostHog initialization (config/initializers/posthog.rb)

```ruby
PostHog::Rails.configure do |config|
  config.auto_capture_exceptions = true
  config.report_rescued_exceptions = true
  config.auto_instrument_active_job = true
  config.capture_user_context = true
  config.current_user_method = :current_user
  config.user_id_method = :posthog_distinct_id
end

project_token = ENV['POSTHOG_PROJECT_TOKEN'].to_s.strip

if project_token.empty?
  Rails.logger.warn('POSTHOG_PROJECT_TOKEN is not set; PostHog is disabled...') if Rails.env.development?
else
  PostHog.init do |config|
    config.api_key = project_token
    config.host = ENV.fetch('POSTHOG_HOST', 'https://us.i.posthog.com')
    config.test_mode = true if Rails.env.test?
  end
end
```

The Gemfile lists both gems: `posthog-ruby` (with `require: 'posthog'`) and `posthog-rails`. `rails generate posthog:install` creates an initializer like this one. `PostHog.init` creates the single shared client; do not create more `PostHog::Client` instances with the same key.

## What the integration sets up for you

Everything below comes from `posthog-rails` (the Railtie in its `railtie.rb`) and its documented behavior. The three `PostHog::Rails` exception and job options default to `false`, so the initializer turns them on.

### Automatic

- **`PostHog` facade**: `PostHog.init`, `PostHog.capture`, `PostHog.identify`, `PostHog.capture_exception`, `PostHog.evaluate_flags` and the other client methods are available on the `PostHog` module. If `PostHog.init` is never called, calls hit a disabled client and do nothing.
- **Request context** (`PostHog::Rails::RequestContext` middleware, inserted before `ActionDispatch::ShowExceptions`): every event captured during a web request gets `$current_url`, `$request_method`, `$request_path`, `$user_agent` and `$ip`. With `use_tracing_headers` (default `true`), the `X-POSTHOG-DISTINCT-ID` and `X-POSTHOG-SESSION-ID` request headers become the default `distinct_id` and `$session_id`. A `distinct_id` you pass explicitly always wins. These headers are client-controlled, so pass the authenticated ID yourself for anything security-sensitive.
- **Exception capture** (`CaptureExceptions` middleware, with `auto_capture_exceptions`): unhandled controller exceptions are sent as `$exception` events with the controller, action, filtered request params, response status and referrer. `RescuedExceptionInterceptor` (with `report_rescued_exceptions`) also reports exceptions Rails rescues and renders as error pages. Common 4xx exceptions (`ActiveRecord::RecordNotFound`, `ActionController::RoutingError`, `ActionController::ParameterMissing` and others) are excluded by default; add more with `config.excluded_exceptions`.
- **User context**: for captured exceptions, `capture_user_context` calls `current_user_method` on the controller and reads the distinct ID from the user. `user_id_method` wins when set; otherwise it tries `posthog_distinct_id`, `distinct_id`, `id`, `pk`, then `uuid`. This app sets `posthog_distinct_id` on `User` so the ID matches the one used for identify and for the browser.
- **`Rails.error` subscriber** (Rails 7+, needs `auto_capture_exceptions` and an initialized client): errors reported through `Rails.error.handle`, `Rails.error.record` and `Rails.error.report` are captured. `user_id` or `distinct_id` in the context hash becomes the distinct ID; other context keys become `$context_*` properties.
- **ActiveJob** (with `auto_instrument_active_job`): job failures are captured with `$job_class`, `$job_id`, `$queue_name` and sanitized arguments. The enqueuing request's distinct ID and session ID travel inside the job payload. A `posthog_distinct_id` class method on the job, or a `user_id` key in a hash argument, sets the ID for the job.
- **Action Cable** connections and channels are instrumented by the same Railtie.
- **Shutdown**: the Railtie registers an `at_exit` hook that calls `shutdown` on the client, which flushes queued events. No manual flush is needed on normal exit.

### What the app still does itself

- Calls `PostHog.identify` once at login and signup (`sessions_controller.rb`, `registrations_controller.rb`) to set person properties.
- Calls `PostHog.capture` for its own events; the SDK does not capture pageviews or business events on the server.
- Evaluates feature flags with `PostHog.evaluate_flags` and passes the user's distinct ID.
- Defines `posthog_distinct_id` on `User` and sets `current_user` in `ApplicationController`.
- Calls `PostHog.capture_exception` for errors it rescues itself.
- Passes the distinct ID to jobs.
- Runs `posthog.identify` in the browser with the same ID, and sets the `tracing_headers` hostname (see the layout).

### User model (app/models/user.rb)

```ruby
class User < ApplicationRecord
  has_secure_password

  # Called by posthog-rails for automatic user association in error reports.
  # The primary key, not the email — an email can change, which splits one
  # person's history in two, and it is PII on every event's identity.
  def posthog_distinct_id
    id.to_s
  end

  def posthog_properties
    { email: email, is_staff: is_staff, date_joined: created_at&.iso8601 }
  end
end
```

### User identification and signed-out visitors (app/controllers/sessions_controller.rb)

```ruby
# Identify the user and capture login event
PostHog.identify(
  distinct_id: user.posthog_distinct_id,
  properties: user.posthog_properties
)

PostHog.capture(
  distinct_id: user.posthog_distinct_id,
  event: 'user_logged_in',
  properties: { login_method: 'email' }
)
```

Every `PostHog.capture` in this app runs for a signed-in user, whose stable id is `posthog_distinct_id`, so the app never invents an id for a visitor. When a server event has no `distinct_id` (for example an exception on a signed-out request), posthog-ruby uses the request's `X-POSTHOG-DISTINCT-ID` header (the browser's own anonymous id, sent because of `tracing_headers`). If there is none, it generates a random UUID and sets `$process_person_profile: false` on the event, so signed-out visitors are never merged into one person. Do not pass a shared literal such as `"anonymous"` as the `distinct_id` ([anonymous vs identified events](https://posthog.com/docs/data/anonymous-vs-identified-events.md)).

### Feature flags (app/controllers/dashboard_controller.rb)

```ruby
# Evaluate flags once, then read values from the snapshot
flags = PostHog.evaluate_flags(
  user.posthog_distinct_id,
  person_properties: user.posthog_properties
)
@show_new_feature = flags.enabled?('new-dashboard-feature')
@feature_config = flags.get_flag_payload('new-dashboard-feature')
```

`PostHog.is_feature_enabled` and `get_feature_flag_payload` still work but are deprecated in favor of `evaluate_flags`.

### Error tracking — auto-capture

With `auto_capture_exceptions = true`, unhandled exceptions in controllers are captured automatically. No code needed:

```ruby
# This exception is automatically captured by posthog-rails
# with the current_user's posthog_distinct_id attached
def show
  raise "Something went wrong"  # Captured automatically!
end
```

### Error tracking — manual capture

```ruby
begin
  risky_operation
rescue => e
  PostHog.capture_exception(e, current_user.posthog_distinct_id)
end
```

### Error tracking — Rails.error integration

```ruby
# posthog-rails subscribes to Rails.error automatically
Rails.error.handle(context: { user_id: user.id }) do
  risky_operation
end
```

### ActiveJob instrumentation

```ruby
# config: auto_instrument_active_job = true
# Job failures are captured automatically.
# Use the posthog_distinct_id DSL to associate errors with a user.
class ExampleJob < ApplicationJob
  posthog_distinct_id ->(distinct_id, *) { distinct_id }

  def perform(distinct_id, should_fail: false)
    raise "Job failed"  # Captured automatically with user context
  end
end

# In the controller, pass the distinct_id when enqueuing:
ExampleJob.perform_later(current_user.posthog_distinct_id, should_fail: true)
```

## Frontend + Backend integration

This example includes the posthog-js snippet in the layout template to demonstrate how frontend and backend tracking work together.

### How it works

1. **posthog-js** (frontend) captures pageviews, clicks, and session replay
2. **posthog-ruby + posthog-rails** (backend) captures business logic events, errors, and feature flag evaluations
3. **Shared distinct_id** — frontend and backend events are linked when the same `distinct_id` is used on both sides. Call `posthog.identify(user.id.to_s)` in posthog-js after login, matching the `posthog_distinct_id` used on the backend
4. **Session replay** lets you watch user sessions where errors occurred

The layout sets `tracing_headers` so posthog-js adds `X-POSTHOG-DISTINCT-ID` and `X-POSTHOG-SESSION-ID` to requests to this app (needs posthog-js 1.380.0 or later). posthog-rails reads those headers in its request context, so backend events join the browser session even before a login.

The layout loads posthog-js only when `POSTHOG_PROJECT_TOKEN` is set, and passes `defaults: '2026-08-30'` so the SDK uses the current recommended behavior.

### When to track frontend vs backend

- **Frontend**: UI interactions, client-side errors, session replay, pageviews
- **Backend**: Business logic (signups, purchases), server errors, feature flag evaluations, background jobs

## Reverse proxy

Ad blockers block requests to known analytics domains, so browser events sent straight to PostHog can be lost. A reverse proxy sends them through a subdomain you own instead. The simplest option is the [managed reverse proxy](https://posthog.com/docs/advanced/proxy/managed-reverse-proxy.md): create it in your organization's proxy settings, add the CNAME record it gives you, and wait for it to go live. Then set `api_host` in the layout's `posthog.init` call to your proxy URL and add `ui_host` (`https://us.posthog.com` or `https://eu.posthog.com`) so the toolbar still works. Leave `POSTHOG_HOST` on the PostHog ingestion host: server-side events from posthog-ruby are not subject to browser ad blockers. PostHog's proxy docs have no Rails-specific pattern, so this example adds no proxy code.

## Learn more

- [PostHog Ruby on Rails integration](https://posthog.com/docs/libraries/ruby-on-rails)
- [posthog-rails source](https://github.com/PostHog/posthog-ruby/tree/main/posthog-rails)
- [PostHog Ruby SDK](https://posthog.com/docs/libraries/ruby)
- [PostHog Error Tracking](https://posthog.com/docs/error-tracking)
- [Ruby on Rails documentation](https://guides.rubyonrails.org/)

---

## .env.example

```example
# PostHog configuration
# Without POSTHOG_PROJECT_TOKEN the app still boots, with PostHog disabled
POSTHOG_PROJECT_TOKEN=phc_your_project_token_here
POSTHOG_HOST=https://us.i.posthog.com

```

---

## app/controllers/application_controller.rb

```rb
class ApplicationController < ActionController::Base
  protect_from_forgery with: :exception

  private

  def current_user
    @current_user ||= User.find_by(id: session[:user_id]) if session[:user_id]
  end
  helper_method :current_user

  def require_login
    unless current_user
      redirect_to login_path
    end
  end
end

```

---

## app/controllers/burritos_controller.rb

```rb
class BurritosController < ApplicationController
  before_action :require_login

  def show
    @burrito_count = session[:burrito_count] || 0
  end

  def consider
    count = (session[:burrito_count] || 0) + 1
    session[:burrito_count] = count

    user = current_user

    # PostHog: Track custom event. The user was identified at login or signup.
    PostHog.capture(
      distinct_id: user.posthog_distinct_id,
      event: 'burrito_considered',
      properties: { total_considerations: count }
    )

    render json: { success: true, count: count }
  end
end

```

---

## app/controllers/dashboard_controller.rb

```rb
class DashboardController < ApplicationController
  before_action :require_login

  def show
    user = current_user

    # PostHog: Track dashboard view
    PostHog.capture(
      distinct_id: user.posthog_distinct_id,
      event: 'dashboard_viewed',
      properties: { is_staff: user.is_staff }
    )

    # PostHog: Evaluate all flags once for this user, then read from the snapshot
    flags = PostHog.evaluate_flags(
      user.posthog_distinct_id,
      person_properties: user.posthog_properties
    )
    @show_new_feature = flags.enabled?('new-dashboard-feature')
    @feature_config = flags.get_flag_payload('new-dashboard-feature')
  end

  def enqueue_test_job
    # Enqueue a job that will fail — posthog-rails captures the error automatically.
    # The distinct_id is passed so the posthog_distinct_id DSL can associate the error with this user.
    ExampleJob.perform_later(current_user.posthog_distinct_id, should_fail: true)

    render json: {
      success: true,
      message: 'Job enqueued. The job will fail and posthog-rails will capture the error automatically.'
    }
  end
end

```

---

## app/controllers/errors_controller.rb

```rb
class ErrorsController < ApplicationController
  before_action :require_login

  def test
    # Manual exception capture — catch the error and report it explicitly
    begin
      raise StandardError, 'Test exception from critical operation'
    rescue StandardError => e
      # PostHog: Manually capture the exception
      PostHog.capture_exception(e, current_user.posthog_distinct_id)

      PostHog.capture(
        distinct_id: current_user.posthog_distinct_id,
        event: 'error_triggered',
        properties: {
          error_type: e.class.name,
          error_message: e.message
        }
      )

      render json: {
        success: false,
        error: e.message,
        message: 'Error has been captured by PostHog'
      }, status: :internal_server_error
    end
  end

  def test_rails_error
    # Rails.error.handle — Rails 7+ error reporting integration.
    # posthog-rails subscribes to Rails.error, so exceptions reported
    # via Rails.error.handle are automatically captured in PostHog.
    Rails.error.handle(context: { user_id: current_user.id }) do
      raise StandardError, 'Test error via Rails.error.handle — captured automatically by posthog-rails'
    end

    render json: {
      success: true,
      message: 'Error was handled via Rails.error.handle and captured by posthog-rails'
    }
  end
end

```

---

## app/controllers/profiles_controller.rb

```rb
class ProfilesController < ApplicationController
  before_action :require_login

  def show
    # PostHog: Track profile view
    PostHog.capture(
      distinct_id: current_user.posthog_distinct_id,
      event: 'profile_viewed'
    )
  end
end

```

---

## app/controllers/registrations_controller.rb

```rb
class RegistrationsController < ApplicationController
  def new
    redirect_to dashboard_path if current_user
  end

  def create
    user = User.new(
      email: params[:email],
      password: params[:password],
      password_confirmation: params[:password_confirmation]
    )

    if user.save
      session[:user_id] = user.id

      # PostHog: Identify the new user and capture signup event
      PostHog.identify(
        distinct_id: user.posthog_distinct_id,
        properties: user.posthog_properties
      )

      PostHog.capture(
        distinct_id: user.posthog_distinct_id,
        event: 'user_signed_up',
        properties: { signup_method: 'form' }
      )

      redirect_to dashboard_path
    else
      flash[:error] = user.errors.full_messages.join(', ')
      render :new, status: :unprocessable_entity
    end
  end
end

```

---

## app/controllers/sessions_controller.rb

```rb
class SessionsController < ApplicationController
  def new
    redirect_to dashboard_path if current_user
  end

  def create
    user = User.find_by(email: params[:email])

    if user&.authenticate(params[:password])
      session[:user_id] = user.id

      # PostHog: Identify the user and capture login event
      PostHog.identify(
        distinct_id: user.posthog_distinct_id,
        properties: user.posthog_properties
      )

      PostHog.capture(
        distinct_id: user.posthog_distinct_id,
        event: 'user_logged_in',
        properties: { login_method: 'email' }
      )

      redirect_to dashboard_path
    else
      flash[:error] = 'Invalid email or password'
      render :new, status: :unprocessable_entity
    end
  end

  def destroy
    if current_user
      # PostHog: Track logout before session ends
      PostHog.capture(
        distinct_id: current_user.posthog_distinct_id,
        event: 'user_logged_out'
      )
    end

    session.delete(:user_id)
    redirect_to login_path
  end
end

```

---

## app/jobs/application_job.rb

```rb
class ApplicationJob < ActiveJob::Base
end

```

---

## app/jobs/example_job.rb

```rb
# Example ActiveJob demonstrating posthog-rails auto-instrumentation.
#
# When auto_instrument_active_job is enabled in the PostHog config,
# posthog-rails automatically captures exceptions from failed jobs.
# The job class name, queue, and arguments are included as properties
# on the error event.
#
# Use the posthog_distinct_id DSL to associate job errors with a user.
# The proc receives the same arguments as perform and should return
# the distinct_id string. Without this, job errors have no user context.
class ExampleJob < ApplicationJob
  queue_as :default

  # Extract distinct_id from the first argument so posthog-rails
  # can associate the error with the user who triggered the job.
  posthog_distinct_id ->(distinct_id, *) { distinct_id }

  def perform(distinct_id, should_fail: false)
    if should_fail
      raise StandardError, 'Example job failure - this error is automatically captured by posthog-rails'
    end

    Rails.logger.info "ExampleJob completed successfully for #{distinct_id}"
  end
end

```

---

## app/models/application_record.rb

```rb
class ApplicationRecord < ActiveRecord::Base
  primary_abstract_class
end

```

---

## app/models/user.rb

```rb
class User < ApplicationRecord
  has_secure_password

  validates :email, presence: true, uniqueness: true

  # Called by posthog-rails for automatic user association in error reports.
  # When auto_capture_exceptions and capture_user_context are enabled,
  # posthog-rails calls this method on current_user to get the distinct_id.
  # The primary key, not the email: an email can change, which would split one
  # person's history in two, and it is PII on every event's identity.
  def posthog_distinct_id
    id.to_s
  end

  # Helper used by controllers when calling PostHog.identify to set person properties.
  # These properties appear on the person profile in PostHog.
  def posthog_properties
    {
      email: email,
      is_staff: is_staff,
      date_joined: created_at&.iso8601
    }
  end
end

```

---

## app/views/burritos/show.html.erb

```erb
<% content_for(:title) { 'Burrito - PostHog Rails example' } %>

<div class="card">
    <h1>Burrito consideration tracker</h1>
    <p>This page demonstrates custom event tracking with PostHog.</p>
</div>

<div class="card" style="text-align: center;">
    <h2>Times considered</h2>
    <div class="count" id="burrito-count"><%= @burrito_count %></div>
    <button onclick="considerBurrito()" style="font-size: 18px; padding: 15px 30px;">
        Consider a burrito
    </button>
</div>

<div class="card">
    <h3>How event tracking works</h3>
    <p>Each time you click the button, a <code>burrito_considered</code> event is sent to PostHog:</p>
    <pre style="background: #f3f4f6; padding: 15px; border-radius: 5px; overflow-x: auto; margin-top: 15px;"><code>PostHog.capture(
  distinct_id: user.posthog_distinct_id,
  event: 'burrito_considered',
  properties: { total_considerations: count }
)</code></pre>
</div>

<% content_for :scripts do %>
<script>
async function considerBurrito() {
    try {
        const response = await fetch('/api/burrito/consider', {
            method: 'POST',
            headers: {
                'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').content,
                'Content-Type': 'application/json',
            },
        });

        const data = await response.json();

        if (data.success) {
            document.getElementById('burrito-count').textContent = data.count;
        }
    } catch (error) {
        console.error('Error:', error);
    }
}
</script>
<% end %>

```

---

## app/views/dashboard/show.html.erb

```erb
<% content_for(:title) { 'Dashboard - PostHog Rails example' } %>

<div class="card">
    <h1>Dashboard</h1>
    <p>Welcome back, <strong><%= current_user.email %></strong>!</p>
</div>

<div class="card">
    <h2>Feature flags</h2>
    <p>Feature flags allow you to control feature rollouts and run A/B tests.</p>

    <% if @show_new_feature %>
    <div class="feature-flag">
        <h3>New feature enabled!</h3>
        <p>
            This section is only visible because the <code>new-dashboard-feature</code>
            flag is enabled for your user.
        </p>
        <% if @feature_config %>
        <p><strong>Feature config:</strong> <%= @feature_config %></p>
        <% end %>
    </div>
    <% else %>
    <div style="background: #f3f4f6; padding: 15px; border-radius: 8px; margin-top: 15px;">
        <p>
            The <code>new-dashboard-feature</code> flag is not enabled for your user.
            Create this flag in your PostHog project to see it in action.
        </p>
    </div>
    <% end %>
</div>

<div class="card">
    <h2>ActiveJob instrumentation</h2>
    <p>
        Click below to enqueue a background job that will fail.
        <code>posthog-rails</code> automatically captures the exception — no extra code needed.
    </p>
    <button onclick="enqueueTestJob()" style="margin-top: 10px;">Enqueue failing job</button>
    <div id="job-result" style="margin-top: 15px; display: none;"></div>
</div>

<div class="card">
    <h3>How feature flags work</h3>
    <pre style="background: #f3f4f6; padding: 15px; border-radius: 5px; overflow-x: auto;"><code># Evaluate flags once, then read from the snapshot
flags = PostHog.evaluate_flags(
  user.posthog_distinct_id,
  person_properties: user.posthog_properties
)
show_feature = flags.enabled?('new-dashboard-feature')

# Get feature flag payload for configuration
config = flags.get_flag_payload('new-dashboard-feature')</code></pre>
</div>

<% content_for :scripts do %>
<script>
async function enqueueTestJob() {
    const resultDiv = document.getElementById('job-result');
    try {
        const response = await fetch('/api/test-job', {
            method: 'POST',
            headers: {
                'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').content,
                'Content-Type': 'application/json',
            },
        });
        const data = await response.json();
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = '<div class="flash success">' + data.message + '</div>';
    } catch (error) {
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = '<div class="flash error">Request failed: ' + error + '</div>';
    }
}
</script>
<% end %>

```

---

## app/views/layouts/application.html.erb

```erb
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><%= content_for?(:title) ? yield(:title) : 'PostHog Rails example' %></title>
    <%= csrf_meta_tags %>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        nav {
            background: #1d4ed8;
            padding: 15px 20px;
            margin-bottom: 30px;
        }
        nav a {
            color: white;
            text-decoration: none;
            margin-right: 20px;
        }
        nav a:hover {
            text-decoration: underline;
        }
        .card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1, h2, h3 {
            margin-bottom: 15px;
            color: #1d4ed8;
        }
        button, .btn {
            background: #1d4ed8;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            display: inline-block;
            text-decoration: none;
        }
        button:hover, .btn:hover {
            background: #1e40af;
        }
        button.danger {
            background: #dc2626;
        }
        button.danger:hover {
            background: #b91c1c;
        }
        input {
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        .flash {
            padding: 10px 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .flash.error {
            background: #fee2e2;
            color: #dc2626;
        }
        .flash.success {
            background: #d1fae5;
            color: #059669;
        }
        .feature-flag {
            background: #fef3c7;
            border: 2px dashed #f59e0b;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        code {
            background: #f3f4f6;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
        }
        .count {
            font-size: 48px;
            font-weight: bold;
            color: #1d4ed8;
            text-align: center;
            padding: 20px;
        }
    </style>

    <% if ENV['POSTHOG_PROJECT_TOKEN'].present? %>
    <!-- PostHog frontend tracking (posthog-js) -->
    <script>
      // POSTHOG_BROWSER_SNIPPET_START
      !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],Object.defineProperty(u,"toString",{configurable:!0,enumerable:!0,writable:!0,value:function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e}}),Object.defineProperty(u.people,"toString",{configurable:!0,enumerable:!0,writable:!0,value:function(){return u.toString(1)+".people (stub)"}}),o="init capture register register_once register_for_session unregister unregister_for_session getFeatureFlag getFeatureFlagPayload isFeatureEnabled reloadFeatureFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset get_distinct_id getGroups get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording sessionRecordingStarted captureException loadToolbar get_property getSessionProperty createPersonProfile opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing clear_opt_in_out_capturing debug getPageViewId".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
      // POSTHOG_BROWSER_SNIPPET_END
      posthog.init('<%= ENV["POSTHOG_PROJECT_TOKEN"] %>', {
        api_host: '<%= ENV.fetch("POSTHOG_HOST", "https://us.i.posthog.com") %>',
        defaults: '2026-08-30',
        person_profiles: 'identified_only',
        // Send X-POSTHOG-DISTINCT-ID and X-POSTHOG-SESSION-ID on same-origin requests so
        // posthog-rails links backend events to the browser session
        tracing_headers: [window.location.hostname]
      })
      <% if current_user %>
      posthog.identify('<%= j current_user.posthog_distinct_id %>')
      <% end %>
    </script>
    <% end %>
</head>
<body>
    <% if current_user %>
    <nav style="display: flex; align-items: center;">
        <a href="<%= dashboard_path %>">Dashboard</a>
        <a href="<%= burrito_path %>">Burrito</a>
        <a href="<%= profile_path %>">Profile</a>
        <%= button_to 'Logout (' + current_user.email + ')', logout_path, method: :delete, form: { style: 'margin-left: auto;' }, style: 'background: transparent; border: none; color: white; cursor: pointer; font-size: inherit; padding: 0;' %>
    </nav>
    <% end %>

    <div class="container">
        <% if flash[:error] %>
        <div class="flash error"><%= flash[:error] %></div>
        <% end %>
        <% if flash[:notice] %>
        <div class="flash success"><%= flash[:notice] %></div>
        <% end %>

        <%= yield %>
    </div>

    <%= yield :scripts %>
</body>
</html>

```

---

## app/views/profiles/show.html.erb

```erb
<% content_for(:title) { 'Profile - PostHog Rails example' } %>

<div class="card">
    <h1>Profile</h1>
    <p>This page demonstrates error tracking with PostHog and <code>posthog-rails</code>.</p>
</div>

<div class="card">
    <h2>User information</h2>
    <table style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #eee;"><strong>Email:</strong></td>
            <td style="padding: 10px; border-bottom: 1px solid #eee;"><%= current_user.email %></td>
        </tr>
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #eee;"><strong>Date Joined:</strong></td>
            <td style="padding: 10px; border-bottom: 1px solid #eee;"><%= current_user.created_at %></td>
        </tr>
        <tr>
            <td style="padding: 10px;"><strong>Staff Status:</strong></td>
            <td style="padding: 10px;"><%= current_user.is_staff ? 'Yes' : 'No' %></td>
        </tr>
    </table>
</div>

<div class="card">
    <h2>Error tracking demo</h2>
    <p>Click the buttons below to trigger different types of errors and see how PostHog captures them.</p>

    <div style="margin-top: 20px;">
        <button class="danger" onclick="triggerError('manual')">
            Manual capture_exception
        </button>
        <button class="danger" onclick="triggerError('rails')" style="margin-left: 10px;">
            Rails.error.handle
        </button>
    </div>

    <div id="error-result" style="margin-top: 20px; display: none;"></div>
</div>

<div class="card">
    <h3>How error tracking works</h3>
    <p><strong>Auto-capture (no code needed):</strong></p>
    <pre style="background: #f3f4f6; padding: 15px; border-radius: 5px; overflow-x: auto;"><code># config/initializers/posthog.rb
PostHog::Rails.configure do |config|
  config.auto_capture_exceptions = true
  config.capture_user_context = true
end
# That's it! Unhandled exceptions are captured automatically.</code></pre>

    <p style="margin-top: 15px;"><strong>Manual capture:</strong></p>
    <pre style="background: #f3f4f6; padding: 15px; border-radius: 5px; overflow-x: auto;"><code>begin
  risky_operation
rescue => e
  PostHog.capture_exception(e, user.posthog_distinct_id)
end</code></pre>

    <p style="margin-top: 15px;"><strong>Rails.error integration:</strong></p>
    <pre style="background: #f3f4f6; padding: 15px; border-radius: 5px; overflow-x: auto;"><code># posthog-rails subscribes to Rails.error automatically
Rails.error.handle(context: { user_id: user.id }) do
  risky_operation
end</code></pre>
</div>

<% content_for :scripts do %>
<script>
async function triggerError(type) {
    const resultDiv = document.getElementById('error-result');
    const url = type === 'rails' ? '/api/test-rails-error' : '/api/test-error';

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').content,
                'Content-Type': 'application/json',
            },
        });

        const data = await response.json();

        resultDiv.style.display = 'block';
        if (data.success) {
            resultDiv.innerHTML = '<div class="flash success">' + data.message + '</div>';
        } else {
            resultDiv.innerHTML = '<div class="flash error"><strong>Error captured:</strong> ' + data.error + '<br><small>' + data.message + '</small></div>';
        }
    } catch (error) {
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = '<div class="flash error">Request failed: ' + error + '</div>';
    }
}
</script>
<% end %>

```

---

## app/views/registrations/new.html.erb

```erb
<% content_for(:title) { 'Sign Up - PostHog Rails example' } %>

<div class="card">
    <h1>Sign Up</h1>
    <p>Create an account to see PostHog analytics in action.</p>

    <form action="<%= signup_path %>" method="post" style="margin-top: 20px;">
        <%= hidden_field_tag :authenticity_token, form_authenticity_token %>
        <input type="email" name="email" placeholder="Email" required>
        <input type="password" name="password" placeholder="Password" required>
        <input type="password" name="password_confirmation" placeholder="Confirm Password" required>
        <button type="submit">Sign Up</button>
    </form>

    <p style="margin-top: 15px; color: #666; font-size: 14px;">
        Already have an account? <a href="<%= login_path %>">Login</a>
    </p>
</div>

```

---

## app/views/sessions/new.html.erb

```erb
<% content_for(:title) { 'Login - PostHog Rails example' } %>

<div class="card">
    <h1>PostHog Rails example</h1>
    <p>Welcome! This example demonstrates PostHog integration with Ruby on Rails, including automatic error tracking via <code>posthog-rails</code>.</p>
</div>

<div class="card">
    <h2>Login</h2>
    <p>Login to see PostHog analytics in action.</p>

    <form action="<%= login_path %>" method="post" style="margin-top: 20px;">
        <%= hidden_field_tag :authenticity_token, form_authenticity_token %>
        <input type="email" name="email" placeholder="Email" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Login</button>
    </form>

    <p style="margin-top: 15px; color: #666; font-size: 14px;">
        Don't have an account? <a href="<%= signup_path %>">Sign up</a><br>
        Tip: Run <code>bin/rails db:seed</code> to create admin@example.com / admin
    </p>
</div>

<div class="card">
    <h3>What this example demonstrates</h3>
    <ul style="padding-left: 20px;">
        <li><strong>User identification</strong> — Users are identified with <code>PostHog.identify</code> on login</li>
        <li><strong>Event tracking</strong> — Custom events captured with <code>PostHog.capture</code></li>
        <li><strong>Feature flags</strong> — Conditional features with <code>PostHog.is_feature_enabled</code></li>
        <li><strong>Error tracking (auto)</strong> — Unhandled exceptions captured automatically by <code>posthog-rails</code></li>
        <li><strong>Error tracking (manual)</strong> — Handled errors captured with <code>PostHog.capture_exception</code></li>
        <li><strong>ActiveJob instrumentation</strong> — Background job failures captured automatically</li>
        <li><strong>Rails.error integration</strong> — Rails 7+ error reporting captured by <code>posthog-rails</code></li>
        <li><strong>Frontend tracking</strong> — posthog-js captures pageviews and session replay</li>
    </ul>
</div>

```

---

## config.ru

```ru
require_relative 'config/environment'
run Rails.application

```

---

## config/application.rb

```rb
require_relative 'boot'
require 'rails/all'

Bundler.require(*Rails.groups)

module PosthogExample
  class Application < Rails::Application
    config.load_defaults 7.1

    # Use SQLite for all stores
    config.active_job.queue_adapter = :async
  end
end

```

---

## config/boot.rb

```rb
ENV['BUNDLE_GEMFILE'] ||= File.expand_path('../Gemfile', __dir__)

require 'bundler/setup'

```

---

## config/environment.rb

```rb
require_relative 'application'
Rails.application.initialize!

```

---

## config/environments/development.rb

```rb
require 'active_support/core_ext/integer/time'

Rails.application.configure do
  config.enable_reloading = true
  config.eager_load = false
  config.consider_all_requests_local = true
  config.server_timing = true

  # Secret key for development (not used in production)
  config.secret_key_base = 'dev-secret-key-for-posthog-example-only'

  config.action_controller.perform_caching = false
  config.cache_store = :memory_store

  config.active_support.deprecation = :log
  config.active_support.disallowed_deprecation = :raise
  config.active_support.disallowed_deprecation_warnings = []

  config.active_record.migration_error = :page_load
  config.active_record.verbose_query_logs = true
end

```

---

## config/initializers/posthog.rb

```rb
# PostHog configuration. The posthog-rails gem wires the integration into Rails
# (middleware, Rails.error subscriber, ActiveJob hooks, shutdown); this file only
# chooses which of those are on and creates the single client.
# See the "What the integration sets up for you" section of the README.

PostHog::Rails.configure do |config|
  # Capture unhandled controller exceptions and Rails.error reports
  config.auto_capture_exceptions = true

  # Also capture exceptions Rails rescues and renders as error pages
  config.report_rescued_exceptions = true

  # Capture ActiveJob failures and carry the request's identity into jobs
  config.auto_instrument_active_job = true

  # Attach the signed-in user to captured exceptions. These are the defaults,
  # shown so the contract with the User model is visible.
  config.capture_user_context = true
  config.current_user_method = :current_user
  config.user_id_method = :posthog_distinct_id
end

project_token = ENV['POSTHOG_PROJECT_TOKEN'].to_s.strip

if project_token.empty?
  # Without PostHog.init the client stays disabled and every PostHog call is a no-op.
  if Rails.env.development?
    Rails.logger.warn('POSTHOG_PROJECT_TOKEN is not set; PostHog is disabled. Copy .env.example to .env and set it.')
  end
else
  PostHog.init do |config|
    config.api_key = project_token
    config.host = ENV.fetch('POSTHOG_HOST', 'https://us.i.posthog.com')
    config.test_mode = true if Rails.env.test?
    config.on_error = proc { |status, msg| Rails.logger.error("PostHog error (#{status}): #{msg}") }
  end
end

```

---

## config/routes.rb

```rb
Rails.application.routes.draw do
  # Auth
  get 'login', to: 'sessions#new'
  post 'login', to: 'sessions#create'
  delete 'logout', to: 'sessions#destroy'

  get 'signup', to: 'registrations#new'
  post 'signup', to: 'registrations#create'

  # App
  get 'dashboard', to: 'dashboard#show'
  get 'burrito', to: 'burritos#show'
  post 'api/burrito/consider', to: 'burritos#consider'
  get 'profile', to: 'profiles#show'

  # Error tracking demos
  post 'api/test-error', to: 'errors#test'
  post 'api/test-rails-error', to: 'errors#test_rails_error'

  # Background job demo
  post 'api/test-job', to: 'dashboard#enqueue_test_job'

  root 'sessions#new'
end

```

---

## db/migrate/20240101000000_create_users.rb

```rb
class CreateUsers < ActiveRecord::Migration[7.1]
  def change
    create_table :users do |t|
      t.string :email, null: false
      t.string :password_digest, null: false
      t.boolean :is_staff, default: false

      t.timestamps
    end

    add_index :users, :email, unique: true
  end
end

```

---

## db/schema.rb

```rb
# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[7.2].define(version: 2024_01_01_000000) do
  create_table "users", force: :cascade do |t|
    t.string "email", null: false
    t.string "password_digest", null: false
    t.boolean "is_staff", default: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["email"], name: "index_users_on_email", unique: true
  end
end

```

---

## db/seeds.rb

```rb
# Create a default admin user for testing
User.find_or_create_by!(email: 'admin@example.com') do |user|
  user.password = 'admin'
  user.password_confirmation = 'admin'
  user.is_staff = true
end

puts 'Seed data created: admin@example.com / admin'

```

---

## Gemfile

```
source 'https://rubygems.org'

gem 'rails', '~> 7.1'
gem 'sqlite3', '~> 1.7'
gem 'puma', '~> 6.0'
gem 'bcrypt', '~> 3.1'
gem 'dotenv-rails', '~> 3.0'

# PostHog
gem 'posthog-ruby', '~> 3.0', require: 'posthog'
gem 'posthog-rails'

```

---

## Rakefile

```
require_relative 'config/application'
Rails.application.load_tasks

```

---

