# PostHog nestjs Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/nestjs

---

## README.md

# PostHog NestJS example

A small NestJS API ("burrito app") that shows how to integrate PostHog with `posthog-node` in a server application.

## Features

- **Client module**: a global `PostHogModule` and an injectable `PostHogService` own the single client for the process
- **Graceful shutdown**: `onApplicationShutdown` flushes queued events when the app stops
- **User identification**: `POST /login` identifies the user once with their own id
- **Signed-out visitors**: a random id kept in a cookie for the visit, with `$process_person_profile: false`
- **Event capture**: `POST /burrito` sends `burrito_considered`
- **Feature flags**: `GET /dashboard` evaluates `new-dashboard-feature`
- **Error tracking**: `PostHogInterceptor` captures unhandled 5xx errors (`GET /profile` throws one)

## Getting started

The interceptor's `getDistinctId` option needs `posthog-node` 5.68.0 or later.

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
├── main.ts                  # Bootstrap, cookie parser, shutdown hooks
├── app.module.ts            # Root module, applies the visitor middleware
├── app.controller.ts        # Routes: login, burrito, dashboard, profile
├── auth.service.ts          # In-memory users and sessions
├── visitor.middleware.ts    # Resolves the user or a signed-out visit id
└── posthog/
    ├── posthog.module.ts    # Global module and interceptor
    └── posthog.service.ts   # The PostHog client and its shutdown
```

## Key integration points

### Client service with shutdown

```typescript
@Injectable()
export class PostHogService implements OnApplicationShutdown {
  readonly client = new PostHog(token ?? '', {
    host: process.env.POSTHOG_HOST || 'https://us.i.posthog.com',
    enableExceptionAutocapture: true,
    disabled: !token,
  })

  async onApplicationShutdown() {
    await this.client.shutdown(3000)
  }
}
```

`main.ts` calls `app.enableShutdownHooks()` so the hook runs on SIGINT and SIGTERM.

### Interceptor for request context and errors

```typescript
{
  provide: APP_INTERCEPTOR,
  inject: [PostHogService],
  useFactory: (posthog: PostHogService) =>
    new PostHogInterceptor(posthog.client, {
      captureExceptions: true,
      getDistinctId: (request: VisitorRequest) => request.visitor?.user?.id,
    }),
}
```

`getDistinctId` tells the interceptor who the signed-in user is, so its context and the exceptions it captures carry that user even when the client doesn't run posthog-js. It wins over the `X-POSTHOG-DISTINCT-ID` tracing header. Signed-out requests return `undefined` and get a personless id.

### Identity belongs to the request

```typescript
this.posthog.client.identify({ distinctId: user.id, properties: { username: user.username } })

this.posthog.client.capture({
  distinctId: req.visitor.distinctId,
  event: 'burrito_considered',
  properties: req.visitor.properties, // { $process_person_profile: false } when signed out
})
```

### Feature flags

```typescript
const flags = await this.posthog.client.evaluateFlags(req.visitor.distinctId)
flags.isEnabled('new-dashboard-feature')
```

## Reverse proxy

This is a server-only app, so it does not need a reverse proxy. A proxy only helps browser code avoid ad blockers.

## Learn more

- [PostHog NestJS docs](https://posthog.com/docs/libraries/nestjs)
- [PostHog Node.js SDK docs](https://posthog.com/docs/libraries/node)

---

## .env.example

```example
# PostHog configuration
POSTHOG_PROJECT_TOKEN=phc_your_project_token_here
POSTHOG_HOST=https://us.i.posthog.com

```

---

## src/app.controller.ts

```ts
import { Body, Controller, Get, HttpCode, Inject, Post, Req, Res } from '@nestjs/common'
import type { Response } from 'express'
import { AuthService } from './auth.service.js'
import { PostHogService } from './posthog/posthog.service.js'
import type { VisitorRequest } from './visitor.middleware.js'

@Controller()
export class AppController {
  constructor(
    @Inject(PostHogService) private readonly posthog: PostHogService,
    @Inject(AuthService) private readonly auth: AuthService,
  ) {}

  @Get()
  home(@Req() req: VisitorRequest) {
    return {
      message: 'Burrito API. POST /login, POST /burrito, GET /dashboard, GET /profile',
      user: req.visitor.user ?? null,
    }
  }

  // User identification: identify once, on login, with the app's own user id.
  @Post('login')
  @HttpCode(200)
  login(
    @Body() body: { username?: string },
    @Res({ passthrough: true }) res: Response,
  ) {
    const username = body?.username?.trim()
    if (!username) {
      res.status(400)
      return { error: 'username is required' }
    }

    const { user, sessionId } = this.auth.login(username)
    res.cookie('session', sessionId, { httpOnly: true, sameSite: 'lax' })

    this.posthog.client.identify({
      distinctId: user.id,
      properties: { username: user.username },
    })

    return { user }
  }

  @Post('logout')
  @HttpCode(204)
  logout(@Req() req: VisitorRequest, @Res({ passthrough: true }) res: Response) {
    this.auth.logout(req.cookies?.session)
    res.clearCookie('session')
  }

  // Custom event.
  @Post('burrito')
  @HttpCode(200)
  burrito(@Req() req: VisitorRequest) {
    this.posthog.client.capture({
      distinctId: req.visitor.distinctId,
      event: 'burrito_considered',
      properties: { ...req.visitor.properties, source: 'api' },
    })

    return { considered: true }
  }

  // Feature flag.
  @Get('dashboard')
  async dashboard(@Req() req: VisitorRequest) {
    const flags = await this.posthog.client.evaluateFlags(req.visitor.distinctId)

    return { newDashboard: flags.isEnabled('new-dashboard-feature') }
  }

  // Error tracking: the PostHog interceptor captures this unhandled error.
  @Get('profile')
  profile(): never {
    throw new Error('Profile lookup failed')
  }
}

```

---

## src/app.module.ts

```ts
import { MiddlewareConsumer, Module, NestModule } from '@nestjs/common'
import { AppController } from './app.controller.js'
import { AuthService } from './auth.service.js'
import { PostHogModule } from './posthog/posthog.module.js'
import { VisitorMiddleware } from './visitor.middleware.js'

@Module({
  imports: [PostHogModule],
  controllers: [AppController],
  providers: [AuthService],
})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer) {
    consumer.apply(VisitorMiddleware).forRoutes('{*path}')
  }
}

```

---

## src/auth.service.ts

```ts
import { Injectable } from '@nestjs/common'
import { randomUUID } from 'node:crypto'

export interface User {
  id: string
  username: string
}

// In-memory users and sessions stand in for a real database and session store.
@Injectable()
export class AuthService {
  private readonly users = new Map<string, User>()
  private readonly sessions = new Map<string, User>()

  login(username: string): { user: User; sessionId: string } {
    let user = this.users.get(username)
    if (!user) {
      user = { id: randomUUID(), username }
      this.users.set(username, user)
    }
    const sessionId = randomUUID()
    this.sessions.set(sessionId, user)
    return { user, sessionId }
  }

  logout(sessionId: string | undefined): void {
    if (sessionId) this.sessions.delete(sessionId)
  }

  findBySession(sessionId: string | undefined): User | undefined {
    return sessionId ? this.sessions.get(sessionId) : undefined
  }
}

```

---

## src/main.ts

```ts
import 'reflect-metadata'
import { NestFactory } from '@nestjs/core'
import cookieParser from 'cookie-parser'
import { AppModule } from './app.module.js'

async function bootstrap() {
  const app = await NestFactory.create(AppModule)

  app.use(cookieParser())

  // Lets PostHogService flush queued events when the process is stopped.
  app.enableShutdownHooks()

  await app.listen(process.env.PORT ?? 3000)
}

bootstrap()

```

---

## src/posthog/posthog.module.ts

```ts
import { Global, Module } from '@nestjs/common'
import { APP_INTERCEPTOR } from '@nestjs/core'
import { PostHogInterceptor } from 'posthog-node/nestjs'
import { PostHogService } from './posthog.service.js'
import type { VisitorRequest } from '../visitor.middleware.js'

@Global()
@Module({
  providers: [
    PostHogService,
    {
      // Adds request metadata to events and captures unhandled 5xx errors. getDistinctId ties
      // them to the signed-in user, even for clients that don't send posthog-js tracing headers.
      // Signed-out requests fall through to a personless id.
      provide: APP_INTERCEPTOR,
      inject: [PostHogService],
      useFactory: (posthog: PostHogService) =>
        new PostHogInterceptor(posthog.client, {
          captureExceptions: true,
          getDistinctId: (request: VisitorRequest) => request.visitor?.user?.id,
        }),
    },
  ],
  exports: [PostHogService],
})
export class PostHogModule {}

```

---

## src/posthog/posthog.service.ts

```ts
import { Injectable, Logger, OnApplicationShutdown } from '@nestjs/common'
import { PostHog } from 'posthog-node'

@Injectable()
export class PostHogService implements OnApplicationShutdown {
  private readonly logger = new Logger(PostHogService.name)

  // One client per process, shared by every request.
  readonly client: PostHog

  constructor() {
    const token = process.env.POSTHOG_PROJECT_TOKEN

    if (!token && process.env.NODE_ENV !== 'production') {
      this.logger.warn(
        'POSTHOG_PROJECT_TOKEN variable required by PostHog is missing or un-configured, this causes events to be silently missed. This error stops appearing once POSTHOG_PROJECT_TOKEN is configured',
      )
    }

    // Without a token the client is disabled: capture calls become no-ops.
    this.client = new PostHog(token ?? '', {
      host: process.env.POSTHOG_HOST || 'https://us.i.posthog.com',
      enableExceptionAutocapture: true,
      disabled: !token,
    })
  }

  // Runs on SIGINT/SIGTERM because main.ts calls enableShutdownHooks().
  async onApplicationShutdown(): Promise<void> {
    await this.client.shutdown(3000)
  }
}

```

---

## src/visitor.middleware.ts

```ts
import { Inject, Injectable, NestMiddleware } from '@nestjs/common'
import type { NextFunction, Request, Response } from 'express'
import { randomUUID } from 'node:crypto'
import { AuthService } from './auth.service.js'

export interface Visitor {
  distinctId: string
  user?: { id: string; username: string }
  // Signed-out visitors get no person profile.
  properties: Record<string, unknown>
}

export type VisitorRequest = Request & { visitor: Visitor }

// Resolves who is making the request. Signed-in users are identified by their
// own id. Signed-out visitors get a random id that lives for the visit.
@Injectable()
export class VisitorMiddleware implements NestMiddleware {
  constructor(@Inject(AuthService) private readonly auth: AuthService) {}

  use(req: Request, res: Response, next: NextFunction): void {
    const user = this.auth.findBySession(req.cookies?.session)

    if (user) {
      ;(req as VisitorRequest).visitor = { distinctId: user.id, user, properties: {} }
    } else {
      let visitId: string | undefined = req.cookies?.visit_id
      if (!visitId) {
        visitId = randomUUID()
        res.cookie('visit_id', visitId, { httpOnly: true, sameSite: 'lax' })
      }
      ;(req as VisitorRequest).visitor = {
        distinctId: visitId,
        properties: { $process_person_profile: false },
      }
    }

    next()
  }
}

```

---

