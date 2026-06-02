# Elixir Error Tracking installation - Docs

1.  1

    ## Install the Elixir SDK

    Required

    Add the [PostHog Elixir SDK](/docs/libraries/elixir.md) to your list of dependencies in `mix.exs`:

    Elixir

    PostHog AI

    ```elixir
    def deps do
      [
        {:posthog, "~> 2.5"}
      ]
    end
    ```

    Then run:

    Terminal

    PostHog AI

    ```bash
    mix deps.get
    ```

    **Source code context**

    The Elixir SDK supports displaying the surrounding lines of source code in the Error Tracking UI. Since Elixir is a compiled language, source files must be packaged at build time. See the [source context step](#enable-source-code-context-optional) below for setup instructions.

2.  2

    ## Configure PostHog

    Required

    Add your project token and host to your config:

    config/config.exs

    PostHog AI

    ```elixir
    config :posthog,
      api_host: "https://us.i.posthog.com",
      api_key: "<ph_project_token>"
    ```

    To get the most out of Error Tracking, set `in_app_otp_apps` to your application name. This marks stack trace frames from your code as "in-app", making it easier to identify relevant frames in the PostHog UI:

    config/config.exs

    PostHog AI

    ```elixir
    config :posthog,
      api_host: "https://us.i.posthog.com",
      api_key: "<ph_project_token>",
      in_app_otp_apps: [:my_app]
    ```

3.  3

    ## Errors are captured automatically

    Required

    Error Tracking is **enabled by default**. The SDK hooks into Elixir's built-in [`Logger`](https://hexdocs.pm/logger/Logger.html) handler system, so it automatically captures:

    -   **Unhandled exceptions** – crashes in GenServers, Tasks, and other OTP processes
    -   **Logger.error calls** – any `Logger.error/1` message at or above the configured level

    No additional code is needed. Any crash or error log in your application is sent to PostHog as a `$exception` event with full stack traces.

    **What gets captured**

    The handler captures log messages based on two rules:

    1.  **Crash reasons are always captured** – any log with a `crash_reason` metadata (e.g., GenServer/Task crashes) is captured regardless of log level.
    2.  **Log level filtering** – other messages at or above the configured `capture_level` (default: `:error`) are captured.

4.  4

    ## Add Phoenix/Plug integration (recommended)

    Recommended

    If you're using Phoenix or Plug, add the `PostHog.Integrations.Plug` middleware to automatically attach HTTP context (URL, host, path, IP) to error events.

    **For Phoenix**, add it to your `endpoint.ex` before the router:

    lib/my\_app\_web/endpoint.ex

    PostHog AI

    ```elixir
    plug PostHog.Integrations.Plug
    plug MyAppWeb.Router
    ```

    **For Plug apps**, add it to your router:

    Elixir

    PostHog AI

    ```elixir
    defmodule MyRouter do
      use Plug.Router
      plug PostHog.Integrations.Plug
      plug :match
      plug :dispatch
      # ... routes
    end
    ```

    This automatically includes `$current_url`, `$host`, `$pathname`, and `$ip` on every error event that occurs during request processing.

5.  5

    ## Identify users on errors (recommended)

    Recommended

    By default, errors are attributed to `"unknown"`. To associate errors with specific users, set a context with a `distinct_id` early in your request lifecycle – for example, in a Plug pipeline after authentication:

    Elixir

    PostHog AI

    ```elixir
    PostHog.set_context(%{distinct_id: current_user.id})
    ```

    This is process-scoped, so any error that occurs in the same process (i.e., the same request) will include the user's distinct ID.

    For Phoenix apps, a common pattern is to add this in a plug or controller action:

    lib/my\_app\_web/plugs/set\_posthog\_context.ex

    PostHog AI

    ```elixir
    defmodule MyAppWeb.Plugs.SetPostHogContext do
      import Plug.Conn
      def init(opts), do: opts
      def call(conn, _opts) do
        if user = conn.assigns[:current_user] do
          PostHog.set_context(%{distinct_id: user.id})
        end
        conn
      end
    end
    ```

    Then add it to your router pipeline:

    Elixir

    PostHog AI

    ```elixir
    pipeline :browser do
      # ... other plugs
      plug MyAppWeb.Plugs.SetPostHogContext
    end
    ```

6.  6

    ## Configure error tracking options (optional)

    Optional

    The SDK supports several configuration options for Error Tracking:

    config/config.exs

    PostHog AI

    ```elixir
    config :posthog,
      api_host: "https://us.i.posthog.com",
      api_key: "<ph_project_token>",
      # Mark your app's stacktrace frames as "in_app"
      in_app_otp_apps: [:my_app],
      # Minimum log level to capture (default: :error)
      # Set to :warning to also capture warnings, or nil to only capture crashes
      capture_level: :error,
      # Logger metadata keys to include in error events (default: [])
      # Set to :all to include all metadata
      metadata: [:request_id, :user_id]
    ```

    | Option | Type | Default | Description |
    | --- | --- | --- | --- |
    | in_app_otp_apps | list of atoms | [] | OTP app names whose stacktrace frames are marked as "in_app" in the UI. |
    | capture_level | log level or nil | :error | Minimum log level to capture. Crashes with crash_reason are always captured. Set to nil to only capture crashes. |
    | metadata | list of atoms or :all | [] | Logger metadata keys to include as event properties. |
    | enable_error_tracking | boolean | true | Set to false to disable automatic Error Tracking entirely. |
    | global_properties | map | %{} | Properties added to all captured events (not just errors). |

7.  7

    ## Enable source code context (optional)

    Optional

    Since Elixir is a compiled language, source files aren't available at runtime by default. To display the surrounding lines of code in PostHog's Error Tracking UI, you need to package your source code at build time.

    **Step 1:** Enable source context in your config:

    config/config.exs

    PostHog AI

    ```elixir
    config :posthog,
      api_host: "https://us.i.posthog.com",
      api_key: "<ph_project_token>",
      enable_source_code_context: true,
      root_source_code_paths: [File.cwd!()],
      context_lines: 5
    ```

    **Step 2:** Package source code before building your release:

    Terminal

    PostHog AI

    ```bash
    mix posthog.package_source_code
    mix release
    ```

    This reads all `.ex` files from your project, compresses them into `priv/posthog_source.map`, and bundles them with your release. When an error occurs, the SDK matches stack trace frames to the packaged source and includes `pre_context`, `context_line`, and `post_context` in each frame.

    **Development mode**

    In development, if `root_source_code_paths` is set and source files are accessible on disk, the SDK reads them directly at startup – no packaging step needed.

    ### Configuration options

    | Option | Type | Default | Description |
    | --- | --- | --- | --- |
    | enable_source_code_context | boolean | false | Enable source code context in stack frames. |
    | root_source_code_paths | list of strings | [] | Root paths to scan for source files. |
    | source_code_path_pattern | string | "**/*.ex" | Glob pattern for files to include. |
    | source_code_exclude_patterns | list of regexes | [~r"^_build/", ~r"^priv/", ~r"^test/"] | Patterns to exclude. |
    | context_lines | integer | 5 | Number of lines to include before and after the error line. |
    | source_code_map_path | string | nil | Custom path to a packaged source map file. |

    ### Mix task options

    Terminal

    PostHog AI

    ```bash
    # Custom output path
    mix posthog.package_source_code --output path/to/output.map
    # Custom root paths (overrides config)
    mix posthog.package_source_code --root-path /app/lib --root-path /app/src
    ```

8.  ## Verify error tracking

    Recommended

    Trigger a test exception to confirm errors are being sent to PostHog. You should see them appear in the [Error Tracking](https://app.posthog.com/error_tracking) tab.

    Elixir

    PostHog AI

    ```elixir
    # In an IEx session or a test route
    require Logger
    Logger.error("Test error from Elixir")
    ```

    Or raise an exception in a controller or GenServer to test crash capture:

    Elixir

    PostHog AI

    ```elixir
    # In a Phoenix controller
    def test_error(conn, _params) do
      raise "Test exception from Phoenix"
    end
    ```

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better