# PostHog fastify Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/fastify

---

## README.md

# PostHog Fastify example

A small Fastify 5 API ("burrito app") that shows how to integrate PostHog with `posthog-node` in a server application.

## Features

- **Plugin**: one PostHog client per process, decorated onto the app as `app.posthog`
- **Request context**: an `onRequest` hook runs each request inside `posthog.withContext`, so captures carry the visitor
- **Graceful shutdown**: an `onClose` hook flushes queued events when the app closes
- **User identification**: `POST /login` identifies the user once with their own id
- **Signed-out visitors**: a random id kept in a cookie for the visit, with `$process_person_profile: false`
- **Event capture**: `POST /burrito` sends `burrito_considered`
- **Feature flags**: `GET /dashboard` evaluates `new-dashboard-feature`
- **Error tracking**: `setErrorHandler` captures 5xx errors (`GET /profile` throws one)

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
├── server.ts            # Registers plugins and routes, closes the app on SIGINT/SIGTERM
├── routes.ts            # Routes: login, burrito, dashboard, profile
└── plugins/
    ├── auth.ts          # Cookies, in-memory users and sessions, request.user
    └── posthog.ts       # Client, request context hook, error handler, shutdown
```

## Key integration points

### Plugin with request context

```typescript
const posthog = new PostHog(token ?? '', {
  host: process.env.POSTHOG_HOST || 'https://us.i.posthog.com',
  enableExceptionAutocapture: true,
  disabled: !token,
})

app.decorate('posthog', posthog)

// Keep this hook callback-based: done() inside withContext continues the request in that context.
app.addHook('onRequest', (request, reply, done) => {
  posthog.withContext({ distinctId, properties }, done, { fresh: true })
})
```

Register the auth plugin first so `request.user` is set before this hook reads it.

### Errors and shutdown

```typescript
app.setErrorHandler((error, request, reply) => {
  if (statusCode >= 500) {
    posthog.captureException(error, undefined, { $response_status_code: statusCode })
  }
  reply.code(statusCode).send({ error: 'Internal server error' })
})

app.addHook('onClose', async () => {
  await posthog.shutdown(3000)
})
```

### Capturing inside a request

```typescript
// The distinct id and request properties come from the context.
app.posthog.capture({ event: 'burrito_considered' })

const flags = await app.posthog.evaluateFlags()
flags.isEnabled('new-dashboard-feature')
```

## Reverse proxy

This is a server-only app, so it does not need a reverse proxy. A proxy only helps browser code avoid ad blockers.

## Learn more

- [PostHog Fastify docs](https://posthog.com/docs/libraries/fastify)
- [PostHog Node.js SDK docs](https://posthog.com/docs/libraries/node)

---

## .env.example

```example
# PostHog configuration
POSTHOG_PROJECT_TOKEN=phc_your_project_token_here
POSTHOG_HOST=https://us.i.posthog.com

```

---

## src/plugins/auth.ts

```ts
import cookie from '@fastify/cookie'
import { randomUUID } from 'node:crypto'
import fp from 'fastify-plugin'

export interface User {
  id: string
  username: string
}

declare module 'fastify' {
  interface FastifyRequest {
    user?: User
  }
  interface FastifyInstance {
    auth: {
      login(username: string): { user: User; sessionId: string }
      logout(sessionId: string | undefined): void
    }
  }
}

// In-memory users and sessions stand in for a real database and session store.
export default fp(async (app) => {
  const users = new Map<string, User>()
  const sessions = new Map<string, User>()

  await app.register(cookie)

  app.decorate('auth', {
    login(username: string) {
      let user = users.get(username)
      if (!user) {
        user = { id: randomUUID(), username }
        users.set(username, user)
      }
      const sessionId = randomUUID()
      sessions.set(sessionId, user)
      return { user, sessionId }
    },
    logout(sessionId: string | undefined) {
      if (sessionId) sessions.delete(sessionId)
    },
  })

  // Populates request.user from the session cookie. PostHog's hook runs after this one.
  app.addHook('onRequest', (request, _reply, done) => {
    const sessionId = request.cookies.session
    request.user = sessionId ? sessions.get(sessionId) : undefined
    done()
  })
})

```

---

## src/plugins/posthog.ts

```ts
import { randomUUID } from 'node:crypto'
import fp from 'fastify-plugin'
import { PostHog } from 'posthog-node'

declare module 'fastify' {
  interface FastifyInstance {
    posthog: PostHog
  }
}

export default fp(async (app) => {
  const token = process.env.POSTHOG_PROJECT_TOKEN

  if (!token && process.env.NODE_ENV !== 'production') {
    app.log.warn(
      'POSTHOG_PROJECT_TOKEN variable required by PostHog is missing or un-configured, this causes events to be silently missed. This error stops appearing once POSTHOG_PROJECT_TOKEN is configured',
    )
  }

  // One client per process. Without a token it is disabled and capture calls are no-ops.
  const posthog = new PostHog(token ?? '', {
    host: process.env.POSTHOG_HOST || 'https://us.i.posthog.com',
    enableExceptionAutocapture: true,
    disabled: !token,
  })

  app.decorate('posthog', posthog)

  // Everything captured while handling a request carries the visitor's identity.
  // Keep this hook callback-based: calling done() inside withContext continues
  // the request in that context.
  app.addHook('onRequest', (request, reply, done) => {
    let distinctId = request.user?.id
    let properties: Record<string, unknown> = {
      $request_method: request.method,
      request_id: request.id,
    }

    if (!distinctId) {
      // Signed-out visitors get a random id for the visit and no person profile.
      distinctId = request.cookies.visit_id
      if (!distinctId) {
        distinctId = randomUUID()
        reply.setCookie('visit_id', distinctId, { httpOnly: true, sameSite: 'lax', path: '/' })
      }
      properties = { ...properties, $process_person_profile: false }
    }

    posthog.withContext({ distinctId, properties }, done, { fresh: true })
  })

  // Fastify handles route errors itself, so exception autocapture never sees them.
  app.setErrorHandler((error: Error & { status?: number; statusCode?: number }, request, reply) => {
    const statusCode = error.status ?? error.statusCode ?? (reply.statusCode >= 400 ? reply.statusCode : 500)

    if (statusCode >= 500) {
      posthog.captureException(error, undefined, {
        $response_status_code: statusCode,
        $request_path: request.routeOptions.url,
      })
    }

    reply.code(statusCode).send({ error: statusCode >= 500 ? 'Internal server error' : error.message })
  })

  // app.close() runs this and waits for buffered events to be sent.
  app.addHook('onClose', async () => {
    await posthog.shutdown(3000)
  })
})

```

---

## src/routes.ts

```ts
import type { FastifyPluginAsync } from 'fastify'

const routes: FastifyPluginAsync = async (app) => {
  app.get('/', async (request) => ({
    message: 'Burrito API. POST /login, POST /burrito, GET /dashboard, GET /profile',
    user: request.user ?? null,
  }))

  // User identification: identify once, on login, with the app's own user id.
  app.post<{ Body: { username?: string } }>(
    '/login',
    { config: { rateLimit: { max: 10, timeWindow: '1 minute' } } },
    async (request, reply) => {
      const username = request.body?.username?.trim()
      if (!username) {
        return reply.code(400).send({ error: 'username is required' })
      }

      const { user, sessionId } = app.auth.login(username)
      reply.setCookie('session', sessionId, { httpOnly: true, sameSite: 'lax', path: '/' })

      app.posthog.identify({
        distinctId: user.id,
        properties: { username: user.username },
      })

      return { user }
    }
  )

  app.post('/logout', async (request, reply) => {
    app.auth.logout(request.cookies.session)
    return reply.clearCookie('session', { path: '/' }).code(204).send()
  })

  // Custom event. The distinct id comes from the request context.
  app.post('/burrito', async () => {
    app.posthog.capture({ event: 'burrito_considered', properties: { source: 'api' } })

    return { considered: true }
  })

  // Feature flag.
  app.get('/dashboard', async () => {
    const flags = await app.posthog.evaluateFlags()

    return { newDashboard: flags.isEnabled('new-dashboard-feature') }
  })

  // Error tracking: the error handler in plugins/posthog.ts captures this.
  app.get('/profile', async () => {
    throw new Error('Profile lookup failed')
  })
}

export default routes

```

---

## src/server.ts

```ts
import Fastify from 'fastify'
import rateLimit from '@fastify/rate-limit'
import auth from './plugins/auth.js'
import posthog from './plugins/posthog.js'
import routes from './routes.js'

const app = Fastify({ logger: true })

// Order matters: auth sets request.user before PostHog reads it, and both
// register before the routes.
// Rate limits apply only to routes that opt in through their config, such as /login.
await app.register(rateLimit, { global: false })
await app.register(auth)
await app.register(posthog)
await app.register(routes)

// Closing the app runs the onClose hook, which flushes PostHog.
for (const signal of ['SIGINT', 'SIGTERM'] as const) {
  process.once(signal, () => {
    app.close().then(() => process.exit(0))
  })
}

await app.listen({ port: Number(process.env.PORT ?? 3000), host: '0.0.0.0' })

```

---

