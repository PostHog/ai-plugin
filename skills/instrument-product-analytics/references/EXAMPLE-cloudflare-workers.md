# PostHog cloudflare-workers Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/cloudflare-workers

---

## README.md

# PostHog Cloudflare Workers example

A [Cloudflare Workers](https://developers.cloudflare.com/workers/) example showing PostHog product analytics, user identification, feature flags, and error tracking with `posthog-node`, using the Workers pattern for short-lived handlers.

## Features

- **Product analytics**: capture a custom event (`burrito_considered`) per request
- **User identification**: identify on login with person properties (`$set`); signed-out visitors get a random id and anonymous events
- **Feature flags**: evaluate a flag with `evaluateFlags()` and fall back to off if PostHog is unreachable
- **Error tracking**: report handled and unhandled errors with `captureExceptionImmediate()`
- **Flush before the Worker ends**: events are sent with `ctx.waitUntil()` so they are not lost after the response

## Getting started

### 1. Install dependencies

```bash
pnpm install
```

To add the SDK to your own Worker:

```bash
pnpm add posthog-node
```

### 2. Configure environment variables

`wrangler.toml` declares `POSTHOG_PROJECT_TOKEN` and `POSTHOG_HOST` under `[vars]`. For local development, copy `.dev.vars.example` to `.dev.vars` and fill in your values:

```bash
cp .dev.vars.example .dev.vars
```

For a deployed Worker, store the token with `wrangler secret put POSTHOG_PROJECT_TOKEN` or set it in `[vars]`. Use `https://eu.i.posthog.com` as `POSTHOG_HOST` for EU Cloud.

A missing token never breaks the Worker. PostHog is skipped, and a warning naming `POSTHOG_PROJECT_TOKEN` is logged unless `ENVIRONMENT` is `production`.

### 3. Run the Worker

```bash
pnpm dev
```

Open [http://localhost:8787](http://localhost:8787). Check the build without deploying:

```bash
pnpm typecheck
pnpm build
```

## Project structure

```
cloudflare-workers/
├── wrangler.toml        # Worker config and non-secret vars
├── .dev.vars.example    # Local environment template
├── tsconfig.json
├── package.json
└── src/
    ├── posthog.ts       # Creates the per-request PostHog client from env bindings
    └── index.ts         # Routes: login, events, flags, error tracking
```

## Key integration points

### Client (src/posthog.ts)

Workers can stop right after the response is sent, so the client sends every event immediately instead of batching. Network timeouts are short and retries are off so PostHog can never stall a request. Create a new client per request.

```ts
return new PostHog(env.POSTHOG_PROJECT_TOKEN, {
  host: env.POSTHOG_HOST || 'https://us.i.posthog.com',
  flushAt: 1,
  flushInterval: 0,
  requestTimeout: 2000,
  fetchRetryCount: 0,
})
```

### Sending events before the Worker ends (src/index.ts)

Start each send without awaiting it, then hand the promises and `shutdown()` to `ctx.waitUntil()`. The response is not delayed and the Worker stays alive until the events are sent.

```ts
track(posthog?.captureImmediate({ distinctId: visitor.id, event: 'burrito_considered' }))

ctx.waitUntil(
  Promise.all(pending).finally(() => posthog?.shutdown().catch(() => {}))
)
```

### User identification (src/index.ts)

Use your app's stable user id as `distinctId`, and send person properties in `$set`. The id must match the one the browser passes to `posthog.identify()`.

```ts
posthog?.captureImmediate({
  distinctId: userId,
  event: 'user_logged_in',
  properties: { login_method: 'email', $set: { email } },
})
```

### Signed-out visitors (src/index.ts)

Visitors without a `user_id` cookie get a random id in an `anon_id` cookie, reused for the visit. Their events set `$process_person_profile` to `false` so PostHog creates no person profile.

```ts
const anonymousProps = visitor.anonymous ? { $process_person_profile: false } : {}
```

### Feature flags (src/index.ts)

Awaiting the flag is the one place the response waits on PostHog, so errors are caught and the flag falls back to off.

```ts
const flags = await posthog?.evaluateFlags(visitor.id)
const showNewFeature = flags?.isEnabled('new-dashboard-feature') ?? false
```

### Error tracking (src/index.ts)

```ts
track(posthog?.captureExceptionImmediate(error, visitor.id, anonymousProps))
```

## Reverse proxy

A Worker sends events from the server, so ad blockers do not affect it and it does not need a reverse proxy. If your Worker serves a browser app that uses `posthog-js`, see [Using Cloudflare as a reverse proxy](https://posthog.com/docs/advanced/proxy/cloudflare.md).

## Learn more

- [PostHog Cloudflare Workers docs](https://posthog.com/docs/libraries/cloudflare-workers.md)
- [PostHog Node.js SDK](https://posthog.com/docs/libraries/node.md)

---

## .dev.vars.example

```example
# Copy to .dev.vars for `wrangler dev`. Values here override [vars] in wrangler.toml.
POSTHOG_PROJECT_TOKEN=phc_your_project_token_here
POSTHOG_HOST=https://us.i.posthog.com

```

---

## src/index.ts

```ts
import { createPostHogClient, type Env } from './posthog'

interface Visitor {
  id: string
  anonymous: boolean
  setCookie?: string
}

const COOKIE_OPTIONS = 'Path=/; HttpOnly; Secure; SameSite=Lax'

function readCookie(request: Request, name: string): string | undefined {
  const cookies = request.headers.get('cookie') ?? ''
  return cookies
    .split(';')
    .map((part) => part.trim().split('='))
    .find(([key]) => key === name)?.[1]
}

// Signed-in users keep the app's own user id in a cookie. Signed-out visitors
// get a random id kept in a cookie for the visit, so they never share an id.
function getVisitor(request: Request): Visitor {
  const userId = readCookie(request, 'user_id')
  if (userId) return { id: decodeURIComponent(userId), anonymous: false }

  const anonId = readCookie(request, 'anon_id')
  if (anonId) return { id: anonId, anonymous: true }

  const id = crypto.randomUUID()
  return { id, anonymous: true, setCookie: `anon_id=${id}; ${COOKIE_OPTIONS}` }
}

function escapeHtml(value: string): string {
  return value.replace(/[&<>"']/g, (char) => `&#${char.charCodeAt(0)};`)
}

function page(title: string, body: string, setCookies: string[] = []): Response {
  const headers = new Headers({ 'content-type': 'text/html; charset=utf-8' })
  for (const cookie of setCookies) headers.append('set-cookie', cookie)
  return new Response(
    `<!doctype html><title>${title}</title><h1>${title}</h1>${body}`,
    { headers }
  )
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const posthog = createPostHogClient(env)
    const visitor = getVisitor(request)
    const url = new URL(request.url)

    // Anonymous events set $process_person_profile to false so PostHog does
    // not create a person profile for the visitor.
    const anonymousProps = visitor.anonymous ? { $process_person_profile: false } : {}

    // Sends started during the request. They are awaited after the response
    // is returned, then the client is shut down.
    const pending: Promise<unknown>[] = []
    const track = (send: Promise<void> | undefined) => {
      if (send) pending.push(send.catch((error) => console.warn('PostHog send failed', error)))
    }

    let response: Response
    try {
      response = await route()
    } catch (error) {
      track(posthog?.captureExceptionImmediate(error, visitor.id, anonymousProps))
      console.error('Unhandled error', error)
      response = new Response('Internal server error', { status: 500 })
    }

    ctx.waitUntil(
      Promise.all(pending).finally(() => posthog?.shutdown().catch(() => {}))
    )

    if (visitor.setCookie && request.method === 'GET') response.headers.append('set-cookie', visitor.setCookie)
    return response

    async function route(): Promise<Response> {
      if (request.method === 'POST' && url.pathname === '/login') {
        const form = await request.formData()
        const userId = String(form.get('user_id') || 'burrito-fan-42')
        const email = String(form.get('email') || '')

        // Identify once, on login. The server-side equivalent of identify() is
        // an event that carries person properties in $set.
        track(
          posthog?.captureImmediate({
            distinctId: userId,
            event: 'user_logged_in',
            properties: { login_method: 'email', $set: { email } },
          })
        )

        return new Response(null, {
          status: 303,
          headers: { location: '/', 'set-cookie': `user_id=${encodeURIComponent(userId)}; ${COOKIE_OPTIONS}` },
        })
      }

      if (request.method === 'POST' && url.pathname === '/logout') {
        return new Response(null, {
          status: 303,
          headers: { location: '/', 'set-cookie': `user_id=; ${COOKIE_OPTIONS}; Max-Age=0` },
        })
      }

      if (url.pathname === '/burrito') {
        const count = Number(readCookie(request, 'burrito_count') ?? 0) + 1

        track(
          posthog?.captureImmediate({
            distinctId: visitor.id,
            event: 'burrito_considered',
            properties: { total_considerations: count, ...anonymousProps },
          })
        )

        return page(
          'Burrito considered',
          `<p>You have considered a burrito <strong>${count}</strong> time(s).</p><p><a href="/">Back home</a></p>`,
          [`burrito_count=${count}; ${COOKIE_OPTIONS}`]
        )
      }

      if (url.pathname === '/dashboard') {
        // Awaiting the flag blocks the response, which is what we want here.
        // A PostHog failure falls back to the flag being off.
        let showNewFeature = false
        try {
          const flags = await posthog?.evaluateFlags(visitor.id)
          showNewFeature = flags?.isEnabled('new-dashboard-feature') ?? false
        } catch (error) {
          console.warn('Feature flag evaluation failed', error)
        }

        return page(
          'Dashboard',
          showNewFeature
            ? '<p>You are seeing the <strong>new</strong> dashboard feature.</p>'
            : '<p>You are seeing the <strong>standard</strong> dashboard.</p>'
        )
      }

      if (url.pathname === '/profile') {
        // A handled failure that is still worth reporting.
        try {
          throw new Error('Profile data is unavailable')
        } catch (error) {
          track(posthog?.captureExceptionImmediate(error, visitor.id, anonymousProps))
        }

        return page('Profile', '<p>Profile data is unavailable. The error was reported.</p>')
      }

      if (url.pathname === '/') {
        const status = visitor.anonymous
          ? 'Not signed in, anonymous visitor'
          : `Signed in as <strong>${escapeHtml(visitor.id)}</strong>`
        const form = visitor.anonymous
          ? `<form method="POST" action="/login">
               <label>User id <input name="user_id" value="burrito-fan-42"></label>
               <label>Email <input name="email" value="fan@example.com"></label>
               <button>Log in</button>
             </form>`
          : '<form method="POST" action="/logout"><button>Log out</button></form>'

        return page(
          'Burrito app',
          `<p>${status}</p>${form}
           <ul>
             <li><a href="/burrito">Consider a burrito</a> (event)</li>
             <li><a href="/dashboard">Dashboard</a> (feature flag)</li>
             <li><a href="/profile">Profile</a> (error tracking)</li>
           </ul>`
        )
      }

      return new Response('Not found', { status: 404 })
    }
  },
} satisfies ExportedHandler<Env>

```

---

## src/posthog.ts

```ts
import { PostHog } from 'posthog-node'

export interface Env {
  POSTHOG_PROJECT_TOKEN?: string
  POSTHOG_HOST?: string
  ENVIRONMENT?: string
}

// Create a new client per request. Workers can be frozen as soon as the
// response is sent, so the client sends every event immediately instead of
// batching, and the caller shuts it down inside ctx.waitUntil().
export function createPostHogClient(env: Env): PostHog | null {
  if (!env.POSTHOG_PROJECT_TOKEN) {
    if (env.ENVIRONMENT !== 'production') {
      console.warn(
        'POSTHOG_PROJECT_TOKEN variable required by PostHog is missing or un-configured, this causes events to be silently missed. This error stops appearing once POSTHOG_PROJECT_TOKEN is configured'
      )
    }
    return null
  }

  return new PostHog(env.POSTHOG_PROJECT_TOKEN, {
    host: env.POSTHOG_HOST || 'https://us.i.posthog.com',
    flushAt: 1,
    flushInterval: 0,
    requestTimeout: 2000,
    fetchRetryCount: 0,
  })
}

```

---

## wrangler.toml

```toml
name = "posthog-cloudflare-workers-example"
main = "src/index.ts"
compatibility_date = "2026-10-01"

[observability]
enabled = true

# Non-secret config. Local overrides go in .dev.vars (see .dev.vars.example).
# Set ENVIRONMENT to "production" in the deployed Worker to silence the
# missing-token warning.
[vars]
POSTHOG_PROJECT_TOKEN = ""
POSTHOG_HOST = "https://us.i.posthog.com"

```

---

