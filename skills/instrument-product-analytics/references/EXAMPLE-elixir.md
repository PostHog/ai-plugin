# PostHog elixir Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/elixir

---

## README.md

# PostHog Phoenix (Elixir) example

This is a [Phoenix](https://www.phoenixframework.org/) example demonstrating PostHog integration with product analytics, feature flags, user identification, and error tracking using the server-side [`posthog`](https://hex.pm/packages/posthog) Elixir SDK.

## Features

- **Product analytics**: Track user events and behaviors
- **User identification**: Associate events with users via the `distinct_id` on capture; signed-out visitors get a per-visit random id and personless events
- **Feature flags**: Control feature rollouts with PostHog feature flags
- **Error tracking**: Automatic exception + `Logger.error` capture (built into the SDK)
- **Server-side tracking**: All tracking happens server-side with the Elixir SDK
- **Single client per app**: The SDK starts one supervised client for the whole app
- **Context plug**: `PostHog.Integrations.Plug` tags every request automatically

> **Note on error tracking:** unlike the Java/Python examples, the PostHog Elixir
> SDK captures errors **automatically** — it hooks into Elixir's `Logger`, so any
> `Logger.error` call and any uncaught exception is reported without an explicit
> call. There is no documented `capture_exception` function, so the profile page
> demonstrates the idiomatic path (`Logger.error`) plus an explicit
> `error_occurred` event.

## Getting started

### 1. Install dependencies

```bash
mix deps.get
```

### 2. Configure environment variables

Copy `.env.example` to `.env`, fill in your values, then export them:

```bash
export POSTHOG_PROJECT_TOKEN=your_posthog_project_token
export POSTHOG_HOST=https://us.i.posthog.com
```

Get your PostHog project token from your [PostHog project settings](https://app.posthog.com/project/settings).

### 3. Run the development server

```bash
mix phx.server
```

Open [http://localhost:8000](http://localhost:8000) with your browser to see the app.

## Project structure

```
elixir/
├── mix.exs                          # Project + the posthog dependency
├── .env.example                     # Environment variable template
├── .gitignore
├── config/
│   ├── config.exs                   # Endpoint + PostHog SDK config (enable, otp apps)
│   └── runtime.exs                  # Reads POSTHOG_* env vars at boot
└── lib/
    ├── posthog_example/
    │   └── application.ex            # OTP app; warns loudly on a blank token
    ├── posthog_example_web.ex        # controller / html / router helpers
    └── posthog_example_web/
        ├── endpoint.ex               # Plug pipeline incl. PostHog.Integrations.Plug
        ├── router.ex                 # Routes for the burrito app
        └── controllers/
            ├── burrito_controller.ex # Events, identify, flags, errors
            ├── burrito_html.ex       # Tiny HEEx pages
            ├── layouts.ex            # Root layout
            └── error_html.ex         # Error pages
```

## What the integration sets up for you

From the SDK docs (https://posthog.com/docs/libraries/elixir):

**Automatic**

- The SDK starts and supervises its own client when `config :posthog, enable: true`, and attaches a logger handler. You add nothing to your supervision tree.
- Events are batched and sent by a background job.
- Error tracking is on by default: uncaught exceptions and `Logger.error` calls are captured (turn it off with `enable_error_tracking: false`).
- `PostHog.Integrations.Plug` adds `$current_url`, `$host`, `$pathname`, `$request_method`, `$user_agent` and `$ip` to events captured during a request, and reads the `X-PostHog-Distinct-Id` and `X-PostHog-Session-Id` headers as default context.
- Context set with `PostHog.set_context/1` is stored in `Logger` metadata and attached to events captured in the same process.

**Still done by the app**

- Capturing every event with `PostHog.capture/2`; the plug captures nothing by itself.
- Choosing the `distinct_id` (signed-in id, or a per-visitor UUID) and passing it or putting it in context.
- Evaluating feature flags with `PostHog.FeatureFlags.evaluate_flags/1`.
- Reading the token and host from the environment in `config/runtime.exs`.
- A missing token: the SDK itself logs a warning and starts in disabled/no-op mode, and `application.ex` adds a warning naming `POSTHOG_PROJECT_TOKEN`. The app still boots.

This example loads no browser SDK, so there is no `posthog-js` or reverse proxy setup here. If you add `posthog-js`, set `defaults: '2026-08-30'` and see the [managed reverse proxy](https://posthog.com/docs/advanced/proxy/managed-reverse-proxy.md).

## Key integration points

### Configuration from the environment (config/runtime.exs)

`runtime.exs` runs at boot, so it can read environment variables. The token and host never live in source.

```elixir
config :posthog,
  api_key: System.get_env("POSTHOG_PROJECT_TOKEN"),
  api_host: System.get_env("POSTHOG_HOST") || "https://us.i.posthog.com"
```

### SDK init — one client per app (config/config.exs)

The SDK starts and supervises a single client for the whole app automatically. You only turn it on and tell it which OTP app is "in app" for error grouping:

```elixir
config :posthog,
  enable: true,
  in_app_otp_apps: [:posthog_example]
```

A blank token doesn't crash the app — `application.ex` logs a clear warning and boots anyway.

### Context plug (lib/posthog_example_web/endpoint.ex)

Add the built-in plug before your router. It wraps each request in a PostHog context: it attaches request metadata (`$current_url`, `$host`, `$pathname`, …) and reads the `X-PostHog-Distinct-Id` / `X-PostHog-Session-Id` tracing headers to link backend and frontend events.

```elixir
plug PostHog.Integrations.Plug
plug PostHogExampleWeb.Router
```

### User identification and signed-out visitors (lib/posthog_example_web/controllers/burrito_controller.ex)

The Elixir SDK has no separate server-side `identify` step. You identify a user by passing their `distinct_id` on `capture`. It must match the id your frontend `posthog.identify(...)` uses so both sides attach to the same person.

```elixir
PostHog.capture("user_logged_in", %{
  distinct_id: distinct_id,
  login_method: "email"
})
```

A `plug :assign_identity` in the controller picks the id for every request:

- **Signed in**: the stable id stored in the session at login.
- **Signed out**: a random UUID generated once and kept in the session (`:visitor_id`), so it is reused for the whole visit. Each visitor gets their own id; a shared literal such as `"anonymous"` would merge every signed-out visitor into one person.

Events from signed-out visitors carry `$process_person_profile: false`, so PostHog stores them without creating a person profile ([anonymous vs identified events](https://posthog.com/docs/data/anonymous-vs-identified-events.md)). The plug also calls `PostHog.set_context/1` with the same `distinct_id` (and the personless flag), so events and errors the SDK captures later in the request use it too. Feature-flag checks use the same id, signed in or not.

### Event tracking (lib/posthog_example_web/controllers/burrito_controller.ex)

`distinct_id` is required; every other key in the map becomes an event property.

```elixir
PostHog.capture("burrito_considered", %{
  distinct_id: distinct_id,
  total_considerations: count
})
```

### Feature flags (lib/posthog_example_web/controllers/burrito_controller.ex)

Evaluate flags once per request, then read individual flags off the returned snapshot.

```elixir
show_new_feature =
  case PostHog.FeatureFlags.evaluate_flags(distinct_id) do
    {:ok, snapshot} ->
      PostHog.FeatureFlags.Evaluations.enabled?(snapshot, "new-dashboard-feature")

    _error ->
      false
  end
```

### Error tracking (lib/posthog_example_web/controllers/burrito_controller.ex)

Error tracking is **automatic** — the SDK is built on Elixir's `Logger`, so uncaught exceptions and `Logger.error` calls are captured with no explicit call. There is no documented `capture_exception`, so we log the error (auto-captured) and also send an explicit analytics event:

```elixir
try do
  raise "Something went wrong while loading the burrito profile!"
rescue
  error ->
    Logger.error("Burrito profile error: #{Exception.message(error)}")

    PostHog.capture("error_occurred", %{
      distinct_id: distinct_id,
      error_message: Exception.message(error)
    })
end
```

Disable automatic capture with `config :posthog, enable_error_tracking: false`.

## Learn more

- [PostHog Elixir SDK](https://posthog.com/docs/libraries/elixir)
- [PostHog feature flags](https://posthog.com/docs/feature-flags)
- [PostHog documentation](https://posthog.com/docs)
- [Phoenix framework](https://www.phoenixframework.org/)

---

## .env.example

```example
# Copy to .env and fill in, then export the values before running the app:
#   export $(grep -v '^#' .env | xargs)
POSTHOG_PROJECT_TOKEN=your_posthog_project_token
POSTHOG_HOST=https://us.i.posthog.com

```

---

## config/config.exs

```exs
import Config

# Endpoint configuration. The secret_key_base here is a throwaway dev value;
# override it in prod via runtime.exs / an environment variable.
config :posthog_example, PostHogExampleWeb.Endpoint,
  url: [host: "localhost"],
  adapter: Bandit.PhoenixAdapter,
  http: [ip: {127, 0, 0, 1}, port: 8000],
  render_errors: [formats: [html: PostHogExampleWeb.ErrorHTML], layout: false],
  secret_key_base:
    "dev_only_secret_key_base_replace_in_prod_0123456789abcdefghijklmnopqrstuvwxyz",
  server: true

# PostHog SDK — one client per app, started automatically by the SDK's
# own supervisor. The token and host are read from the environment in
# config/runtime.exs so secrets never live in source control.
#
#   enable            -> master on/off switch for the SDK
#   in_app_otp_apps   -> which OTP apps' stack frames count as "in app" for
#                        automatic error tracking (grouping / noise control)
config :posthog,
  enable: true,
  in_app_otp_apps: [:posthog_example]

config :phoenix, :json_library, Jason

```

---

## config/runtime.exs

```exs
import Config

# runtime.exs runs at boot in every environment, which makes it the right
# place to read environment variables (they are not available at compile time).

# Configuration from the environment. Never hardcode the token.
#   POSTHOG_PROJECT_TOKEN -> your project's write key
#   POSTHOG_HOST          -> defaults to PostHog US Cloud
config :posthog,
  api_key: System.get_env("POSTHOG_PROJECT_TOKEN"),
  api_host: System.get_env("POSTHOG_HOST") || "https://us.i.posthog.com"

# In production, require a real secret_key_base from the environment.
if config_env() == :prod do
  secret_key_base =
    System.get_env("SECRET_KEY_BASE") ||
      raise "SECRET_KEY_BASE is missing. Generate one with `mix phx.gen.secret`."

  config :posthog_example, PostHogExampleWeb.Endpoint,
    http: [ip: {0, 0, 0, 0}, port: String.to_integer(System.get_env("PORT") || "8000")],
    secret_key_base: secret_key_base
end

```

---

## lib/posthog_example_web.ex

```ex
defmodule PostHogExampleWeb do
  @moduledoc """
  Entry points for the web layer: controllers, HTML views, and the router.

  Use it with `use PostHogExampleWeb, :controller`, `use PostHogExampleWeb, :html`,
  or `use PostHogExampleWeb, :router`.
  """

  def router do
    quote do
      use Phoenix.Router, helpers: false

      import Plug.Conn
      import Phoenix.Controller
    end
  end

  def controller do
    quote do
      use Phoenix.Controller,
        formats: [:html],
        layouts: [html: PostHogExampleWeb.Layouts]

      import Plug.Conn
      unquote(verified_routes())
    end
  end

  def html do
    quote do
      use Phoenix.Component

      import Phoenix.Controller, only: [get_csrf_token: 0]
      unquote(verified_routes())
    end
  end

  def verified_routes do
    quote do
      use Phoenix.VerifiedRoutes,
        endpoint: PostHogExampleWeb.Endpoint,
        router: PostHogExampleWeb.Router
    end
  end

  @doc """
  Dispatches to the appropriate helper (controller / html / router / ...).
  """
  defmacro __using__(which) when is_atom(which) do
    apply(__MODULE__, which, [])
  end
end

```

---

## lib/posthog_example_web/controllers/burrito_controller.ex

```ex
defmodule PostHogExampleWeb.BurritoController do
  @moduledoc """
  The whole burrito app, and every PostHog integration point:

    * user identification  -> /login
    * event tracking       -> /burrito
    * feature flags        -> /dashboard
    * error tracking       -> /profile (see the note in `trigger_error/2`)

  All PostHog calls use the documented v2.0 SDK API:
  https://posthog.com/docs/libraries/elixir
  """

  use PostHogExampleWeb, :controller
  require Logger

  plug :assign_identity

  # ---------------------------------------------------------------------------
  # Home / login
  # ---------------------------------------------------------------------------

  def home(conn, _params) do
    render(conn, :home, distinct_id: conn.assigns.distinct_id)
  end

  @doc """
  Identify the user.

  The PostHog Elixir SDK has no separate `identify` step for server events —
  you identify a user by passing their `distinct_id` on `capture`. The
  `distinct_id` must match the id your frontend `posthog.identify(...)` uses,
  so events from both sides attach to the same person.

  We derive a stable distinct id from the username and remember it in the
  session so every later request captures against the same person.

  Identity note: this demo takes the username from an unverified form field for
  simplicity. A real app must derive `distinct_id` from the authenticated
  principal (session / token), never from an unverified request param — otherwise
  a client could pick any id and overwrite another person's profile.
  """
  def login(conn, params) do
    username = params["username"] || "burrito_fan"
    distinct_id = "user_" <> username

    # PostHog: identify + capture in one call. Extra keys in the map become
    # event properties.
    PostHog.capture("user_logged_in", %{
      distinct_id: distinct_id,
      login_method: "email"
    })

    conn
    |> put_session(:distinct_id, distinct_id)
    |> redirect(to: ~p"/dashboard")
  end

  def logout(conn, _params) do
    # Capture before we drop the session so the event is still attributed.
    capture(conn, "user_logged_out")

    conn
    |> delete_session(:distinct_id)
    |> redirect(to: ~p"/")
  end

  # ---------------------------------------------------------------------------
  # Event tracking
  # ---------------------------------------------------------------------------

  def burrito(conn, _params) do
    render(conn, :burrito, count: get_session(conn, :burrito_count) || 0)
  end

  @doc "Track a custom `burrito_considered` event with properties."
  def consider_burrito(conn, _params) do
    count = (get_session(conn, :burrito_count) || 0) + 1

    # PostHog: custom event. `distinct_id` is required; the rest are properties.
    capture(conn, "burrito_considered", %{total_considerations: count})

    conn
    |> put_session(:burrito_count, count)
    |> redirect(to: ~p"/burrito")
  end

  # ---------------------------------------------------------------------------
  # Feature flags
  # ---------------------------------------------------------------------------

  @doc """
  Evaluate flags once per request, then read individual flags off the snapshot.
  """
  def dashboard(conn, _params) do
    distinct_id = conn.assigns.distinct_id

    show_new_feature =
      case PostHog.FeatureFlags.evaluate_flags(distinct_id) do
        {:ok, snapshot} ->
          PostHog.FeatureFlags.Evaluations.enabled?(snapshot, "new-dashboard-feature")

        _error ->
          # Fail safe: if flag evaluation fails, fall back to "off".
          false
      end

    capture(conn, "dashboard_viewed")

    render(conn, :dashboard, show_new_feature: show_new_feature)
  end

  # ---------------------------------------------------------------------------
  # Error tracking
  # ---------------------------------------------------------------------------

  def profile(conn, _params) do
    capture(conn, "profile_viewed")
    message = get_session(conn, :message)

    conn
    |> delete_session(:message)
    |> render(:profile, distinct_id: conn.assigns.distinct_id, message: message)
  end

  @doc """
  Demonstrate error tracking.

  PostHog's Elixir SDK does error tracking *automatically*: it is built on top
  of Elixir's `Logger`, so any `Logger.error/1` call and any uncaught exception
  is captured — there is no documented explicit `capture_exception` function.

  So here we `rescue` a deliberate exception and report it two ways:

    1. `Logger.error(...)` — which the SDK auto-captures as an exception, and
    2. an explicit `error_occurred` custom event for easy funnel/analytics use.
  """
  def trigger_error(conn, _params) do
    try do
      raise "Something went wrong while loading the burrito profile!"
    rescue
      error ->
        # PostHog auto-captures this Logger.error as an exception.
        Logger.error("Burrito profile error: #{Exception.message(error)}")

        # Plus an explicit analytics event, matching the other examples.
        capture(conn, "error_occurred", %{
          error_type: error.__struct__ |> Module.split() |> List.last(),
          error_message: Exception.message(error)
        })
    end

    conn
    |> put_flash_message("Error triggered and captured by PostHog.")
    |> redirect(to: ~p"/profile")
  end

  # ---------------------------------------------------------------------------
  # Helpers
  # ---------------------------------------------------------------------------

  # Signed-in users keep their stable id. A signed-out visitor gets a random
  # UUID that lives in the session for the whole visit, and their events are
  # captured without a person profile. Never share one id such as "anonymous"
  # across visitors: PostHog would merge them into a single person.
  defp assign_identity(conn, _opts) do
    {conn, distinct_id, anonymous?} =
      case get_session(conn, :distinct_id) do
        nil ->
          conn = ensure_visitor_id(conn)
          {conn, get_session(conn, :visitor_id), true}

        distinct_id ->
          {conn, distinct_id, false}
      end

    # Context is attached to everything captured later in this request,
    # including errors the SDK captures from Logger.
    PostHog.set_context(
      if anonymous?,
        do: %{distinct_id: distinct_id, "$process_person_profile": false},
        else: %{distinct_id: distinct_id}
    )

    conn |> assign(:distinct_id, distinct_id) |> assign(:anonymous?, anonymous?)
  end

  defp ensure_visitor_id(conn) do
    if get_session(conn, :visitor_id), do: conn, else: put_session(conn, :visitor_id, uuid4())
  end

  # Capture against the request's identity; anonymous visitors are personless.
  defp capture(conn, event, properties \\ %{}) do
    properties = Map.put(properties, :distinct_id, conn.assigns.distinct_id)

    properties =
      if conn.assigns.anonymous?,
        do: Map.put(properties, :"$process_person_profile", false),
        else: properties

    PostHog.capture(event, properties)
  end

  defp uuid4 do
    <<a::48, _::4, b::12, _::2, c::62>> = :crypto.strong_rand_bytes(16)
    hex = Base.encode16(<<a::48, 4::4, b::12, 2::2, c::62>>, case: :lower)

    <<p1::binary-8, p2::binary-4, p3::binary-4, p4::binary-4, p5::binary-12>> = hex
    Enum.join([p1, p2, p3, p4, p5], "-")
  end

  # Tiny session-backed flash (this app doesn't wire the full Phoenix flash).
  defp put_flash_message(conn, message), do: put_session(conn, :message, message)
end

```

---

## lib/posthog_example_web/controllers/burrito_html.ex

```ex
defmodule PostHogExampleWeb.BurritoHTML do
  @moduledoc "Tiny HEEx pages for the burrito app."
  use PostHogExampleWeb, :html

  def home(assigns) do
    ~H"""
    <h1>🌯 Burrito app</h1>
    <p>Signed in as: <strong><%= @distinct_id %></strong></p>
    <form method="post" action="/login">
      <input type="hidden" name="_csrf_token" value={get_csrf_token()} />
      <label>Username <input type="text" name="username" value="burrito_fan" /></label>
      <button type="submit">Log in</button>
    </form>
    """
  end

  def burrito(assigns) do
    ~H"""
    <h1>Consider a burrito</h1>
    <p>You have considered a burrito <strong><%= @count %></strong> time(s).</p>
    <form method="post" action="/burrito">
      <input type="hidden" name="_csrf_token" value={get_csrf_token()} />
      <button type="submit">Consider a burrito</button>
    </form>
    """
  end

  def dashboard(assigns) do
    ~H"""
    <h1>Dashboard</h1>
    <p :if={@show_new_feature} class="flag-on">
      ✨ The <code>new-dashboard-feature</code> flag is <strong>ON</strong>.
    </p>
    <p :if={!@show_new_feature} class="flag-off">
      The <code>new-dashboard-feature</code> flag is off (default).
    </p>
    """
  end

  def profile(assigns) do
    ~H"""
    <h1>Profile</h1>
    <p>Distinct id: <strong><%= @distinct_id %></strong></p>
    <p :if={@message}><em><%= @message %></em></p>
    <form method="post" action="/profile/error">
      <input type="hidden" name="_csrf_token" value={get_csrf_token()} />
      <button type="submit">Trigger an error</button>
    </form>
    <p><a href="/logout">Log out</a></p>
    """
  end
end

```

---

## lib/posthog_example_web/controllers/error_html.ex

```ex
defmodule PostHogExampleWeb.ErrorHTML do
  @moduledoc "Renders plain-text status pages for errors (e.g. 404, 500)."
  use PostHogExampleWeb, :html

  # e.g. render("404.html", _) -> "Not Found"
  def render(template, _assigns) do
    Phoenix.Controller.status_message_from_template(template)
  end
end

```

---

## lib/posthog_example_web/controllers/layouts.ex

```ex
defmodule PostHogExampleWeb.Layouts do
  @moduledoc "The root layout wrapping every page."
  use PostHogExampleWeb, :html

  # The app layout wraps each page's content and is itself wrapped by root/1.
  # Controllers apply it by default (see the `layouts:` option in
  # posthog_example_web.ex); without it every render fails with
  # "no app html template defined".
  def app(assigns) do
    ~H"""
    {@inner_content}
    """
  end

  def root(assigns) do
    ~H"""
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>PostHog Elixir example</title>
        <style>
          body { font-family: system-ui, sans-serif; max-width: 40rem; margin: 3rem auto; padding: 0 1rem; }
          nav a { margin-right: 1rem; }
          .flag-on { color: #2e7d32; } .flag-off { color: #999; }
        </style>
      </head>
      <body>
        <nav>
          <a href="/">Home</a>
          <a href="/burrito">Burrito</a>
          <a href="/dashboard">Dashboard</a>
          <a href="/profile">Profile</a>
        </nav>
        <hr />
        <%= @inner_content %>
      </body>
    </html>
    """
  end
end

```

---

## lib/posthog_example_web/endpoint.ex

```ex
defmodule PostHogExampleWeb.Endpoint do
  use Phoenix.Endpoint, otp_app: :posthog_example

  # The session is stored in a signed cookie. We use it to remember the
  # logged-in user's stable distinct id across requests.
  @session_options [
    store: :cookie,
    key: "_posthog_example_key",
    signing_salt: "kE9xVq2p",
    same_site: "Lax"
  ]

  plug Plug.RequestId
  plug Plug.Telemetry, event_prefix: [:phoenix, :endpoint]

  plug Plug.Parsers,
    parsers: [:urlencoded, :multipart, :json],
    pass: ["*/*"],
    json_decoder: Phoenix.json_library()

  plug Plug.MethodOverride
  plug Plug.Head
  plug Plug.Session, @session_options

  # PostHog's built-in Plug. Placed before the router so every request is
  # wrapped in a PostHog context: it attaches request metadata ($current_url,
  # $host, $pathname, ...) and reads the X-PostHog-Distinct-Id /
  # X-PostHog-Session-Id tracing headers to link backend and frontend events.
  plug PostHog.Integrations.Plug

  plug PostHogExampleWeb.Router
end

```

---

## lib/posthog_example_web/router.ex

```ex
defmodule PostHogExampleWeb.Router do
  use PostHogExampleWeb, :router

  pipeline :browser do
    plug :accepts, ["html"]
    plug :fetch_session
    plug :put_root_layout, html: {PostHogExampleWeb.Layouts, :root}
    plug :protect_from_forgery
    plug :put_secure_browser_headers
  end

  scope "/", PostHogExampleWeb do
    pipe_through :browser

    get "/", BurritoController, :home
    post "/login", BurritoController, :login
    get "/logout", BurritoController, :logout

    get "/burrito", BurritoController, :burrito
    post "/burrito", BurritoController, :consider_burrito

    get "/dashboard", BurritoController, :dashboard

    get "/profile", BurritoController, :profile
    post "/profile/error", BurritoController, :trigger_error
  end
end

```

---

## lib/posthog_example/application.ex

```ex
defmodule PostHogExample.Application do
  @moduledoc false

  use Application
  require Logger

  @impl true
  def start(_type, _args) do
    warn_if_token_missing()

    children = [
      PostHogExampleWeb.Endpoint
    ]

    opts = [strategy: :one_for_one, name: PostHogExample.Supervisor]
    Supervisor.start_link(children, opts)
  end

  @impl true
  def config_change(changed, _new, removed) do
    PostHogExampleWeb.Endpoint.config_change(changed, removed)
    :ok
  end

  # Fail loudly, but don't break the app: with a blank token the SDK simply
  # won't deliver events. We log a clear warning and let the app boot.
  defp warn_if_token_missing do
    case Application.get_env(:posthog, :api_key) do
      token when token in [nil, ""] ->
        Logger.warning(
          "POSTHOG_PROJECT_TOKEN is not set — PostHog events will not be delivered. " <>
            "The app will still run. Set it in your environment to enable analytics."
        )

      _token ->
        :ok
    end
  end
end

```

---

## mix.exs

```exs
defmodule PostHogExample.MixProject do
  use Mix.Project

  def project do
    [
      app: :posthog_example,
      version: "0.1.0",
      elixir: "~> 1.15",
      elixirc_paths: elixirc_paths(Mix.env()),
      start_permanent: Mix.env() == :prod,
      deps: deps()
    ]
  end

  # Run "mix help compile.app" to learn about applications.
  def application do
    [
      mod: {PostHogExample.Application, []},
      extra_applications: [:logger]
    ]
  end

  defp elixirc_paths(_), do: ["lib"]

  # Run "mix help deps" to learn about dependencies.
  defp deps do
    [
      {:phoenix, "~> 1.7"},
      {:phoenix_html, "~> 4.0"},
      # Phoenix.Component / the ~H sigil used by the HTML views ships in
      # phoenix_live_view, even though this app does not use LiveView itself.
      {:phoenix_live_view, "~> 1.0"},
      {:bandit, "~> 1.5"},
      {:jason, "~> 1.4"},
      # The PostHog server-side SDK. https://posthog.com/docs/libraries/elixir
      {:posthog, "~> 2.0"}
    ]
  end
end

```

---

