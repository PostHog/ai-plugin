# PostHog nuxt-3-6 Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/nuxt-3-6

---

## README.md

# PostHog Nuxt 3.6 example

This is a [Nuxt 3.6](https://nuxt.com) example demonstrating PostHog integration with product analytics, session replay, feature flags, and error tracking.

Nuxt 3.0 - 3.6 **does not** support the `@posthog/nuxt` package. You must use the `posthog-js` and `posthog-node` packages directly instead. This example also does not cover automatic source map uploads, only available through the `@posthog/nuxt` package.

Nuxt 2.x is also distinctly different, [follow this guide instead](https://posthog.com/docs/libraries/nuxt-js-2).

## Features

- **Product Analytics**: Track user events and behaviors
- **Session Replay**: Record and replay user sessions
- **Error Tracking**: Capture and track errors
- **User Authentication**: Demo login system with PostHog user identification
- **Server-side & Client-side Tracking**: Examples of both tracking methods
- **SSR Support**: Server-side rendering with Nuxt 3.6

## Getting Started

### 1. Install Dependencies

```bash
npm install
# or
pnpm install
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
NUXT_PUBLIC_POSTHOG_PROJECT_TOKEN=your_posthog_project_token
NUXT_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com
```

Get your PostHog project token from your [PostHog project settings](https://app.posthog.com/project/settings). If the token is missing, the app still builds and boots: in development `nuxt.config.ts` logs a warning naming `NUXT_PUBLIC_POSTHOG_PROJECT_TOKEN`, and PostHog is not initialized.

### 3. Run the Development Server

```bash
npm run dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the app.

## Project Structure

```
├── assets/
│   └── css/
│       └── main.css          # Global styles
├── components/
│   └── Header.vue            # Navigation header with auth state
├── composables/
│   └── useAuth.ts            # Authentication composable
├── pages/
│   ├── index.vue             # Home/Login page
│   ├── burrito.vue           # Demo feature page with event tracking
│   └── profile.vue           # User profile with error tracking demo
├── plugins/
│   └── posthog.client.ts     # Client-side PostHog plugin
├── server/
│   ├── api/
│   │   ├── auth/
│   │   │   └── login.post.ts # Login API with server-side tracking
│   │   └── burrito/
│   │       └── consider.post.ts # Burrito API with server-side tracking
│   ├── routes/
│   │   └── burrito-relay/
│   │       └── [...path].ts  # Reverse proxy to PostHog
│   └── utils/
│       └── users.ts          # In-memory user storage utilities
├── types/
│   └── nuxt-app.d.ts          # TypeScript declarations for PostHog
├── app.vue                    # Root component with error handling
└── nuxt.config.ts             # Nuxt configuration
```

## Key Integration Points

### Client-side initialization (plugins/posthog.client.ts)

```typescript
import posthog from 'posthog-js'
import type { PostHog, PostHogInterface } from 'posthog-js'

export default defineNuxtPlugin((nuxtApp) => {
  const runtimeConfig = useRuntimeConfig()
  const publicKey = runtimeConfig.public.posthog.publicKey

  if (!publicKey) {
    return { provide: { posthog: undefined } }
  }

  const posthogClient = posthog.init(publicKey, {
    api_host: '/burrito-relay', // Reverse proxy, see below
    ui_host: 'https://us.posthog.com',
    defaults: runtimeConfig.public.posthog.posthogDefaults as any,
    loaded: (posthog: PostHogInterface) => {
      if (import.meta.env.MODE === 'development') posthog.debug()
    },
  })

  nuxtApp.hook('vue:error', (error) => {
    posthogClient.captureException(error)
  })

  return {
    provide: {
      posthog: posthogClient as PostHog,
    },
  }
})
```

The session and distinct ID are automatically passed to the backend via the `X-POSTHOG-SESSION-ID` and `X-POSTHOG-DISTINCT-ID` headers when `tracing_headers` is configured in the PostHog initialization.

**Important**: do not identify users on the server-side.

### User identification (pages/index.vue)

The user is identified when the user logs in on the **client-side**.

```typescript
const { $posthog: posthog } = useNuxtApp()

const handleSubmit = async () => {
  const success = await auth.login(username.value, password.value)
  if (success) {
    // Identifying the user once on login/sign up is enough.
    posthog?.identify(username.value)
    
    // Capture login event
    posthog?.capture('user_logged_in')
  }
}
```

The session and distinct ID are automatically passed to the backend via the `X-POSTHOG-SESSION-ID` and `X-POSTHOG-DISTINCT-ID` headers because we set the `tracing_headers` option in the PostHog initialization.

**Important**: do not identify users on the server-side.

### Server-side API routes (server/api/auth/login.post.ts, server/api/burrito/consider.post.ts)

Server-side API routes create a PostHog Node client for each request and extract session and user context from request headers:

```typescript
import { PostHog } from 'posthog-node'
import { getHeader } from 'h3'

export default defineEventHandler(async (event) => {
  const runtimeConfig = useRuntimeConfig()

  // Relies on tracing_headers being set in the client-side SDK
  const sessionId = getHeader(event, 'x-posthog-session-id')
  const distinctId = getHeader(event, 'x-posthog-distinct-id')

  const posthog = new PostHog(
    runtimeConfig.public.posthog.publicKey,
    { 
      host: runtimeConfig.public.posthog.host, 
    }
  )

  await posthog.withContext(
    { sessionId: sessionId ?? undefined, distinctId: distinctId ?? undefined },
    async () => {
      posthog.capture({
        event: 'server_login',
        distinctId: distinctId ?? username,
      })
    }
  )

  // Always shutdown to ensure all events are flushed
  await posthog.shutdown()
})
```

**Key Points:**
- Creates a new PostHog Node client for each request
- Extracts `sessionId` and `distinctId` from request headers using `getHeader()` from `h3`
- Uses `withContext()` to associate server-side events with the correct session/user
- Properly shuts down the client after each request to ensure events are flushed

### Event tracking (pages/burrito.vue)

```typescript
const { $posthog: posthog } = useNuxtApp()

const handleConsideration = () => {
  if (user.value) {
    auth.incrementBurritoConsiderations()
    
    posthog?.capture('burrito_considered', {
      total_considerations: user.value?.burritoConsiderations + 1,
      username: user.value?.username,
    })
  }
}
```

### Error tracking (app.vue, plugins/posthog.client.ts, pages/profile.vue)

Errors are captured in three ways:

1. **Vue error hook** - The `vue:error` hook in `plugins/posthog.client.ts` automatically captures Vue errors:
```typescript
nuxtApp.hook('vue:error', (error) => {
  posthogClient.captureException(error)
})
```

2. **Error boundary** - The `onErrorCaptured` in `app.vue` captures component errors:
```typescript
onErrorCaptured((error) => {
  posthog?.captureException(error)
  return false // Let the error propagate
})
```

3. **Manual error capture** in components (pages/profile.vue):
```typescript
const triggerTestError = () => {
  try {
    throw new Error('Test error for PostHog error tracking')
  } catch (err) {
    posthog?.captureException(err as Error)
  }
}
```

### Server-side tracking (server/api/auth/login.post.ts, server/api/burrito/consider.post.ts)

Server-side events use a PostHog Node client created per request:

```typescript
const posthog = new PostHog(
  runtimeConfig.public.posthog.publicKey,
  { 
    host: runtimeConfig.public.posthog.host, 
  }
)

await posthog.withContext(
  { sessionId: sessionId ?? undefined, distinctId: distinctId ?? undefined },
  async () => {
    posthog.capture({
      event: 'server_login',
      distinctId: distinctId ?? username,
    })
  }
)

await posthog.shutdown()
```

**Key Points:**
- The PostHog Node client is created per request in each API route
- Events are automatically associated with the correct user/session via `withContext()`
- The `distinctId` and `sessionId` are extracted from request headers and used to maintain context between client and server
- Always call `shutdown()` to ensure events are flushed

### Accessing PostHog in components

PostHog is accessed via `useNuxtApp()`:

```typescript
const { $posthog: posthog } = useNuxtApp()
posthog?.capture('event_name', { property: 'value' })
```

TypeScript types are provided via `types/nuxt-app.d.ts`:

```typescript
import type { PostHog } from 'posthog-js'

declare module '#app' {
  interface NuxtApp {
    $posthog: PostHog | undefined
  }
}
```

## Reverse proxy

Ad blockers drop events sent to PostHog's domain. This example sends events to its own domain instead: the server route in `server/routes/burrito-relay/[...path].ts` forwards them to PostHog, and the client sets `api_host` to `/burrito-relay` and `ui_host` to your PostHog app URL so toolbar links still work. The route and `ui_host` follow the region in `NUXT_PUBLIC_POSTHOG_HOST`, so setting it to `https://eu.i.posthog.com` sends events to EU Cloud through `eu.i.posthog.com` and `eu-assets.i.posthog.com`. The proxy path is arbitrary, so pick your own and avoid names like `/posthog` or `/analytics`.

Server routes don't exist with `nuxt generate`, and all PostHog traffic passes through your deployment. If your app can't proxy itself, use PostHog's [managed reverse proxy](https://posthog.com/docs/advanced/proxy/managed-reverse-proxy), which is free for PostHog Cloud users.

## Learn More

- [PostHog Documentation](https://posthog.com/docs)
- [Nuxt 3 Documentation](https://nuxt.com/docs)
- [PostHog JavaScript Integration Guide](https://posthog.com/docs/libraries/js)

---

## .env.example

```example
NUXT_PUBLIC_POSTHOG_PROJECT_TOKEN=your_posthog_project_token_here
NUXT_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com

```

---

## app.vue

```vue
<template>
  <div>
    <NuxtRouteAnnouncer />
    <Header />
    <main>
      <NuxtPage />
    </main>
  </div>
</template>

```

---

## components/Header.vue

```vue
<template>
  <header class="header">
    <div class="header-container">
      <nav>
        <NuxtLink to="/">Home</NuxtLink>
        <template v-if="user">
          <NuxtLink to="/burrito">Burrito Consideration</NuxtLink>
          <NuxtLink to="/profile">Profile</NuxtLink>
        </template>
      </nav>
      <div class="user-section">
        <template v-if="user">
          <span>Welcome, {{ user.username }}!</span>
          <button @click="handleLogout" class="btn-logout">
            Logout
          </button>
        </template>
        <template v-else>
          <span>Not logged in</span>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
const auth = useAuth()
const user = computed(() => auth.user.value)
const { $posthog: posthog } = useNuxtApp()

const handleLogout = () => {
  posthog?.capture('user_logged_out')
  posthog?.reset()
  auth.logout()
}
</script>

```

---

## composables/useAuth.ts

```ts
interface User {
  username: string
  burritoConsiderations: number
}

const users = new Map<string, User>()

export const useAuth = () => {
  const user = useState<User | null>('auth-user', () => {
    if (typeof window !== 'undefined') {
      const storedUsername = localStorage.getItem('currentUser')
      if (storedUsername) {
        const existingUser = users.get(storedUsername)
        if (existingUser) {
          return existingUser
        }
      }
    }
    return null
  })

  const login = async (username: string, password: string): Promise<boolean> => {
    if (!username || !password) {
      return false
    }

    try {
      const response = await $fetch('/api/auth/login', {
        method: 'POST',
        body: { username, password },
      })

      if (response.success && response.user) {
        // Update client-side state
        user.value = response.user
        users.set(username, response.user)
        
        if (typeof window !== 'undefined') {
          localStorage.setItem('currentUser', username)
        }

        return true
      }
      return false
    } catch (err) {
      console.error('Login error:', err)
      return false
    }
  }

  const logout = () => {
    user.value = null
    if (typeof window !== 'undefined') {
      localStorage.removeItem('currentUser')
    }
  }

  const setUser = (newUser: User) => {
    user.value = newUser
    users.set(newUser.username, newUser)
  }

  const incrementBurritoConsiderations = () => {
    if (user.value) {
      user.value.burritoConsiderations++
      users.set(user.value.username, user.value)
      // Trigger reactivity by creating a new object
      user.value = { ...user.value }
    }
  }

  return {
    user,
    login,
    logout,
    setUser,
    incrementBurritoConsiderations
  }
}

```

---

## nuxt.config.ts

```ts
if (!process.env.NUXT_PUBLIC_POSTHOG_PROJECT_TOKEN && process.env.NODE_ENV === 'development') {
  console.warn('NUXT_PUBLIC_POSTHOG_PROJECT_TOKEN is not set. Skipping PostHog init.')
}

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    public: {
      posthog: {
        publicKey: process.env.NUXT_PUBLIC_POSTHOG_PROJECT_TOKEN,
        host: process.env.NUXT_PUBLIC_POSTHOG_HOST,
        posthogDefaults: '2026-08-30',
      },
    },
  },
})


```

---

## pages/burrito.vue

```vue
<template>
  <div class="container">
    <h1>Burrito consideration zone</h1>
    <p>Take a moment to truly consider the potential of burritos.</p>

    <div style="text-align: center">
      <button
        @click="handleConsideration"
        class="btn-burrito"
      >
        I have considered the burrito potential
      </button>

      <p v-if="hasConsidered" class="success">
        Thank you for your consideration! Count: {{ user?.burritoConsiderations }}
      </p>
    </div>

    <div class="stats">
      <h3>Consideration stats</h3>
      <p>Total considerations: {{ user?.burritoConsiderations }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const auth = useAuth()
const user = computed(() => auth.user.value)
const router = useRouter()
const hasConsidered = ref(false)
const { $posthog } = useNuxtApp()

// Redirect to home if not logged in
watchEffect(() => {
  if (!user.value) {
    router.push('/')
  }
})

const handleConsideration = async () => {
  if (!user.value) return

  try {
    const response = await $fetch('/api/burrito/consider', {
      method: 'POST',
      body: { username: user.value.username },
    })

    if (response.success && response.user) {
      auth.setUser(response.user)
      hasConsidered.value = true

      // Client-side tracking (in addition to server-side tracking)
      $posthog?.capture('burrito_considered', {
        total_considerations: response.user.burritoConsiderations,
        username: response.user.username,
      })

      setTimeout(() => {
        hasConsidered.value = false
      }, 2000)
    }
  } catch (err) {
    console.error('Error considering burrito:', err)
  }
}
</script>

```

---

## pages/index.vue

```vue
<template>
  <div class="container">
    <template v-if="user">
      <h1>Welcome back, {{ user.username }}!</h1>
      <p>You are logged in. Feel free to explore:</p>
      <ul>
        <li>Consider the potential of burritos</li>
        <li>View your profile and statistics</li>
      </ul>
    </template>
    <template v-else>
      <h1>Welcome to Burrito Consideration App</h1>
      <p>Please sign in to begin your burrito journey</p>

      <form @submit.prevent="handleSubmit" class="form">
        <div class="form-group">
          <label for="username">Username:</label>
          <input
            type="text"
            id="username"
            v-model="username"
            placeholder="Enter any username"
          />
        </div>

        <div class="form-group">
          <label for="password">Password:</label>
          <input
            type="password"
            id="password"
            v-model="password"
            placeholder="Enter any password"
          />
        </div>

        <p v-if="error" class="error">{{ error }}</p>

        <button type="submit" class="btn-primary">Sign In</button>
      </form>

      <p class="note">
        Note: This is a demo app. Use any username and password to sign in.
      </p>
    </template>
  </div>
</template>

<script setup lang="ts">
const auth = useAuth()
const user = computed(() => auth.user.value)
const username = ref('')
const password = ref('')
const error = ref('')
const { $posthog: posthog } = useNuxtApp()

const handleSubmit = async () => {
  error.value = ''

  const success = await auth.login(username.value, password.value)
  if (success) {
    // Identifying the user once on login/sign up is enough.
    posthog?.identify(username.value)
    
    // Capture login event
    posthog?.capture('user_logged_in')
    
    username.value = ''
    password.value = ''
  } else {
    error.value = 'Please provide both username and password'
  }
}
</script>

```

---

## pages/profile.vue

```vue
<template>
  <div class="container">
    <h1>User Profile</h1>

    <div class="stats">
      <h2>Your Information</h2>
      <p><strong>Username:</strong> {{ user?.username }}</p>
      <p><strong>Burrito Considerations:</strong> {{ user?.burritoConsiderations }}</p>
    </div>

    <div style="margin-top: 2rem">
      <button @click="triggerTestError" class="btn-primary" style="background-color: #dc3545">
        Trigger Test Error (for PostHog)
      </button>
    </div>

    <div style="margin-top: 2rem">
      <h3>Your Burrito Journey</h3>
      <template v-if="user">
        <p v-if="user.burritoConsiderations === 0">
          You haven't considered any burritos yet. Visit the Burrito Consideration page to start!
        </p>
        <p v-else-if="user.burritoConsiderations === 1">
          You've considered the burrito potential once. Keep going!
        </p>
        <p v-else-if="user.burritoConsiderations < 5">
          You're getting the hang of burrito consideration!
        </p>
        <p v-else-if="user.burritoConsiderations < 10">
          You're becoming a burrito consideration expert!
        </p>
        <p v-else>
          You are a true burrito consideration master! 🌯
        </p>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
const auth = useAuth()
const user = computed(() => auth.user.value)
const router = useRouter()
const { $posthog: posthog } = useNuxtApp()

// Redirect to home if not logged in
watchEffect(() => {
  if (!user.value) {
    router.push('/')
  }
})

const triggerTestError = () => {
  try {
    throw new Error('Test error for PostHog error tracking')
  } catch (err) {
    console.error('Captured error:', err)
    posthog?.captureException(err as Error)
  }
}
</script>

```

---

## plugins/posthog.client.ts

```ts
import { defineNuxtPlugin, useRuntimeConfig } from '#imports'
import posthog from 'posthog-js'
import type { PostHog, PostHogInterface } from 'posthog-js'

export default defineNuxtPlugin((nuxtApp) => {
  const runtimeConfig = useRuntimeConfig()
  const publicKey = runtimeConfig.public.posthog.publicKey

  // nuxt.config.ts warns about a missing token in development
  if (!publicKey) {
    return { provide: { posthog: undefined } }
  }

  const posthogClient = posthog.init(publicKey, {
    // Events go through the server route in server/routes/burrito-relay
    api_host: '/burrito-relay',
    // The PostHog app for the region in NUXT_PUBLIC_POSTHOG_HOST
    ui_host: String(runtimeConfig.public.posthog.host || '').includes('eu.') ? 'https://eu.posthog.com' : 'https://us.posthog.com',
    defaults: runtimeConfig.public.posthog.posthogDefaults as any,
    // Automatically add X-POSTHOG-SESSION-ID and X-POSTHOG-DISTINCT-ID headers
    // to same-origin requests so server-side events join the same session.
    tracing_headers: [window.location.hostname],
    loaded: (posthog: PostHogInterface) => {
      if (import.meta.env.MODE === 'development') posthog.debug()
    },
  })

  nuxtApp.hook('vue:error', (error) => {
    posthogClient.captureException(error)
  })

  return {
    provide: {
      posthog: posthogClient as PostHog,
    },
  }
})

```

---

## public/robots.txt

```txt
User-Agent: *
Disallow:

```

---

## server/api/auth/login.post.ts

```ts
import { getOrCreateUser } from '~/server/utils/users'
import { PostHog } from 'posthog-node'
import { useRuntimeConfig } from '#imports'
import { getHeader } from 'h3'

export default defineEventHandler(async (event) => {
  if (event.node.req.method !== 'POST') {
    throw createError({
      statusCode: 405,
      statusMessage: 'Method Not Allowed'
    })
  }

  const body = await readBody(event)
  const { username, password } = body

  if (!username || !password) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Username and password required'
    })
  }

  // Fake auth - just get or create user
  const user = getOrCreateUser(username)

  const runtimeConfig = useRuntimeConfig()

    // Relies on tracing_headers being set in the client-side SDK
  const sessionId = getHeader(event, 'x-posthog-session-id')
  const distinctId = getHeader(event, 'x-posthog-distinct-id')

  const posthog = new PostHog(
    runtimeConfig.public.posthog.publicKey,
    {
      host: runtimeConfig.public.posthog.host,
      disabled: !runtimeConfig.public.posthog.publicKey,
    }
  )

  await posthog.withContext(
    { sessionId: sessionId ?? undefined, distinctId: distinctId ?? undefined },
    async () => {
      posthog.capture({
        event: 'server_login',
        distinctId: distinctId ?? username,
      })
    }
  )

  // Always shutdown to ensure all events are flushed
  await posthog.shutdown()

  return {
    success: true,
    user: { ...user }
  }
})

```

---

## server/api/burrito/consider.post.ts

```ts
import { users, incrementBurritoConsiderations } from '~/server/utils/users'
import { PostHog } from 'posthog-node'
import { useRuntimeConfig } from '#imports'
import { getHeader } from 'h3'

export default defineEventHandler(async (event) => {
  if (event.node.req.method !== 'POST') {
    throw createError({
      statusCode: 405,
      statusMessage: 'Method Not Allowed'
    })
  }

  const body = await readBody(event)
  const { username } = body

  if (!username) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Username required'
    })
  }

  if (!users.has(username)) {
    throw createError({
      statusCode: 404,
      statusMessage: 'User not found'
    })
  }

  // Increment burrito considerations (fake, in-memory)
  const user = incrementBurritoConsiderations(username)

  const runtimeConfig = useRuntimeConfig()

  // Relies on tracing_headers being set in the client-side SDK
  const sessionId = getHeader(event, 'x-posthog-session-id')
  const distinctId = getHeader(event, 'x-posthog-distinct-id')

  const posthog = new PostHog(
    runtimeConfig.public.posthog.publicKey,
    {
      host: runtimeConfig.public.posthog.host,
      disabled: !runtimeConfig.public.posthog.publicKey,
    }
  )

  await posthog.withContext(
    { sessionId: sessionId ?? undefined, distinctId: distinctId ?? undefined },
    async () => {
      posthog.capture({
        event: 'burrito_considered',
        distinctId: distinctId ?? username,
      })
    }
  )

  // Always shutdown to ensure all events are flushed
  await posthog.shutdown()

  return {
    success: true,
    user: { ...user }
  }
})

```

---

## server/routes/burrito-relay/[...path].ts

```ts
export default defineEventHandler(async (event) => {
  const path = event.context.params?.path || ''
  const url = getRequestURL(event)
  const search = url.search || ''

  // Proxy to the region in NUXT_PUBLIC_POSTHOG_HOST: us.i.posthog.com or eu.i.posthog.com
  const apiHostname = new URL(process.env.NUXT_PUBLIC_POSTHOG_HOST || 'https://us.i.posthog.com').hostname
  const useAssetHost = path.startsWith('static/') || path.startsWith('array/')
  const hostname = useAssetHost
    ? apiHostname.replace('.i.posthog.com', '-assets.i.posthog.com')
    : apiHostname

  const targetUrl = `https://${hostname}/${path}${search}`

  // Forward headers, excluding ones that shouldn't be proxied
  const headers = new Headers()
  const excludedHeaders = ['host', 'connection', 'content-length', 'transfer-encoding', 'accept-encoding', 'cookie']

  const requestHeaders = getRequestHeaders(event)
  for (const [key, value] of Object.entries(requestHeaders)) {
    const name = key.toLowerCase()
    // Forward PostHog keys (Bearer phc_, phs_ or phx_), which the SDKs need. Strip any other credentials.
    // To allow an older key without one of these prefixes, also match its exact 'Bearer <key>' value.
    const isNonBearerAuth = name === 'authorization' && !/^Bearer ph[csx]_/.test(value ?? '')
    if (value && !excludedHeaders.includes(name) && !isNonBearerAuth) {
      headers.set(key, value)
    }
  }

  headers.set('host', hostname)

  // Forward client IP for geolocation
  const clientIp = getHeader(event, 'x-forwarded-for') || getRequestIP(event)
  if (clientIp) {
    headers.set('x-forwarded-for', clientIp)
  }

  // Read body as binary buffer to preserve gzip compression
  const body = event.method !== 'GET' && event.method !== 'HEAD'
    ? await readRawBody(event, false)
    : undefined

  const response = await fetch(targetUrl, {
    method: event.method,
    headers,
    body,
  })

  // Copy response headers, excluding problematic ones
  for (const [key, value] of response.headers.entries()) {
    if (!['content-encoding', 'content-length', 'transfer-encoding'].includes(key.toLowerCase())) {
      setResponseHeader(event, key, value)
    }
  }

  setResponseStatus(event, response.status)

  // Return binary response
  const arrayBuffer = await response.arrayBuffer()
  return Buffer.from(arrayBuffer)
})

```

---

## server/utils/users.ts

```ts
interface User {
  username: string
  burritoConsiderations: number
}

// Shared in-memory storage for users (fake, no database)
export const users = new Map<string, User>()

export function getOrCreateUser(username: string): User {
  let user = users.get(username)
  
  if (!user) {
    user = { 
      username, 
      burritoConsiderations: 0 
    }
    users.set(username, user)
  }
  
  return user
}

export function incrementBurritoConsiderations(username: string): User {
  const user = users.get(username)
  
  if (!user) {
    throw new Error('User not found')
  }
  
  user.burritoConsiderations++
  users.set(username, user)
  
  return { ...user }
}

```

---

## types/nuxt-app.d.ts

```ts
import type { PostHog } from 'posthog-js'

declare module '#app' {
  interface NuxtApp {
    $posthog: PostHog | undefined
  }
}

export {}

```

---

