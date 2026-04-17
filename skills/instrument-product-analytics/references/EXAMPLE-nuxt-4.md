# PostHog nuxt-4 Example Project

Repository: https://github.com/PostHog/context-mill
Path: basics/nuxt-4

---

## README.md

# PostHog Nuxt 4 example

This is a [Nuxt 4](https://nuxt.com) example demonstrating PostHog integration with product analytics, session replay, feature flags, and error tracking.

Nuxt 4 supports the `@posthog/nuxt` package, which provides automatic PostHog integration with built-in error tracking, source map uploads, and simplified configuration. This is the recommended approach for Nuxt 4+.

For Nuxt 3.0 - 3.6, you must use the `posthog-js` and `posthog-node` packages directly instead. See the [Nuxt 3.6 example](../nuxt-3-6) for that approach.

## Features

- **Product Analytics**: Track user events and behaviors
- **Session Replay**: Record and replay user sessions
- **Error Tracking**: Automatic error capture on both client and server
- **Source Maps**: Automatic source map uploads when *building for production*
- **User Authentication**: Demo login system with PostHog user identification
- **Server-side & Client-side Tracking**: Examples of both tracking methods
- **SSR Support**: Server-side rendering with Nuxt 4

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

# Optional: For source map uploads
PROJECT_ID=your_project_id
PERSONAL_API_KEY=your_personal_api_key
```

Get your PostHog project token from your [PostHog project settings](https://app.posthog.com/project/settings).

For source map uploads, get your project ID from [PostHog environment variables](https://app.posthog.com/settings/environment#variables) and your personal API key from [PostHog user API keys](https://app.posthog.com/settings/user-api-keys) (requires `organization:read` and `error_tracking:write` scopes).

### 3. Run the Development Server

```bash
npm run dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the app.

## Project Structure

```
├── app/
│   ├── components/
│   │   └── AppHeader.vue        # Navigation header with auth state
│   ├── composables/
│   │   └── useAuth.ts           # Authentication composable
│   ├── middleware/
│   │   └── auth.ts              # Authentication middleware
│   ├── pages/
│   │   ├── index.vue            # Home/Login page
│   │   ├── burrito.vue          # Demo feature page with event tracking
│   │   └── profile.vue           # User profile with error tracking demo
│   ├── utils/
│   │   └── formValidation.ts    # Form validation utilities
│   └── app.vue                  # Root component
├── assets/
│   └── css/
│       └── main.css              # Global styles
├── server/
│   ├── api/
│   │   ├── auth/
│   │   │   └── login.post.ts     # Login API with server-side tracking
│   │   └── burrito/
│   │       └── consider.post.ts  # Burrito consideration API with server-side tracking
│   └── utils/
│       ├── posthog.ts            # Server-side PostHog utility
│       └── users.ts              # In-memory user storage utilities
├── nuxt.config.ts               # Nuxt configuration with PostHog module
└── package.json
```

## Key Integration Points

### Module Configuration (nuxt.config.ts)

Nuxt 4 uses the `@posthog/nuxt` module for automatic PostHog integration:

```typescript
export default defineNuxtConfig({
  modules: ['@posthog/nuxt'],
  runtimeConfig: {
    public: {
      posthog: {
        publicKey: process.env.NUXT_PUBLIC_POSTHOG_PROJECT_TOKEN || '',
        host: process.env.NUXT_PUBLIC_POSTHOG_HOST || 'https://us.i.posthog.com',
      },
    },
  },
  posthogConfig: {
    publicKey: process.env.NUXT_PUBLIC_POSTHOG_PROJECT_TOKEN || '',
    host: process.env.NUXT_PUBLIC_POSTHOG_HOST || 'https://us.i.posthog.com',
    clientConfig: {
      capture_exceptions: true, // Enables automatic exception capture on the client side (Vue)
      __add_tracing_headers: ['localhost', 'yourdomain.com'], // Add your domain here
    },
    serverConfig: {
      enableExceptionAutocapture: true, // Enables automatic exception capture on the server side (Nitro)
    },
    sourcemaps: {
      enabled: true,
      envId: process.env.PROJECT_ID || '',
      personalApiKey: process.env.PERSONAL_API_KEY || '',
      project: 'my-application',
      version: '1.0.0',
    },
  },
})
```

**Key Points:**
- The `@posthog/nuxt` module handles PostHog initialization automatically
- Client-side error tracking is enabled via `capture_exceptions: true`
- Server-side error tracking is enabled via `enableExceptionAutocapture: true`
- Source map uploads are configured for better error tracking
- The `__add_tracing_headers` option automatically adds `X-POSTHOG-SESSION-ID` and `X-POSTHOG-DISTINCT-ID` headers to requests

**Important**: do not identify users on the server-side.

### User identification (app/pages/index.vue)

The user is identified when the user logs in on the **client-side**.

```typescript
const posthog = usePostHog()

const handleSubmit = async () => {
  const success = await auth.login(formData.username, formData.password)
  if (success) {
    // Identifying the user once on login/sign up is enough.
    posthog?.identify(formData.username)
    
    // Capture login event
    posthog?.capture('user_logged_in')
  }
}
```

The session and distinct ID are automatically passed to the backend via the `X-POSTHOG-SESSION-ID` and `X-POSTHOG-DISTINCT-ID` headers because we set the `__add_tracing_headers` option in the PostHog configuration.

**Important**: do not identify users on the server-side.

### Server-side API routes (server/api/auth/login.post.ts)

Server-side API routes use the `useServerPostHog()` utility to get a PostHog Node client and extract session and user context from request headers:

```typescript
import { useServerPostHog } from '../../utils/posthog'
import { getOrCreateUser, users } from '../../utils/users'

export default defineEventHandler(async (event) => {
  const body = await readBody<{ username: string; password: string }>(event)
  const { username, password } = body || {}

  if (!username || !password) {
    throw createError({
      statusCode: 400,
      message: 'Username and password required',
    })
  }

  const user = getOrCreateUser(username)
  const isNewUser = !users.has(username)

  const sessionId = getHeader(event, 'x-posthog-session-id')
  const distinctId = getHeader(event, 'x-posthog-distinct-id')

  // Capture server-side login event
  const posthog = useServerPostHog()
  
  posthog.capture({
    distinctId: distinctId,
    event: 'server_login',
    properties: {
      $session_id: sessionId,
      username: username,
      isNewUser: isNewUser,
      source: 'api',
    },
  })

  return {
    success: true,
    user,
  }
})
```

**Key Points:**
- Uses `useServerPostHog()` utility to get a shared PostHog Node client instance
- Extracts `sessionId` and `distinctId` from request headers using `getHeader()` (auto-imported from h3)
- The PostHog client is reused across requests (singleton pattern)
- h3 functions like `defineEventHandler`, `readBody`, `createError`, `getHeader` are auto-imported in server routes

### Event tracking (app/pages/burrito.vue)

The burrito consideration page demonstrates both client-side and server-side event tracking:

```typescript
const posthog = usePostHog()

const handleConsideration = async () => {
  if (!user.value) return

  try {
    // Call server-side API route
    const response = await $fetch('/api/burrito/consider', {
      method: 'POST',
      body: { username: user.value.username },
    })

    if (response.success && response.user) {
      auth.setUser(response.user)
      hasConsidered.value = true

      // Client-side tracking (in addition to server-side tracking)
      posthog?.capture('burrito_considered', {
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
```

The server-side route (`server/api/burrito/consider.post.ts`) also captures the event, demonstrating dual tracking.

### Error tracking

Errors are captured automatically in multiple ways:

1. **Automatic client-side capture** - The `@posthog/nuxt` module automatically captures Vue errors when `capture_exceptions: true` is set in `posthogConfig.clientConfig`.

2. **Automatic server-side capture** - The module automatically captures Nitro errors when `enableExceptionAutocapture: true` is set in `posthogConfig.serverConfig`.

3. **Manual error capture** in components (app/pages/profile.vue):
```typescript
const posthog = usePostHog()

const triggerTestError = () => {
  try {
    throw new Error('Test error for PostHog error tracking')
  } catch (err) {
    posthog?.captureException(err)
  }
}
```

### Server-side tracking (server/api/auth/login.post.ts)

Server-side events use the shared PostHog Node client. Note that h3 functions are auto-imported in Nuxt server routes:

```typescript
import { useServerPostHog } from '../../utils/posthog'
import { getOrCreateUser, users } from '../../utils/users'

export default defineEventHandler(async (event) => {
  const body = await readBody<{ username: string; password: string }>(event)
  const { username, password } = body || {}

  // ... validation logic ...

  // Extract headers using getHeader (auto-imported from h3)
  const sessionId = getHeader(event, 'x-posthog-session-id')
  const distinctId = getHeader(event, 'x-posthog-distinct-id')

  // Capture server-side event
  const posthog = useServerPostHog()
  
  posthog.capture({
    distinctId: distinctId,
    event: 'server_login',
    properties: {
      $session_id: sessionId,
      username: username,
      isNewUser: isNewUser,
      source: 'api',
    },
  })

  return { success: true, user }
})
```

**Key Points:**
- The PostHog Node client is shared across requests via `useServerPostHog()` utility
- `getHeader()` is auto-imported from h3 in Nuxt server routes (no need to import from 'h3')
- h3 functions like `defineEventHandler`, `readBody`, `createError` are also auto-imported
- The `distinctId` and `sessionId` are extracted from request headers and used to maintain context between client and server
- No need to manually shutdown the client (it's managed by the module)

### Accessing PostHog in components

PostHog is accessed via the `usePostHog()` composable provided by `@posthog/nuxt`:

```typescript
const posthog = usePostHog()
posthog?.capture('event_name', { property: 'value' })
```

The composable is automatically typed and available throughout your Nuxt application.

### Server-side PostHog utility (server/utils/posthog.ts)

The server utility provides a shared PostHog Node client instance:

```typescript
import { PostHog } from 'posthog-node'

let client: PostHog | null = null

export function useServerPostHog(): PostHog {
  if (!client) {
    const config = useRuntimeConfig()
    const posthogConfig = config.public.posthog
    client = new PostHog(posthogConfig.publicKey, {
      host: posthogConfig.host,
    })
  }
  return client
}
```

This ensures a single PostHog client instance is reused across all server requests, improving performance.

## Differences from Nuxt 3.6

- **Module-based**: Uses `@posthog/nuxt` module instead of manual plugin setup
- **Automatic error tracking**: Built-in error capture on both client and server
- **Source map uploads**: Automatic source map uploads for better error tracking
- **Simplified API**: Uses `usePostHog()` composable instead of `useNuxtApp().$posthog`
- **Shared server client**: Reuses PostHog Node client across requests instead of creating per-request
- **Automatic imports**: In Nuxt 4 server routes, h3 functions (`defineEventHandler`, `readBody`, `createError`, `getHeader`, etc.) are auto-imported - no need to import them explicitly

## Learn More

- [PostHog Documentation](https://posthog.com/docs)
- [Nuxt 4 Documentation](https://nuxt.com/docs)
- [PostHog Nuxt Integration Guide](https://posthog.com/docs/libraries/nuxt-js)
- [@posthog/nuxt Package](https://www.npmjs.com/package/@posthog/nuxt)

---

## .env.example

```example
NUXT_PUBLIC_POSTHOG_PROJECT_TOKEN=
NUXT_PUBLIC_POSTHOG_HOST=
PROJECT_ID=
PERSONAL_API_KEY=
```

---

## app/app.vue

```vue
<template>
  <div style="min-height: 100vh; display: flex; flex-direction: column; background: #f5f5f5; width: 100%;">
    <AppHeader />
    <main style="flex: 1;">
      <NuxtPage />
    </main>
  </div>
</template>

```

---

## app/components/AppHeader.vue

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
        <span v-if="user">Welcome, {{ user.username }}!</span>
        <span v-else>Not logged in</span>
        <button v-if="user" @click="handleLogout" class="btn-logout">Logout</button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
const posthog = usePostHog()
const auth = useAuth()
const user = computed(() => auth.user.value)

const handleLogout = async () => {
  auth.logout()
  posthog?.capture('user_logged_out')
  posthog?.reset()
  await navigateTo('/')
}
</script>

```

---

## app/composables/useAuth.ts

```ts
interface User {
  username: string
  burritoConsiderations: number
}

const users: Map<string, User> = new Map()

export function useAuth() {
  const user = useState<User | null>('auth-user', () => {
    if (process.client) {
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
    try {
      const response = await $fetch<{ success: boolean; user: User }>('/api/auth/login', {
        method: 'POST',
        body: { username, password },
      })

      if (response.success) {
        let localUser = users.get(username)
        if (!localUser) {
          localUser = response.user
          users.set(username, localUser)
        }

        user.value = localUser
        if (process.client) {
          localStorage.setItem('currentUser', username)
        }

        return true
      }
      return false
    } catch (error) {
      console.error('Login error:', error)
      return false
    }
  }

  const logout = () => {
    user.value = null
    if (process.client) {
      localStorage.removeItem('currentUser')
    }
  }

  const incrementBurritoConsiderations = () => {
    if (user.value) {
      user.value.burritoConsiderations++
      users.set(user.value.username, user.value)
      // Trigger reactivity
      user.value = { ...user.value }
    }
  }

  const setUser = (newUser: User) => {
    user.value = newUser
    users.set(newUser.username, newUser)
  }

  return {
    user,
    login,
    logout,
    incrementBurritoConsiderations,
    setUser,
  }
}

```

---

## app/middleware/auth.ts

```ts
export default defineNuxtRouteMiddleware((to, from) => {
  const auth = useAuth()
  const user = auth.user.value

  // If user is not logged in, redirect to home/login page
  if (!user) {
    return navigateTo('/')
  }
})

```

---

## app/pages/burrito.vue

```vue
<template>
  <div class="container">
    <h1>Burrito consideration zone</h1>
    <p>Take a moment to truly consider the potential of burritos.</p>

    <div style="text-align: center">
      <button @click="handleConsideration" class="btn-burrito">
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
definePageMeta({
  middleware: 'auth'
})

const auth = useAuth()
const user = computed(() => auth.user.value)
const posthog = usePostHog()
const hasConsidered = ref(false)

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
      posthog?.capture('burrito_considered', {
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

## app/pages/index.vue

```vue
<template>
  <div class="container">
    <h1 v-if="user">Welcome back, {{ user.username }}!</h1>
    <h1 v-else>Welcome to Burrito Consideration App</h1>

    <div v-if="user">
      <p>You are now logged in. Feel free to explore:</p>
      <ul>
        <li>Consider the potential of burritos</li>
        <li>View your profile and statistics</li>
      </ul>
    </div>

    <div v-else>
      <p>Please sign in to begin your burrito journey</p>

      <form @submit.prevent="handleSubmit" class="form" novalidate>
        <div class="form-group">
          <label for="username">Username:</label>
          <input
            id="username"
            v-model="formData.username"
            type="text"
            placeholder="Enter any username"
            :class="{ 'error-input': errors.username }"
            @blur="validateField('username')"
            @input="clearError('username')"
          />
          <p v-if="errors.username" class="field-error">{{ errors.username }}</p>
        </div>

        <div class="form-group">
          <label for="password">Password:</label>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            placeholder="Enter any password"
            :class="{ 'error-input': errors.password }"
            @blur="validateField('password')"
            @input="clearError('password')"
          />
          <p v-if="errors.password" class="field-error">{{ errors.password }}</p>
        </div>

        <p v-if="error" class="error">{{ error }}</p>

        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'Signing in...' : 'Sign In' }}
        </button>
      </form>

      <p class="note">
        Note: This is a demo app. Use any username and password to sign in.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { loginSchema, validateForm, type LoginFormData } from '../utils/formValidation'

const auth = useAuth()
const user = computed(() => auth.user.value)

const posthog = usePostHog()

const formData = reactive<LoginFormData>({
  username: '',
  password: '',
})

const errors = reactive<Partial<Record<keyof LoginFormData, string>>>({})
const error = ref('')
const isSubmitting = ref(false)

const validateField = (field: keyof LoginFormData) => {
  const fieldSchema = loginSchema.shape[field]
  if (!fieldSchema) return

  const result = fieldSchema.safeParse(formData[field])
  if (!result.success) {
    errors[field] = result.error.errors[0]?.message || 'Invalid value'
  } else {
    delete errors[field]
  }
}

const clearError = (field: keyof LoginFormData) => {
  delete errors[field]
}

const handleSubmit = async () => {
  // Clear previous errors
  error.value = ''
  Object.keys(errors).forEach((key) => {
    delete errors[key as keyof LoginFormData]
  })

  // Validate entire form
  const validation = validateForm(loginSchema, formData)
  if (!validation.success) {
    Object.assign(errors, validation.errors)
    return
  }

  isSubmitting.value = true

  try {
    const success = await auth.login(formData.username, formData.password)
    if (success) {
      // Identifying the user once on login/sign up is enough.
      posthog?.identify(formData.username)
      
      // Capture login event
      posthog?.capture('user_logged_in')
      formData.username = ''
      formData.password = ''
      await navigateTo('/')
    } else {
      error.value = 'Login failed. Please check your credentials and try again.'
    }
  } catch (err) {
    console.error('Login failed:', err)
    error.value = 'An error occurred during login. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

```

---

## app/pages/profile.vue

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
      <p v-if="user?.burritoConsiderations === 0">
        You haven't considered any burritos yet. Visit the Burrito Consideration page to start!
      </p>
      <p v-else-if="user?.burritoConsiderations === 1">
        You've considered the burrito potential once. Keep going!
      </p>
      <p v-else-if="user && user.burritoConsiderations < 5">
        You're getting the hang of burrito consideration!
      </p>
      <p v-else-if="user && user.burritoConsiderations < 10">
        You're becoming a burrito consideration expert!
      </p>
      <p v-else>You are a true burrito consideration master! 🌯</p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

const auth = useAuth()
const user = computed(() => auth.user.value)
const posthog = usePostHog()

const triggerTestError = () => {
  try {
    throw new Error('Test error for PostHog error tracking')
  } catch (err) {
    console.error('Captured error:', err)
    posthog?.captureException(err)
  }
}
</script>

```

---

## app/utils/formValidation.ts

```ts
import { z } from 'zod'

export const loginSchema = z.object({
  username: z
    .string()
    .min(1, 'Username is required')
    .min(3, 'Username must be at least 3 characters')
    .max(50, 'Username must be less than 50 characters'),
  password: z
    .string()
    .min(1, 'Password is required')
    .min(3, 'Password must be at least 3 characters'),
})

export type LoginFormData = z.infer<typeof loginSchema>

export function validateForm<T>(schema: z.ZodSchema<T>, data: unknown): {
  success: boolean
  data?: T
  errors?: Record<string, string>
} {
  const result = schema.safeParse(data)

  if (result.success) {
    return { success: true, data: result.data }
  }

  const errors: Record<string, string> = {}
  result.error.errors.forEach((error) => {
    const path = error.path.join('.')
    errors[path] = error.message
  })

  return { success: false, errors }
}

```

---

## nuxt.config.ts

```ts
import { fileURLToPath } from 'node:url'
import { resolve, dirname } from 'node:path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  css: [resolve(__dirname, 'assets/css/main.css')],
  modules: ['@posthog/nuxt'],
  runtimeConfig: {
    public: {
      posthog: {
        publicKey: process.env.NUXT_PUBLIC_POSTHOG_PROJECT_TOKEN || '',
        host: process.env.NUXT_PUBLIC_POSTHOG_HOST || 'https://us.i.posthog.com',
      },
    },
  },
  posthogConfig: {
    publicKey: process.env.NUXT_PUBLIC_POSTHOG_PROJECT_TOKEN || '', // Find it in project settings https://app.posthog.com/settings/project
    host: process.env.NUXT_PUBLIC_POSTHOG_HOST || 'https://us.i.posthog.com', // Optional: defaults to https://us.i.posthog.com. Use https://eu.i.posthog.com for EU region
    clientConfig: {
      capture_exceptions: true, // Enables automatic exception capture on the client side (Vue)
      __add_tracing_headers: [ 'localhost', 'yourdomain.com' ], // Add your domain here
    },
    serverConfig: {
      enableExceptionAutocapture: true, // Enables automatic exception capture on the server side (Nitro)
    },
    sourcemaps: {
      enabled: true,
      envId: process.env.PROJECT_ID || '', // Your project ID from PostHog settings https://app.posthog.com/settings/environment#variables
      personalApiKey: process.env.PERSONAL_API_KEY || '', // Your personal API key from PostHog settings https://app.posthog.com/settings/user-api-keys (requires organization:read and error_tracking:write scopes)
      project: 'my-application', // Optional: defaults to git repository name
      version: '1.0.0', // Optional: defaults to current git commit
    },
  },
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
import { useServerPostHog } from '../../utils/posthog'
import { getOrCreateUser, users } from '../../utils/users'

export default defineEventHandler(async (event) => {
  const body = await readBody<{ username: string; password: string }>(event)
  const { username, password } = body || {}

  if (!username || !password) {
    throw createError({
      statusCode: 400,
      message: 'Username and password required',
    })
  }

  const user = getOrCreateUser(username)
  const isNewUser = !users.has(username)

  const sessionId = getHeader(event, 'x-posthog-session-id')
  const distinctId = getHeader(event, 'x-posthog-distinct-id')

  // Capture server-side login event
  const posthog = useServerPostHog()
  
  posthog.capture({
    distinctId: distinctId,
    event: 'server_login',
    properties: {
      $session_id: sessionId,
      username: username,
      isNewUser: isNewUser,
      source: 'api',
    },
  })

  return {
    success: true,
    user,
  }
})

```

---

## server/api/burrito/consider.post.ts

```ts
import { useServerPostHog } from '../../utils/posthog'
import { users, incrementBurritoConsiderations } from '../../utils/users'
import { defineEventHandler, readBody, createError, getHeader } from 'h3'

export default defineEventHandler(async (event) => {
  const body = await readBody<{ username: string }>(event)
  const username = body?.username

  if (!username) {
    throw createError({
      statusCode: 400,
      message: 'Username required',
    })
  }

  if (!users.has(username)) {
    throw createError({
      statusCode: 404,
      message: 'User not found',
    })
  }

  // Increment burrito considerations (fake, in-memory)
  const user = incrementBurritoConsiderations(username)

  const sessionId = getHeader(event, 'x-posthog-session-id')
  const distinctId = getHeader(event, 'x-posthog-distinct-id')

  // Capture server-side burrito consideration event
  const posthog = useServerPostHog()
  
  posthog.capture({
    distinctId: distinctId,
    event: 'burrito_considered',
    properties: {
      $session_id: sessionId,
      username: username,
      total_considerations: user.burritoConsiderations,
      source: 'api',
    },
  })

  return {
    success: true,
    user: { ...user },
  }
})

```

---

## server/utils/posthog.ts

```ts
import { PostHog } from 'posthog-node'

let client: PostHog | null = null

export function useServerPostHog(): PostHog {
  if (!client) {
    const config = useRuntimeConfig()
    // The @posthog/nuxt module exposes config at runtimeConfig.public.posthog
    const posthogConfig = config.public.posthog
    client = new PostHog(posthogConfig.publicKey, {
      host: posthogConfig.host,
    })
  }
  return client
}

```

---

## server/utils/users.ts

```ts
// Shared in-memory storage for users (fake, no database)
export const users = new Map<string, { username: string; burritoConsiderations: number }>()

export function getOrCreateUser(username: string): { username: string; burritoConsiderations: number } {
  let user = users.get(username)
  
  if (!user) {
    user = { username, burritoConsiderations: 0 }
    users.set(username, user)
  }
  
  return user
}

export function incrementBurritoConsiderations(username: string): { username: string; burritoConsiderations: number } {
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

