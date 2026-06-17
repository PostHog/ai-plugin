# PostHog vue-3 Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/vue-3

---

## README.md

# PostHog Vue 3 + Vite example

This is a [Vue 3](https://vuejs.org/) + [Vite](https://vitejs.dev/) example demonstrating PostHog integration with product analytics, session replay, and error tracking.

It uses the `posthog-js` browser SDK directly and shows how to:

- Initialize PostHog in a Vue 3 SPA
- Identify users after login
- Track custom events from components
- Capture errors via Vue’s global `errorHandler`
- Reset PostHog state on logout

## Features

- **Product analytics**: Track login and burrito consideration events
- **Session replay**: Enabled via `posthog-js` configuration
- **Error tracking**: Global Vue error handler sends exceptions to PostHog
- **Simple auth flow**: Demo login + protected routes using Pinia + Vue Router

## Getting started

### 1. Install dependencies

```bash
npm install
# or
pnpm install
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```bash
VITE_POSTHOG_PROJECT_TOKEN=your_posthog_project_token
VITE_POSTHOG_HOST=https://us.i.posthog.com
```

Get your PostHog project token from your project settings in PostHog.

### 3. Run the development server

```bash
npm run dev
# or
pnpm dev
```

Open `http://localhost:5173` (or whatever Vite prints) in your browser.

## Project structure

```text
src/
  main.ts            # Vue app entrypoint, PostHog init + global errorHandler
  router/
    index.ts         # Routes + simple auth guard
  stores/
    auth.ts          # Pinia auth store (login, logout, user state)
  components/
    Header.vue       # Navigation + logout, calls posthog.reset()
  views/
    Home.vue         # Login form, identifies user + captures 'user_logged_in'
    Burrito.vue      # Burrito consideration demo, captures 'burrito_considered'
    Profile.vue      # Profile + error tracking demo (if implemented)
  App.vue            # Root layout
```

## Key integration points

### PostHog initialization (`src/main.ts`)

`posthog-js` is initialized once when the app boots:

```ts
import posthog from 'posthog-js'

posthog.init(import.meta.env.VITE_POSTHOG_PROJECT_TOKEN || '', {
  api_host: import.meta.env.VITE_POSTHOG_HOST || 'https://us.i.posthog.com',
})

app.config.errorHandler = (err) => {
  posthog.captureException(err)
}
```

This ensures:

- The SDK is configured with your project key and host
- The singleton instance is initialized only once and before the app mounts
- Any uncaught Vue errors are sent to PostHog

### User identification (`src/views/Home.vue`)

After a successful “login”, the app identifies the user and captures a login event:

```ts
const success = await authStore.login(username.value, password.value)
if (success) {
  posthog.identify(username.value)
  posthog.capture('user_logged_in')
}
```

Identification happens **only on login**, all further requests will automatically use the same distinct ID.

### Event tracking (`src/views/Burrito.vue`)

The burrito page tracks a custom event when a user “considers” the burrito:

```ts
posthog.capture('burrito_considered', {
  total_considerations: updatedUser.burritoConsiderations,
  username: updatedUser.username,
})
```

This shows how to attach useful properties to events (e.g. counts, usernames).

### Logout and session reset (`src/components/Header.vue`)

On logout, both the local auth state and PostHog state are cleared:

```ts
authStore.logout()
posthog.reset()
router.push({ name: 'home' })
```

`posthog.reset()` clears the current distinct ID and session so the next login starts a fresh identity.

## Scripts

```bash
# Run dev server
npm run dev

# Type-check, compile, and minify for production
npm run build

# Lint
npm run lint
```

## Learn more

- [PostHog documentation](https://posthog.com/docs)
- [posthog-js SDK](https://posthog.com/docs/libraries/js)
- [Vue 3 documentation](https://vuejs.org/guide/introduction.html)
- [Vite documentation](https://vitejs.dev/guide/)

---

## .editorconfig

```
[*.{js,jsx,mjs,cjs,ts,tsx,mts,cts,vue,css,scss,sass,less,styl}]
charset = utf-8
indent_size = 2
indent_style = space
insert_final_newline = true
trim_trailing_whitespace = true
end_of_line = lf
max_line_length = 100

```

---

## .env.example

```example
VITE_POSTHOG_PROJECT_TOKEN=your_posthog_project_token
VITE_POSTHOG_HOST=https://us.i.posthog.com

```

---

## env.d.ts

```ts
/// <reference types="vite/client" />

```

---

## index.html

```html
<!DOCTYPE html>
<html lang="">
  <head>
    <meta charset="UTF-8">
    <link rel="icon" href="/favicon.ico">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vite App</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>

```

---

## src/App.vue

```vue
<script setup lang="ts">
import Header from '@/components/Header.vue'
</script>

<template>
  <Header />
  <main>
    <RouterView />
  </main>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  line-height: 1.6;
  color: #333;
  background: #f5f5f5;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 2rem auto;
  padding: 0 1rem;
}

h1 {
  margin-bottom: 1rem;
}

p {
  margin-bottom: 1rem;
}
</style>

```

---

## src/components/Header.vue

```vue
<template>
  <header class="header">
    <div class="header-container">
      <nav>
        <RouterLink to="/">Home</RouterLink>
        <template v-if="authStore.user">
          <RouterLink to="/burrito">Burrito Consideration</RouterLink>
          <RouterLink to="/profile">Profile</RouterLink>
        </template>
      </nav>
      <div class="user-section">
        <template v-if="authStore.user && authStore.user.username">
          <span>Welcome, {{ authStore.user.username }}!</span>
          <button @click="handleLogout" class="btn-logout">
            Logout
          </button>
        </template>
        <template v-else>
          <span>Not logged in</span>
          <button v-if="authStore.user" @click="handleLogout" class="btn-logout">
            Clear Session
          </button>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import posthog from 'posthog-js'

const authStore = useAuthStore()
const router = useRouter()

const handleLogout = () => {
  authStore.logout()
  // IMPORTANT: Reset the PostHog instance to clear the user session
  posthog.reset()
  router.push({ name: 'home' })
}
</script>

<style scoped>
.header {
  background-color: #333;
  color: white;
  padding: 1rem;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header nav {
  display: flex;
  gap: 1rem;
}

.header a {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.header a:hover {
  background-color: #555;
  text-decoration: none;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-logout {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-logout:hover {
  background-color: #c82333;
}
</style>

```

---

## src/main.ts

```ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import posthog from "posthog-js";

const app = createApp(App);

posthog.init(import.meta.env.VITE_POSTHOG_PROJECT_TOKEN || '', {
  api_host: import.meta.env.VITE_POSTHOG_HOST || 'https://us.i.posthog.com',
  defaults: '2026-01-30',
});

app.use(createPinia())
app.use(router)

app.config.errorHandler = (err, instance, info) => {
  // report error to tracking services
  posthog.captureException(err)
}

app.mount('#app')

```

---

## src/router/index.ts

```ts
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Home from '@/views/Home.vue'
import Burrito from '@/views/Burrito.vue'
import Profile from '@/views/Profile.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/burrito',
      name: 'burrito',
      component: Burrito,
      meta: { requiresAuth: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: Profile,
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // Check if user exists and has a valid username
  const isValidUser = authStore.user && authStore.user.username
  
  if (to.meta.requiresAuth && !isValidUser) {
    // Clear invalid state
    if (authStore.user && !authStore.user.username) {
      authStore.logout()
    }
    next({ name: 'home' })
  } else {
    next()
  }
})

export default router

```

---

## src/stores/auth.ts

```ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface User {
  username: string
  burritoConsiderations: number
}

const users = new Map<string, User>()

export const useAuthStore = defineStore('auth', () => {

  const getInitialUser = (): User | null => {
    if (typeof window === 'undefined') return null

    const storedUsername = localStorage.getItem('currentUser')
    if (storedUsername) {
      const existingUser = users.get(storedUsername)
      if (existingUser && existingUser.username) {
        return existingUser
      } else {
        // Clean up invalid state
        localStorage.removeItem('currentUser')
      }
    }
    return null
  }

  const user = ref<User | null>(getInitialUser())

  const isAuthenticated = computed(() => user.value !== null)

  const login = async (username: string, password: string): Promise<boolean> => {
    // Client-side only fake auth - no server calls
    if (!username || !password) {
      return false
    }

    let localUser = users.get(username)
    if (!localUser) {
      localUser = {
        username,
        burritoConsiderations: 0
      }
      users.set(username, localUser)
    }

    user.value = localUser
    localStorage.setItem('currentUser', username)

    return true
  }

  const logout = () => {
    user.value = null
    localStorage.removeItem('currentUser')
  }

  const setUser = (newUser: User) => {
    user.value = newUser
    users.set(newUser.username, newUser)
  }

  return {
    user,
    isAuthenticated,
    login,
    logout,
    setUser
  }
})

```

---

## src/views/Burrito.vue

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
        Thank you for your consideration! Count: {{ authStore.user?.burritoConsiderations }}
      </p>
    </div>

    <div class="stats">
      <h3>Consideration stats</h3>
      <p>Total considerations: {{ authStore.user?.burritoConsiderations }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import posthog from 'posthog-js'

const authStore = useAuthStore()
const hasConsidered = ref(false)

const handleConsideration = () => {
  if (!authStore.user) return

  // Client-side only - no server calls
  const updatedUser = {
    ...authStore.user,
    burritoConsiderations: authStore.user.burritoConsiderations + 1
  }
  authStore.setUser(updatedUser)
  hasConsidered.value = true
  setTimeout(() => {
    hasConsidered.value = false
  }, 2000)

  // Capture burrito consideration event
  posthog.capture('burrito_considered', {
    total_considerations: updatedUser.burritoConsiderations,
    username: updatedUser.username
  })
}
</script>

<style scoped>
.container {
  padding: 2rem;
  max-width: 600px;
  margin: 0 auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn-burrito {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 4px;
  font-size: 18px;
  cursor: pointer;
  margin: 2rem 0;
}

.btn-burrito:hover {
  background-color: #218838;
}

.success {
  color: #28a745;
  margin-top: 0.5rem;
}

.stats {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  margin-top: 1rem;
}

h3 {
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}
</style>

```

---

## src/views/Home.vue

```vue
<template>
  <div class="container">
    <template v-if="authStore.user && authStore.user.username">
      <h1>Welcome back, {{ authStore.user.username }}!</h1>
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
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import posthog from 'posthog-js'

const authStore = useAuthStore()
const username = ref('')
const password = ref('')
const error = ref('')

// Clean up invalid user state on mount
onMounted(() => {
  if (authStore.user && !authStore.user.username) {
    authStore.logout()
  }
})

const handleSubmit = async () => {
  error.value = ''

  const success = await authStore.login(username.value, password.value)
  if (success) {
    // Identifying the user once on login/sign up is enough.
    posthog.identify(username.value)
    posthog.capture('user_logged_in')
    
    username.value = ''
    password.value = ''
  } else {
    error.value = 'Please provide both username and password'
  }
}
</script>

<style scoped>
.container {
  padding: 2rem;
  max-width: 600px;
  margin: 0 auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form {
  margin-top: 2rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.form-group input:focus {
  outline: none;
  border-color: #0070f3;
}

.btn-primary {
  background-color: #0070f3;
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  width: 100%;
  margin-top: 1rem;
}

.btn-primary:hover {
  background-color: #0051cc;
}

.error {
  color: #dc3545;
  margin-top: 0.5rem;
}

.note {
  margin-top: 2rem;
  color: #666;
  font-size: 14px;
  text-align: center;
}

ul {
  margin-top: 1rem;
  padding-left: 1.5rem;
}

li {
  margin-bottom: 0.5rem;
}
</style>

```

---

## src/views/Profile.vue

```vue
<template>
  <div class="container">
    <h1>User Profile</h1>

    <div class="stats">
      <h2>Your Information</h2>
      <p><strong>Username:</strong> {{ authStore.user?.username }}</p>
      <p><strong>Burrito Considerations:</strong> {{ authStore.user?.burritoConsiderations }}</p>
    </div>

    <div style="margin-top: 2rem">
      <h3>Your Burrito Journey</h3>
      <template v-if="authStore.user">
        <p v-if="authStore.user.burritoConsiderations === 0">
          You haven't considered any burritos yet. Visit the Burrito Consideration page to start!
        </p>
        <p v-else-if="authStore.user.burritoConsiderations === 1">
          You've considered the burrito potential once. Keep going!
        </p>
        <p v-else-if="authStore.user.burritoConsiderations < 5">
          You're getting the hang of burrito consideration!
        </p>
        <p v-else-if="authStore.user.burritoConsiderations < 10">
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
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
</script>

<style scoped>
.container {
  padding: 2rem;
  max-width: 600px;
  margin: 0 auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stats {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  margin-top: 1rem;
}

h2 {
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}

h3 {
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}
</style>

```

---

## vite.config.ts

```ts
import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})

```

---

