# Framework rules

Follow these when integrating PostHog into this framework.

- A missing PostHog configuration must never break the app — read keys optionally (never a required setting, and never with a format check such as a URL rule in an env schema, which a blank value fails at boot), guard init and capture behind their presence, and keep build and boot working with no PostHog environment set — but never silently: in development or debug builds fail loudly, using the language's idiomatic error, with the message "<VAR> variable required by PostHog is missing or un-configured, this causes events to be silently missed. This error stops appearing once <VAR> is configured" (substituting the actual variable name); production stays a no-op. Only client code, in a browser or on a device, raises it as an error. Server-side code (a server, a worker, a module they load) logs that message as a warning outside production and keeps running, because an error there stops the process from booting for anyone without PostHog keys. A process another program launches, such as an MCP server on STDIO, has nobody watching it boot and no development build — it always writes the warning to stderr (never stdout, which can carry the protocol)
- Sending analytics must never fail or stall the app's own work. Where the app waits on a flush, handle any error it raises and keep the wait short. A long-running server or worker whose SDK sends in the background needs no flush after each capture
- A proxy forwards to the project's own region only: `/static/*` and `/array/*` to the assets host (us-assets.i.posthog.com or eu-assets.i.posthog.com), every other path to the ingestion host (us.i.posthog.com or eu.i.posthog.com). Never mix US and EU hosts
- Whenever `api_host` points at a proxy, set `ui_host` to the PostHog app host (https://us.posthog.com or https://eu.posthog.com). Without it the toolbar and the recordings player break
- A self-hosted proxy sets the `Host` header to the PostHog host it forwards to, forwards the visitor's IP in `X-Forwarded-For`, passes `Authorization`, every `PostHog-*` header, `Content-Type`, `Content-Encoding`, and `User-Agent` unchanged, allows GET and POST, keeps the query string, and accepts request bodies up to 64 MB for session recordings
- Never point `api_host` at a managed proxy before `proxy-get` reports its status as `valid`. Until then every request to it fails
- Create a managed proxy only after the user confirmed the subdomain. A proxy belongs to the whole organization and counts against its limit
- When a reverse proxy is configured, both /static/* AND /array/* must route to the assets origin (us-assets.i.posthog.com or eu-assets.i.posthog.com).
- posthog-js is the JavaScript SDK package name
- posthog.init() MUST be called before any other PostHog methods (capture, identify, etc.)
- posthog-js is browser-only — do NOT import it in Node.js or server-side contexts (use posthog-node instead)
- Autocapture is ON by default with posthog-js (tracks clicks, form submissions, pageviews). Keep autocapture enabled unless the user explicitly asks to turn it off.
- NEVER send PII in posthog.capture() event properties — no emails, full names, phone numbers, physical addresses, IP addresses, or user-generated content
- PII belongs in posthog.identify() person properties (email, name, role), NOT in capture() event properties
- Call posthog.identify(userId, { email, name, role }) on login AND on page refresh if the user is already logged in
- Call posthog.reset() on logout — the transition out of an identified session, never an initially anonymous page load (that discards the anonymous id and its history) — and before identify() when switching directly between accounts
- For SPAs without a framework router, capture pageviews with posthog.capture($pageview) or use the capture_pageview history_change option in init for History API routing
- When verifying with an automated browser (Playwright, Puppeteer, Selenium), posthog-js's bot filter silently drops every capture while flags and asset loads still succeed. Override navigator.webdriver, the user agent, AND navigator.userAgentData before concluding events do not send. Diagnose with ?__posthog_debug=true ("likely bot" in the console).
