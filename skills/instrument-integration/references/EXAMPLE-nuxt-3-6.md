# PostHog nuxt-3-6 Example Project

Repository: https://github.com/PostHog/context-mill
Path: basics/nuxt-3-6

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

Get your PostHog project token from your [PostHog project settings](https://app.posthog.com/project/settings).

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
  const posthogClient = posthog.init(runtimeConfig.public.posthog.publicKey, {
    api_host: runtimeConfig.public.posthog.host,
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

The session and distinct ID are automatically passed to the backend via the `X-POSTHOG-SESSION-ID` and `X-POSTHOG-DISTINCT-ID` headers when `__add_tracing_headers` is configured in the PostHog initialization.

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

The session and distinct ID are automatically passed to the backend via the `X-POSTHOG-SESSION-ID` and `X-POSTHOG-DISTINCT-ID` headers because we set the `__add_tracing_headers` option in the PostHog initialization.

**Important**: do not identify users on the server-side.

### Server-side API routes (server/api/auth/login.post.ts, server/api/burrito/consider.post.ts)

Server-side API routes create a PostHog Node client for each request and extract session and user context from request headers:

```typescript
import { PostHog } from 'posthog-node'
import { getHeader } from 'h3'

export default defineEventHandler(async (event) => {
  const runtimeConfig = useRuntimeConfig()

  // Relies on __add_tracing_headers being set in the client-side SDK
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
    $posthog: PostHog
  }
}
```

## Learn More

- [PostHog Documentation](https://posthog.com/docs)
- [Nuxt 3 Documentation](https://nuxt.com/docs)
- [PostHog JavaScript Integration Guide](https://posthog.com/docs/libraries/js)

---

## .env.example

```example

NUXT_PUBLIC_POSTHOG_PROJECT_TOKEN=
NUXT_PUBLIC_POSTHOG_HOST=
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
        posthogDefaults: '2026-01-30',
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
      <p>You are now logged in. Feel free to explore:</p>
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
  const posthogClient = posthog.init(runtimeConfig.public.posthog.publicKey, {
    api_host: runtimeConfig.public.posthog.host,
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

    // Relies on __add_tracing_headers being set in the client-side SDK
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

  // Relies on __add_tracing_headers being set in the client-side SDK
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
    $posthog: PostHog
  }
}

export {}

```

---

