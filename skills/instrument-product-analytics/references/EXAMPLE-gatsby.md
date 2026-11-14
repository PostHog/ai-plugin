# PostHog gatsby Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/gatsby

---

## README.md

# PostHog Gatsby example

A minimal [Gatsby](https://www.gatsbyjs.com) 5 site that uses the [PostHog JavaScript SDK](https://posthog.com/docs/libraries/js) (`posthog-js`) to add PostHog analytics, session replay, feature flags and error tracking.

## Features

- **Product analytics**: pageviews, autocapture and a custom `burrito_considered` event
- **Session replay**: recordings start when posthog-js initializes
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

If the token is missing, the site still builds and runs. `gatsby-browser.ts` skips `posthog.init()`, and `gatsby-config.ts` logs a warning outside production.

### 3. Run the site

```bash
pnpm develop   # http://localhost:8000
pnpm build && pnpm serve
```

## Project structure

```
.
├── gatsby-browser.ts       # Initializes posthog-js when the site loads in the browser
├── gatsby-config.ts        # Loads .env and warns when the token is missing
└── src/
    └── pages/
        └── index.tsx       # Demo page: identify, custom event, feature flag, error capture
```

## Key integration points

### SDK setup (gatsby-browser.ts)

```typescript
import posthog from "posthog-js"

export const onClientEntry: GatsbyBrowser["onClientEntry"] = () => {
  const token = process.env.GATSBY_POSTHOG_PROJECT_TOKEN
  if (!token) return

  posthog.init(token, {
    api_host: process.env.GATSBY_POSTHOG_HOST || "https://us.i.posthog.com",
    defaults: "2026-08-30",
    capture_pageview: "history_change",
  })
}
```

`onClientEntry` runs once in the browser, before the first page renders, so PostHog initializes before any page code calls it. Gatsby changes routes with the History API, so `capture_pageview: "history_change"` captures a `$pageview` on the first page load and on each route change. You do not need an `onRouteUpdate` handler. With `defaults` dated `2025-05-24` or later, `capture_pageview` is already `"history_change"`. This example sets it explicitly to make the behavior clear.

Gatsby inlines `GATSBY_`-prefixed environment variables into the browser bundle at build time. `gatsby-config.ts` loads `.env` with `dotenv`, so the token and host are available to `gatsby-browser.ts`. The token ends up in the generated JavaScript, which is expected for a project token.

### Migrating from gatsby-plugin-posthog

The `gatsby-plugin-posthog` plugin is deprecated. To move to `posthog-js`:

1. Remove `gatsby-plugin-posthog` from the `plugins` array in `gatsby-config` and uninstall it.
2. Install `posthog-js` and initialize it in `gatsby-browser` as shown above.
3. Remove any manual `$pageview` captures in `onRouteUpdate`. If you keep them, each route change sends two pageviews.
4. Import `posthog` from `posthog-js` instead of using `window.posthog`.

### Identify, capture and reset (src/pages/index.tsx)

```typescript
import posthog from "posthog-js"

posthog.identify(username, { username })
posthog.capture("user_logged_in")

posthog.capture("burrito_considered", { total_considerations: n })

posthog.reset() // on sign-out
```

Identify once when the user signs in, with your own stable user id (a primary key or UUID, never an email), and call `reset()` on sign-out.

### Feature flags and error capture

```typescript
posthog.isFeatureEnabled("burrito-tip")

posthog.captureException(err)
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

## gatsby-browser.ts

```ts
import type { GatsbyBrowser } from "gatsby"
import posthog from "posthog-js"

export const onClientEntry: GatsbyBrowser["onClientEntry"] = () => {
  const token = process.env.GATSBY_POSTHOG_PROJECT_TOKEN
  // Without a token, posthog-js would initialize with an empty key, so skip it
  if (!token) return

  posthog.init(token, {
    api_host: process.env.GATSBY_POSTHOG_HOST || "https://us.i.posthog.com",
    defaults: "2026-08-30",
    // Gatsby routes with the History API, so capture a $pageview on each route change
    capture_pageview: "history_change",
  })
}

```

---

## gatsby-config.ts

```ts
import type { GatsbyConfig } from "gatsby"
import dotenv from "dotenv"

// Loads .env so GATSBY_-prefixed variables get inlined into the browser bundle
dotenv.config({ quiet: true })

if (!process.env.GATSBY_POSTHOG_PROJECT_TOKEN && process.env.NODE_ENV !== "production") {
  console.warn(
    "GATSBY_POSTHOG_PROJECT_TOKEN variable required by PostHog is missing or un-configured, this causes events to be silently missed. This error stops appearing once GATSBY_POSTHOG_PROJECT_TOKEN is configured"
  )
}

const config: GatsbyConfig = {
  siteMetadata: {
    title: "Burrito consideration app",
  },
}

export default config

```

---

## src/pages/index.tsx

```tsx
import * as React from "react"
import type { HeadFC, PageProps } from "gatsby"
import posthog from "posthog-js"

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

    posthog.identify(getUserId(username), { username })
    posthog.capture("user_logged_in")
    setUser(username)
    setUsername("")
  }

  const handleLogout = () => {
    posthog.reset()
    setUser(null)
    setConsiderations(0)
  }

  const handleConsider = () => {
    posthog.capture("burrito_considered", {
      total_considerations: considerations + 1,
    })
    setConsiderations(considerations + 1)
    setShowTip(posthog.isFeatureEnabled("burrito-tip") === true)
  }

  const handleError = () => {
    try {
      throw new Error("Demo burrito error")
    } catch (err) {
      posthog.captureException(err)
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

