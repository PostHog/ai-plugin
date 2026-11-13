# PostHog hono Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/hono

---

## README.md

# PostHog Hono example

A small Hono API ("burrito app") running on Node.js that shows how to integrate PostHog with `posthog-node` in a server application.

## Features

- **Middleware**: runs each request inside `posthog.withContext`, so captures carry the visitor
- **One client per process**: created once in `src/posthog.ts` and flushed on shutdown
- **User identification**: `POST /login` identifies the user once with their own id
- **Signed-out visitors**: a random id kept in a cookie for the visit, with `$process_person_profile: false`
- **Event capture**: `POST /burrito` sends `burrito_considered`
- **Feature flags**: `GET /dashboard` evaluates `new-dashboard-feature`
- **Error tracking**: `app.onError` captures exceptions (`GET /profile` throws one)

## Getting started

### 1. Install dependencies

```bash
pnpm install
```

### 2. Configure PostHog

```bash
cp .env.example .env
```

Set `POSTHOG_PROJECT_TOKEN` to your project token. Set `POSTHOG_HOST` to `https://eu.i.posthog.com` for an EU project. If the token is missing the app still boots, logs a warning outside production, and sends nothing.

### 3. Run the app

```bash
pnpm dev
```

### 4. Try it out

```bash
curl -c jar -b jar -X POST localhost:3000/burrito
curl -c jar -b jar -X POST -H 'content-type: application/json' -d '{"username":"ada"}' localhost:3000/login
curl -c jar -b jar -X POST localhost:3000/burrito
curl -c jar -b jar localhost:3000/dashboard
curl -c jar -b jar localhost:3000/profile
```

## Project structure

```text
src/
├── index.ts       # Routes, error handler, server and shutdown
├── auth.ts        # Cookie sessions and in-memory users
└── posthog.ts     # The PostHog client and the request context middleware
```

## Key integration points

### Client and middleware

```typescript
export const posthog = new PostHog(token ?? '', {
  host: process.env.POSTHOG_HOST || 'https://us.i.posthog.com',
  enableExceptionAutocapture: true,
  disabled: !token,
})

export const posthogMiddleware = createMiddleware(async (c, next) => {
  // distinctId is the signed-in user's id, or a random visit id with
  // $process_person_profile: false for signed-out visitors.
  return posthog.withContext({ distinctId, properties }, next, { fresh: true })
})
```

Register the auth middleware first so `user` is set before PostHog reads it. The server flushes the client once on shutdown with `posthog.shutdown(3000)`, so there is no flush per request.

### Capturing inside a request

```typescript
// The distinct id and request properties come from the context.
posthog.capture({ event: 'burrito_considered' })

const flags = await posthog.evaluateFlags()
flags.isEnabled('new-dashboard-feature')
```

### Error tracking

```typescript
app.onError((err, c) => {
  posthog.captureException(err, undefined, { $request_path: c.req.path })
  return c.json({ error: 'Internal server error' }, 500)
})
```

## Reverse proxy

This is a server-only app, so it does not need a reverse proxy. A proxy only helps browser code avoid ad blockers.

## Learn more

- [PostHog Hono docs](https://posthog.com/docs/libraries/hono)
- [PostHog Node.js SDK docs](https://posthog.com/docs/libraries/node)

---

## .env.example

```example
# PostHog configuration
POSTHOG_PROJECT_TOKEN=phc_your_project_token_here
POSTHOG_HOST=https://us.i.posthog.com

```

---

## src/auth.ts

```ts
import type { Context } from 'hono'
import { deleteCookie, getCookie, setCookie } from 'hono/cookie'
import { createMiddleware } from 'hono/factory'
import { randomUUID } from 'node:crypto'

export interface User {
  id: string
  username: string
}

// In-memory users and sessions stand in for a real database and session store.
const users = new Map<string, User>()
const sessions = new Map<string, User>()

export const authMiddleware = createMiddleware<{ Variables: { user?: User } }>(async (c, next) => {
  const sessionId = getCookie(c, 'session')
  const user = sessionId ? sessions.get(sessionId) : undefined
  if (user) c.set('user', user)
  await next()
})

export function login(c: Context, username: string): User {
  let user = users.get(username)
  if (!user) {
    user = { id: randomUUID(), username }
    users.set(username, user)
  }
  const sessionId = randomUUID()
  sessions.set(sessionId, user)
  setCookie(c, 'session', sessionId, { httpOnly: true, sameSite: 'Lax', path: '/' })
  return user
}

export function logout(c: Context): void {
  const sessionId = getCookie(c, 'session')
  if (sessionId) sessions.delete(sessionId)
  deleteCookie(c, 'session', { path: '/' })
}

```

---

## src/index.ts

```ts
import { serve } from '@hono/node-server'
import { Hono } from 'hono'
import { authMiddleware, login, logout, type User } from './auth.js'
import { posthog, posthogMiddleware } from './posthog.js'

const app = new Hono<{ Variables: { user?: User } }>()

// Order matters: auth sets `user` before PostHog reads it.
app.use('*', authMiddleware)
app.use('*', posthogMiddleware)

app.get('/', (c) =>
  c.json({
    message: 'Burrito API. POST /login, POST /burrito, GET /dashboard, GET /profile',
    user: c.get('user') ?? null,
  }),
)

// User identification: identify once, on login, with the app's own user id.
app.post('/login', async (c) => {
  const body = await c.req.json<{ username?: string }>().catch(() => ({}) as { username?: string })
  const username = body.username?.trim()
  if (!username) {
    return c.json({ error: 'username is required' }, 400)
  }

  const user = login(c, username)

  posthog.identify({
    distinctId: user.id,
    properties: { username: user.username },
  })

  return c.json({ user })
})

app.post('/logout', (c) => {
  logout(c)
  return c.body(null, 204)
})

// Custom event. The distinct id comes from the request context.
app.post('/burrito', (c) => {
  posthog.capture({ event: 'burrito_considered', properties: { source: 'api' } })

  return c.json({ considered: true })
})

// Feature flag.
app.get('/dashboard', async (c) => {
  const flags = await posthog.evaluateFlags()

  return c.json({ newDashboard: flags.isEnabled('new-dashboard-feature') })
})

// Error tracking: onError captures this.
app.get('/profile', () => {
  throw new Error('Profile lookup failed')
})

app.onError((err, c) => {
  posthog.captureException(err, undefined, {
    $request_path: c.req.path,
    $request_method: c.req.method,
  })

  return c.json({ error: 'Internal server error' }, 500)
})

const server = serve({ fetch: app.fetch, port: Number(process.env.PORT ?? 3000) }, (info) => {
  console.log(`Listening on http://localhost:${info.port}`)
})

// Stop accepting requests, then flush queued PostHog events.
for (const signal of ['SIGINT', 'SIGTERM'] as const) {
  process.once(signal, () => {
    server.close(async () => {
      await posthog.shutdown(3000)
      process.exit(0)
    })
  })
}

```

---

## src/posthog.ts

```ts
import { getCookie, setCookie } from 'hono/cookie'
import { createMiddleware } from 'hono/factory'
import { randomUUID } from 'node:crypto'
import { PostHog } from 'posthog-node'
import type { User } from './auth.js'

const token = process.env.POSTHOG_PROJECT_TOKEN

if (!token && process.env.NODE_ENV !== 'production') {
  console.warn(
    'POSTHOG_PROJECT_TOKEN variable required by PostHog is missing or un-configured, this causes events to be silently missed. This error stops appearing once POSTHOG_PROJECT_TOKEN is configured',
  )
}

// One client per process. Without a token it is disabled and capture calls are no-ops.
export const posthog = new PostHog(token ?? '', {
  host: process.env.POSTHOG_HOST || 'https://us.i.posthog.com',
  enableExceptionAutocapture: true,
  disabled: !token,
})

// Everything captured while handling a request carries the visitor's identity.
// Register this after the middleware that sets `user`.
export const posthogMiddleware = createMiddleware<{ Variables: { user?: User } }>(async (c, next) => {
  const user = c.get('user')
  let distinctId = user?.id
  let properties: Record<string, unknown> = {
    $request_method: c.req.method,
    $request_path: c.req.path,
  }

  if (!distinctId) {
    // Signed-out visitors get a random id for the visit and no person profile.
    distinctId = getCookie(c, 'visit_id')
    if (!distinctId) {
      distinctId = randomUUID()
      setCookie(c, 'visit_id', distinctId, { httpOnly: true, sameSite: 'Lax', path: '/' })
    }
    properties = { ...properties, $process_person_profile: false }
  }

  return posthog.withContext({ distinctId, properties }, next, { fresh: true })
})

```

---

