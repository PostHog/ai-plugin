# PostHog docusaurus Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/docusaurus

---

## README.md

# PostHog Docusaurus example

A minimal [Docusaurus](https://docusaurus.io) 3 site that uses the [`posthog-docusaurus`](https://github.com/PostHog/posthog-docusaurus) plugin to add PostHog analytics, session replay, feature flags and error tracking.

## Features

- **Product analytics**: pageviews, autocapture and a custom `burrito_considered` event
- **Session replay**: recordings start with the plugin's posthog-js snippet
- **Feature flags**: `isFeatureEnabled()` gates a tip in the demo page
- **Error tracking**: `captureException()` from a try/catch
- **User identification**: a demo sign-in that calls `identify()`, and a sign-out that calls `reset()`

## Getting started

### 1. Install dependencies

```bash
pnpm install
# or
npm install
```

### 2. Configure environment variables

Copy `.env.example` to `.env`:

```bash
POSTHOG_PROJECT_TOKEN=phc_your_project_token_here
POSTHOG_HOST=https://us.i.posthog.com
```

Get your project token from your [PostHog project settings](https://app.posthog.com/project/settings). Use `https://eu.i.posthog.com` as the host for an EU Cloud project.

If the token is missing, the site still builds and runs. `docusaurus.config.ts` leaves the plugin out and logs a warning outside production.

### 3. Run the site

```bash
pnpm start   # http://localhost:3000
pnpm build && pnpm serve
```

## Project structure

```
.
├── docusaurus.config.ts    # Registers posthog-docusaurus with the token and host from env
├── sidebars.ts
├── docs/
│   └── intro.md
└── src/
    ├── pages/
    │   └── burrito.tsx     # Demo page: identify, custom event, feature flag, error capture
    └── posthog.d.ts        # Types for window.posthog
```

## Key integration points

### Plugin setup (docusaurus.config.ts)

```typescript
[
  "posthog-docusaurus",
  {
    apiKey: token,
    appUrl: host,
    enableInDevelopment: true,
    defaults: "2026-08-30",
    capture_pageview: false,
  },
]
```

The plugin injects the posthog-js snippet into the page head and exposes the client as `window.posthog`. Any option besides `apiKey`, `appUrl` and `enableInDevelopment` is passed through to `posthog.init()`, so `defaults` goes there. Options go through `JSON.stringify()`, so functions such as `before_send` are not supported. The plugin captures its own `$pageview` on every route change, including the first page load, so `capture_pageview: false` stops the SDK from sending a second one.

The plugin throws when `apiKey` is empty, which is why the config only registers it when a token is set. It only loads PostHog in production builds unless `enableInDevelopment` is `true`. The token is read at build time and ends up in the generated HTML, which is expected for a project token.

### Identify, capture and reset (src/pages/burrito.tsx)

```typescript
window.posthog?.identify(username, { username })
window.posthog?.capture("user_logged_in")

window.posthog?.capture("burrito_considered", { total_considerations: n })

window.posthog?.reset() // on sign-out
```

Identify once when the user signs in, with your own stable user id (a primary key or UUID, never an email), and call `reset()` on sign-out.

### Feature flags and error capture

```typescript
window.posthog?.isFeatureEnabled("burrito-tip")

window.posthog?.captureException(err)
```

## Reverse proxy

The site is static, so there is no server code to host a proxy. To keep events from being blocked, use PostHog's [managed reverse proxy](https://posthog.com/docs/advanced/proxy/managed-reverse-proxy.md), then set `POSTHOG_HOST` to your proxy domain.

## Learn more

- [PostHog Docusaurus docs](https://posthog.com/docs/libraries/docusaurus)
- [Docusaurus docs](https://docusaurus.io/docs)

---

## .env.example

```example
# Get your PostHog project token from: https://app.posthog.com/project/settings
POSTHOG_PROJECT_TOKEN=phc_your_project_token_here
# Ingestion host: https://us.i.posthog.com or https://eu.i.posthog.com
POSTHOG_HOST=https://us.i.posthog.com

```

---

## docs/intro.md

---
slug: /
---

# Burrito docs

A small Docusaurus site tracked by PostHog. Every page view is captured, along with clicks and session replays.

Try the [burrito demo](/burrito) for identify, custom events, feature flags and error capture.

---

## docusaurus.config.ts

```ts
import dotenv from "dotenv"
import type { Config } from "@docusaurus/types"
import type * as Preset from "@docusaurus/preset-classic"

dotenv.config({ quiet: true })

const token = process.env.POSTHOG_PROJECT_TOKEN
const host = process.env.POSTHOG_HOST || "https://us.i.posthog.com"

if (!token && process.env.NODE_ENV !== "production") {
  console.warn(
    "POSTHOG_PROJECT_TOKEN variable required by PostHog is missing or un-configured, this causes events to be silently missed. This error stops appearing once POSTHOG_PROJECT_TOKEN is configured"
  )
}

const config: Config = {
  title: "Burrito docs",
  url: "https://example.com",
  baseUrl: "/",
  onBrokenLinks: "throw",

  presets: [
    [
      "classic",
      {
        docs: { routeBasePath: "/", sidebarPath: "./sidebars.ts" },
        blog: false,
      } satisfies Preset.Options,
    ],
  ],

  plugins: [
    // The plugin throws without an apiKey, so only register it when a token is set
    ...(token
      ? [
          [
            "posthog-docusaurus",
            {
              apiKey: token,
              appUrl: host,
              // Load PostHog during `docusaurus start` too
              enableInDevelopment: true,
              // Extra options are passed through to posthog.init()
              defaults: "2026-08-30",
              // The plugin captures a $pageview on every route change, including the first
              capture_pageview: false,
            },
          ] as [string, Record<string, unknown>],
        ]
      : []),
  ],

  themeConfig: {
    navbar: {
      title: "Burrito docs",
      items: [{ to: "/burrito", label: "Burrito demo", position: "left" }],
    },
  } satisfies Preset.ThemeConfig,
}

export default config

```

---

## sidebars.ts

```ts
import type { SidebarsConfig } from "@docusaurus/plugin-content-docs"

const sidebars: SidebarsConfig = {
  docs: [{ type: "autogenerated", dirName: "." }],
}

export default sidebars

```

---

## src/pages/burrito.tsx

```tsx
import React, { useState } from "react"
import Layout from "@theme/Layout"

// Stands in for your auth system: each username gets a stable user id, the way a user
// record's primary key would. Identify with that id, never with the username or email.
function getUserId(username: string): string {
  const key = `demo-user-id:${username}`
  const existing = window.localStorage.getItem(key)
  if (existing) return existing
  const id = crypto.randomUUID()
  window.localStorage.setItem(key, id)
  return id
}

export default function Burrito(): React.JSX.Element {
  const [username, setUsername] = useState("")
  const [user, setUser] = useState<string | null>(null)
  const [considerations, setConsiderations] = useState(0)
  const [showTip, setShowTip] = useState(false)

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault()
    if (!username) return

    window.posthog?.identify(getUserId(username), { username })
    window.posthog?.capture("user_logged_in")
    setUser(username)
    setUsername("")
  }

  const handleLogout = () => {
    window.posthog?.reset()
    setUser(null)
    setConsiderations(0)
  }

  const handleConsider = () => {
    window.posthog?.capture("burrito_considered", {
      total_considerations: considerations + 1,
    })
    setConsiderations(considerations + 1)
    setShowTip(window.posthog?.isFeatureEnabled("burrito-tip") === true)
  }

  const handleError = () => {
    try {
      throw new Error("Demo burrito error")
    } catch (err) {
      window.posthog?.captureException(err)
    }
  }

  return (
    <Layout title="Burrito demo">
      <main className="container margin-vert--lg">
        {user ? (
          <>
            <h1>Welcome, {user}</h1>
            <p>Burritos considered: {considerations}</p>
            {showTip && <p>Tip: consider the beans.</p>}
            <button className="button button--primary margin-right--sm" onClick={handleConsider}>
              Consider a burrito
            </button>
            <button className="button button--secondary margin-right--sm" onClick={handleError}>
              Trigger a test error
            </button>
            <button className="button button--link" onClick={handleLogout}>
              Sign out
            </button>
          </>
        ) : (
          <>
            <h1>Burrito demo</h1>
            <form onSubmit={handleLogin}>
              <label htmlFor="username">Username</label>{" "}
              <input id="username" value={username} onChange={(e) => setUsername(e.target.value)} />{" "}
              <button className="button button--primary" type="submit">
                Sign in
              </button>
            </form>
          </>
        )}
      </main>
    </Layout>
  )
}

```

---

## src/posthog.d.ts

```ts
// posthog-docusaurus loads posthog-js with a script snippet and exposes it as window.posthog
interface PostHogSnippet {
  identify(distinctId: string, personProperties?: Record<string, unknown>): void
  capture(event: string, properties?: Record<string, unknown>): void
  captureException(error: unknown): void
  isFeatureEnabled(key: string): boolean | undefined
  reset(): void
}

interface Window {
  posthog?: PostHogSnippet
}

```

---

