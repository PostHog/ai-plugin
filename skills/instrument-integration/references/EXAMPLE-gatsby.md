# PostHog gatsby Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/gatsby

---

## README.md

# PostHog Gatsby example

A minimal [Gatsby](https://www.gatsbyjs.com) 5 site that uses the community [`gatsby-plugin-posthog`](https://github.com/PostHog/gatsby-plugin-posthog) plugin to add PostHog analytics, session replay, feature flags and error tracking.

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
GATSBY_POSTHOG_PROJECT_TOKEN=phc_your_project_token_here
GATSBY_POSTHOG_HOST=https://us.i.posthog.com
```

Get your project token from your [PostHog project settings](https://app.posthog.com/project/settings). Use `https://eu.i.posthog.com` as the host for an EU Cloud project.

If the token is missing, the site still builds and runs. `gatsby-config.ts` leaves the plugin out and logs a warning outside production.

### 3. Run the site

```bash
pnpm develop   # http://localhost:8000
pnpm build && pnpm serve
```

## Project structure

```
.
├── gatsby-config.ts        # Registers gatsby-plugin-posthog with the token and host from env
└── src/
    ├── pages/
    │   └── index.tsx       # Demo page: identify, custom event, feature flag, error capture
    └── posthog.d.ts        # Types for window.posthog
```

## Key integration points

### Plugin setup (gatsby-config.ts)

```typescript
{
  resolve: "gatsby-plugin-posthog",
  options: {
    apiKey: token,
    apiHost: host,
    isEnabledDevMode: true,
    initOptions: {
      defaults: "2026-08-30",
      capture_pageview: false,
    },
  },
}
```

The plugin injects the posthog-js snippet into the page head and exposes the client as `window.posthog`. It has no `defaults` option of its own, but `initOptions` is passed through to `posthog.init()`, so `defaults` goes there. The plugin captures its own `$pageview` on every route change, including the first page load, so `capture_pageview: false` stops the SDK from sending a second one.

The plugin only loads PostHog in production builds unless `isEnabledDevMode` is `true`. The token is read in `gatsby-config.ts` at build time and ends up in the generated HTML, which is expected for a project token.

### Identify, capture and reset (src/pages/index.tsx)

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

The site is static, so there is no server code to host a proxy. To keep events from being blocked, use PostHog's [managed reverse proxy](https://posthog.com/docs/advanced/proxy/managed-reverse-proxy.md), then set `GATSBY_POSTHOG_HOST` to your proxy domain.

## Learn more

- [PostHog Gatsby docs](https://posthog.com/docs/libraries/gatsby)
- [Gatsby docs](https://www.gatsbyjs.com/docs)

---

## .env.example

```example
# Get your PostHog project token from: https://app.posthog.com/project/settings
GATSBY_POSTHOG_PROJECT_TOKEN=phc_your_project_token_here
# Ingestion host: https://us.i.posthog.com or https://eu.i.posthog.com
GATSBY_POSTHOG_HOST=https://us.i.posthog.com

```

---

## gatsby-config.ts

```ts
import type { GatsbyConfig } from "gatsby"
import dotenv from "dotenv"

dotenv.config({ quiet: true })

const token = process.env.GATSBY_POSTHOG_PROJECT_TOKEN
const host = process.env.GATSBY_POSTHOG_HOST || "https://us.i.posthog.com"

if (!token && process.env.NODE_ENV !== "production") {
  console.warn(
    "GATSBY_POSTHOG_PROJECT_TOKEN variable required by PostHog is missing or un-configured, this causes events to be silently missed. This error stops appearing once GATSBY_POSTHOG_PROJECT_TOKEN is configured"
  )
}

const config: GatsbyConfig = {
  siteMetadata: {
    title: "Burrito consideration app",
  },
  plugins: [
    // Without a token the plugin would initialize PostHog with an empty key, so leave it out
    ...(token
      ? [
          {
            resolve: "gatsby-plugin-posthog",
            options: {
              apiKey: token,
              apiHost: host,
              // Load PostHog during `gatsby develop` too
              isEnabledDevMode: true,
              // Passed through to posthog.init()
              initOptions: {
                defaults: "2026-08-30",
                // The plugin captures a $pageview on every route change, including the first
                capture_pageview: false,
              },
            },
          },
        ]
      : []),
  ],
}

export default config

```

---

## src/pages/index.tsx

```tsx
import * as React from "react"
import type { HeadFC, PageProps } from "gatsby"

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

const IndexPage: React.FC<PageProps> = () => {
  const [username, setUsername] = React.useState("")
  const [user, setUser] = React.useState<string | null>(null)
  const [considerations, setConsiderations] = React.useState(0)
  const [showTip, setShowTip] = React.useState(false)

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

  if (!user) {
    return (
      <main>
        <h1>Burrito consideration app</h1>
        <form onSubmit={handleLogin}>
          <label htmlFor="username">Username</label>{" "}
          <input
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />{" "}
          <button type="submit">Sign in</button>
        </form>
      </main>
    )
  }

  return (
    <main>
      <h1>Welcome, {user}</h1>
      <p>Burritos considered: {considerations}</p>
      {showTip && <p>Tip: consider the beans.</p>}
      <button onClick={handleConsider}>Consider a burrito</button>{" "}
      <button onClick={handleError}>Trigger a test error</button>{" "}
      <button onClick={handleLogout}>Sign out</button>
    </main>
  )
}

export default IndexPage

export const Head: HeadFC = () => <title>Burrito consideration app</title>

```

---

## src/posthog.d.ts

```ts
// The Gatsby plugin loads posthog-js with a script snippet and exposes it as window.posthog
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

