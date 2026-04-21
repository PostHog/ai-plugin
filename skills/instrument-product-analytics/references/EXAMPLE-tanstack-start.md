# PostHog tanstack-start Example Project

Repository: https://github.com/PostHog/context-mill
Path: basics/tanstack-start

---

## README.md

# PostHog TanStack Start example

This is a [TanStack Start](https://tanstack.com/start) example demonstrating PostHog integration with product analytics, session replay, feature flags, and error tracking.

## Features

- **Product analytics**: Track user events and behaviors
- **Session replay**: Record and replay user sessions
- **Error tracking**: Capture and track errors automatically
- **User authentication**: Demo login system with PostHog user identification
- **Server-side & client-side tracking**: Complete examples of both tracking methods
- **Reverse proxy**: PostHog ingestion through Vite dev server proxy

## Getting started

### 1. Install dependencies

```bash
npm install
```

### 2. Configure environment variables

Create a `.env` file in the root directory:

```bash
VITE_PUBLIC_POSTHOG_PROJECT_TOKEN=your_posthog_project_token
VITE_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com
```

Get your PostHog project token from your [PostHog project settings](https://app.posthog.com/project/settings).

### 3. Run the development server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the app.

## Project structure

```
src/
├── components/
│   └── Header.tsx           # Navigation header with auth state
├── contexts/
│   └── AuthContext.tsx      # Authentication context with PostHog integration
├── utils/
│   └── posthog-server.ts   # Server-side PostHog client
├── routes/
│   ├── __root.tsx           # Root route with PostHogProvider
│   ├── index.tsx            # Home/login page
│   ├── burrito.tsx          # Demo feature page with event tracking
│   ├── profile.tsx          # User profile with error tracking demo
│   └── api/
│       ├── auth/
│       │   └── login.ts     # Login API with server-side tracking
│       └── burrito/
│           └── consider.ts  # Burrito API with server-side tracking
└── styles.css               # Global styles

vite.config.ts               # Vite config with PostHog proxy
.env                         # Environment variables
```

## Key integration points

### Client-side initialization (routes/__root.tsx)

PostHog is initialized using `PostHogProvider` from `@posthog/react`. The provider wraps the entire app in the root shell component and handles calling `posthog.init()` automatically:

```typescript
import { PostHogProvider } from '@posthog/react'

<PostHogProvider
  apiKey={import.meta.env.VITE_PUBLIC_POSTHOG_PROJECT_TOKEN!}
  options={{
    api_host: '/ingest',
    ui_host: import.meta.env.VITE_PUBLIC_POSTHOG_HOST || 'https://us.posthog.com',
    defaults: '2025-05-24',
    capture_exceptions: true,
    debug: import.meta.env.DEV,
  }}
>
  {children}
</PostHogProvider>
```

### Server-side setup (utils/posthog-server.ts)

For server-side tracking, we use the `posthog-node` SDK with a singleton pattern:

```typescript
import { PostHog } from 'posthog-node'

export function getPostHogClient() {
  if (!posthogClient) {
    posthogClient = new PostHog(
      process.env.VITE_PUBLIC_POSTHOG_PROJECT_TOKEN || import.meta.env.VITE_PUBLIC_POSTHOG_PROJECT_TOKEN!,
      {
        host: process.env.VITE_PUBLIC_POSTHOG_HOST || import.meta.env.VITE_PUBLIC_POSTHOG_HOST,
        flushAt: 1,
        flushInterval: 0,
      }
    )
  }
  return posthogClient
}
```

This client is used in API routes to track server-side events.

### Server-side capture (routes/api/*)

Server-side events include the client's `$session_id` so they appear in the same session in PostHog. The frontend sends it via a header:

```typescript
// Frontend: include session ID in API requests
await fetch('/api/burrito/consider', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-PostHog-Session-Id': posthog.get_session_id() ?? '',
  },
  body: JSON.stringify({ ... }),
})
```

```typescript
// Server: read session ID from header and include in capture
import { getPostHogClient } from '../../utils/posthog-server'

const sessionId = request.headers.get('X-PostHog-Session-Id')

const posthog = getPostHogClient()
posthog.capture({
  distinctId: username,
  event: 'burrito_considered',
  properties: {
    $session_id: sessionId || undefined,
    username: username,
    source: 'api',
  },
})
```

### Reverse proxy configuration

The Vite dev server is configured to proxy PostHog requests to avoid CORS issues and improve reliability:

```typescript
server: {
  proxy: {
    '/ingest': {
      target: 'https://us.i.posthog.com',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/ingest/, ''),
      secure: false,
    },
  },
}
```

### User identification (contexts/AuthContext.tsx)

```typescript
import { usePostHog } from '@posthog/react'

const posthog = usePostHog()

posthog.identify(username, {
  username: username,
})
```

### Event tracking (routes/burrito.tsx)

```typescript
import { usePostHog } from '@posthog/react'

const posthog = usePostHog()

posthog.capture('burrito_considered', {
  total_considerations: user.burritoConsiderations + 1,
  username: user.username,
})
```

### Error tracking (routes/profile.tsx)

```typescript
posthog.captureException(error)
```

## Learn more

- [PostHog documentation](https://posthog.com/docs)
- [TanStack Start documentation](https://tanstack.com/start)
- [TanStack Router documentation](https://tanstack.com/router)
- [PostHog React integration](https://posthog.com/docs/libraries/react)
- [PostHog Node.js integration](https://posthog.com/docs/libraries/node)

---

## .env.example

```example
VITE_PUBLIC_POSTHOG_PROJECT_TOKEN=<ph_project_token>
VITE_PUBLIC_POSTHOG_HOST=<ph_client_api_host>

```

---

## .prettierignore

```
package-lock.json
pnpm-lock.yaml
yarn.lock
```

---

## prettier.config.js

```js
//  @ts-check

/** @type {import('prettier').Config} */
const config = {
  semi: false,
  singleQuote: true,
  trailingComma: "all",
};

export default config;

```

---

## public/robots.txt

```txt
# https://www.robotstxt.org/robotstxt.html
User-agent: *
Disallow:

```

---

## src/components/Header.tsx

```tsx
import { Link } from '@tanstack/react-router'
import { useAuth } from '../contexts/AuthContext'

export default function Header() {
  const { user, logout } = useAuth()

  return (
    <header className="header">
      <div className="header-container">
        <nav>
          <Link to="/">Home</Link>
          {user && (
            <>
              <Link to="/burrito">Burrito Consideration</Link>
              <Link to="/profile">Profile</Link>
            </>
          )}
        </nav>
        <div className="user-section">
          {user ? (
            <>
              <span>Welcome, {user.username}!</span>
              <button onClick={logout} className="btn-logout">
                Logout
              </button>
            </>
          ) : (
            <span>Not logged in</span>
          )}
        </div>
      </div>
    </header>
  )
}

```

---

## src/contexts/AuthContext.tsx

```tsx
import {
  createContext,
  useContext,
  useState,
  ReactNode,
} from 'react'
import { usePostHog } from '@posthog/react'

interface User {
  username: string
  burritoConsiderations: number
}

interface AuthContextType {
  user: User | null
  login: (username: string, password: string) => Promise<boolean>
  logout: () => void
  incrementBurritoConsiderations: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

const users: Map<string, User> = new Map()

export function AuthProvider({ children }: { children: ReactNode }) {
  const posthog = usePostHog()

  // Use lazy initializer to read from localStorage only once on mount
  const [user, setUser] = useState<User | null>(() => {
    if (typeof window === 'undefined') return null

    const storedUsername = localStorage.getItem('currentUser')
    if (storedUsername) {
      const existingUser = users.get(storedUsername)
      if (existingUser) {
        return existingUser
      }
    }
    return null
  })

  const login = async (
    username: string,
    password: string,
  ): Promise<boolean> => {
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-PostHog-Session-Id': posthog.get_session_id() ?? '',
        },
        body: JSON.stringify({ username, password }),
      })

      if (response.ok) {
        const { user: userData } = await response.json()

        // Get or create user in local map
        let localUser = users.get(username)
        if (!localUser) {
          localUser = userData as User
          users.set(username, localUser)
        }

        setUser(localUser)
        if (typeof window !== 'undefined') {
          localStorage.setItem('currentUser', username)
        }

        // Identify user in PostHog using username as distinct ID
        posthog.identify(username, {
          username: username,
        })

        // Capture login event
        posthog.capture('user_logged_in', {
          username: username,
        })

        return true
      }
      return false
    } catch (error) {
      console.error('Login error:', error)
      return false
    }
  }

  const logout = () => {
    // Capture logout event before resetting
    posthog.capture('user_logged_out')
    posthog.reset()

    setUser(null)
    if (typeof window !== 'undefined') {
      localStorage.removeItem('currentUser')
    }
  }

  const incrementBurritoConsiderations = () => {
    if (user) {
      user.burritoConsiderations++
      users.set(user.username, user)
      setUser({ ...user })
    }
  }

  return (
    <AuthContext.Provider
      value={{ user, login, logout, incrementBurritoConsiderations }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

```

---

## src/router.tsx

```tsx
import { createRouter } from '@tanstack/react-router'

// Import the generated route tree
import { routeTree } from './routeTree.gen'

// Create a new router instance
export const getRouter = () => {
  return createRouter({
    routeTree,
    scrollRestoration: true,
    defaultPreloadStaleTime: 0,
  })
}

```

---

## src/routes/__root.tsx

```tsx
import { HeadContent, Scripts, createRootRoute } from '@tanstack/react-router'
import { TanStackRouterDevtoolsPanel } from '@tanstack/react-router-devtools'
import { TanStackDevtools } from '@tanstack/react-devtools'
import { PostHogProvider } from '@posthog/react'

import Header from '../components/Header'
import { AuthProvider } from '../contexts/AuthContext'

import appCss from '../styles.css?url'

export const Route = createRootRoute({
  head: () => ({
    meta: [
      {
        charSet: 'utf-8',
      },
      {
        name: 'viewport',
        content: 'width=device-width, initial-scale=1',
      },
      {
        title: 'TanStack Start Starter',
      },
    ],
    links: [
      {
        rel: 'stylesheet',
        href: appCss,
      },
    ],
  }),

  shellComponent: RootDocument,
})

function RootDocument({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <HeadContent />
      </head>
      <body>
        <PostHogProvider
          apiKey={import.meta.env.VITE_PUBLIC_POSTHOG_PROJECT_TOKEN!}
          options={{
            api_host: '/ingest',
            ui_host: import.meta.env.VITE_PUBLIC_POSTHOG_HOST || 'https://us.posthog.com',
            defaults: '2025-05-24',
            capture_exceptions: true,
            debug: import.meta.env.DEV,
          }}
        >
          <AuthProvider>
            <Header />
            {children}
          <TanStackDevtools
            config={{
              position: 'bottom-right',
            }}
            plugins={[
              {
                name: 'Tanstack Router',
                render: <TanStackRouterDevtoolsPanel />,
              },
            ]}
          />
          </AuthProvider>
        </PostHogProvider>
        <Scripts />
      </body>
    </html>
  )
}

```

---

## src/routes/api/auth/login.ts

```ts
import { createFileRoute } from '@tanstack/react-router'
import { json } from '@tanstack/react-start'
import { getPostHogClient } from '../../../utils/posthog-server'

export const Route = createFileRoute('/api/auth/login')({
  server: {
    handlers: {
      POST: async ({ request }) => {
        const body = await request.json()
        const { username, password } = body

        // Simple validation (in production, you'd verify against a real database)
        if (!username || !password) {
          return json(
            { error: 'Username and password required' },
            { status: 400 },
          )
        }

        // Check if this is a new user (simplified - in production use a database)
        const isNewUser = !username

        // Create or get user
        const user = {
          username,
          burritoConsiderations: 0,
        }

        const sessionId = request.headers.get('X-PostHog-Session-Id')

        // Capture server-side login event
        const posthog = getPostHogClient()
        posthog.capture({
          distinctId: username,
          event: 'server_login',
          properties: {
            $session_id: sessionId || undefined,
            username: username,
            isNewUser: isNewUser,
            source: 'api',
          },
        })

        // Identify user on server side
        posthog.identify({
          distinctId: username,
          properties: {
            username: username,
            createdAt: isNewUser ? new Date().toISOString() : undefined,
          },
        })

        return json({ success: true, user })
      },
    },
  },
})

```

---

## src/routes/api/burrito/consider.ts

```ts
import { createFileRoute } from '@tanstack/react-router'
import { json } from '@tanstack/react-start'
import { getPostHogClient } from '../../../utils/posthog-server'

export const Route = createFileRoute('/api/burrito/consider')({
  server: {
    handlers: {
      POST: async ({ request }) => {
        const body = await request.json()
        const { username, totalConsiderations } = body

        if (!username) {
          return json(
            { error: 'Username is required' },
            { status: 400 },
          )
        }

        const sessionId = request.headers.get('X-PostHog-Session-Id')

        const posthog = getPostHogClient()
        posthog.capture({
          distinctId: username,
          event: 'burrito_considered',
          properties: {
            $session_id: sessionId || undefined,
            total_considerations: totalConsiderations,
            username: username,
            source: 'api',
          },
        })

        return json({ success: true })
      },
    },
  },
})

```

---

## src/routes/burrito.tsx

```tsx
import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useState } from 'react'
import { usePostHog } from '@posthog/react'
import { useAuth } from '../contexts/AuthContext'

export const Route = createFileRoute('/burrito')({
  component: BurritoPage,
  head: () => ({
    meta: [
      {
        title: 'Burrito Consideration - Burrito Consideration App',
      },
      {
        name: 'description',
        content: 'Consider the potential of burritos',
      },
    ],
  }),
})

function BurritoPage() {
  const { user, incrementBurritoConsiderations } = useAuth()
  const navigate = useNavigate()
  const posthog = usePostHog()
  const [hasConsidered, setHasConsidered] = useState(false)

  // Redirect to home if not logged in
  if (!user) {
    navigate({ to: '/' })
    return null
  }

  const handleClientConsideration = () => {
    incrementBurritoConsiderations()
    setHasConsidered(true)
    setTimeout(() => setHasConsidered(false), 2000)

    posthog.capture('burrito_considered', {
      total_considerations: user.burritoConsiderations + 1,
      username: user.username,
    })
  }

  const handleServerConsideration = async () => {
    incrementBurritoConsiderations()
    setHasConsidered(true)
    setTimeout(() => setHasConsidered(false), 2000)

    await fetch('/api/burrito/consider', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-PostHog-Session-Id': posthog.get_session_id() ?? '',
      },
      body: JSON.stringify({
        username: user.username,
        totalConsiderations: user.burritoConsiderations + 1,
      }),
    })
  }

  return (
    <main>
      <div className="container">
        <h1>Burrito consideration zone</h1>
        <p>Take a moment to truly consider the potential of burritos.</p>

        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.125rem' }}>
          <button
            onClick={handleClientConsideration}
            className="btn-burrito"
            style={{ backgroundColor: '#e07c24', color: '#fff' }}
          >
            Consider burrito (client)
          </button>
          <button
            onClick={handleServerConsideration}
            className="btn-burrito"
            style={{ backgroundColor: '#4a90d9', color: '#fff' }}
          >
            Consider burrito (server)
          </button>

          {hasConsidered && (
            <p className="success">
              Thank you for your consideration! Count:{' '}
              {user.burritoConsiderations}
            </p>
          )}
        </div>

        <div className="stats">
          <h3>Consideration stats</h3>
          <p>Total considerations: {user.burritoConsiderations}</p>
        </div>
      </div>
    </main>
  )
}

```

---

## src/routes/index.tsx

```tsx
import { createFileRoute } from '@tanstack/react-router'
import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'

export const Route = createFileRoute('/')({
  component: Home,
  head: () => ({
    meta: [
      {
        title: 'Burrito Consideration App',
      },
      {
        name: 'description',
        content: 'Consider the potential of burritos',
      },
    ],
  }),
})

function Home() {
  const { user, login } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    try {
      const success = await login(username, password)
      if (success) {
        setUsername('')
        setPassword('')
      } else {
        setError('Please provide both username and password')
      }
    } catch (err) {
      console.error('Login failed:', err)
      setError('An error occurred during login')
    }
  }

  return (
    <main>
      {user ? (
        <div className="container">
          <h1>Welcome back, {user.username}!</h1>
          <p>You are now logged in. Feel free to explore:</p>
          <ul>
            <li>Consider the potential of burritos</li>
            <li>View your profile and statistics</li>
          </ul>
        </div>
      ) : (
        <div className="container">
          <h1>Welcome to Burrito Consideration App</h1>
          <p>Please sign in to begin your burrito journey</p>

          <form onSubmit={handleSubmit} className="form">
            <div className="form-group">
              <label htmlFor="username">Username:</label>
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter any username"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password:</label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter any password"
              />
            </div>

            {error && <p className="error">{error}</p>}

            <button type="submit" className="btn-primary">
              Sign In
            </button>
          </form>

          <p className="note">
            Note: This is a demo app. Use any username and password to sign in.
          </p>
        </div>
      )}
    </main>
  )
}

```

---

## src/routes/profile.tsx

```tsx
import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { usePostHog } from '@posthog/react'
import { useAuth } from '../contexts/AuthContext'

export const Route = createFileRoute('/profile')({
  component: ProfilePage,
  head: () => ({
    meta: [
      {
        title: 'Profile - Burrito Consideration App',
      },
      {
        name: 'description',
        content: 'Your burrito consideration profile',
      },
    ],
  }),
})

function ProfilePage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const posthog = usePostHog()

  // Redirect to home if not logged in
  if (!user) {
    navigate({ to: '/' })
    return null
  }

  const triggerTestError = () => {
    try {
      throw new Error('Test error for PostHog error tracking')
    } catch (err) {
      posthog.captureException(err)
      console.error('Captured error:', err)
      alert('Error captured and sent to PostHog!')
    }
  }

  return (
    <main>
      <div className="container">
        <h1>User Profile</h1>

        <div className="stats">
          <h2>Your Information</h2>
          <p>
            <strong>Username:</strong> {user.username}
          </p>
          <p>
            <strong>Burrito Considerations:</strong>{' '}
            {user.burritoConsiderations}
          </p>
        </div>

        <div style={{ marginTop: '2rem' }}>
          <button
            onClick={triggerTestError}
            className="btn-primary"
            style={{ backgroundColor: '#dc3545' }}
          >
            Trigger Test Error (for PostHog)
          </button>
        </div>

        <div style={{ marginTop: '2rem' }}>
          <h3>Your Burrito Journey</h3>
          {user.burritoConsiderations === 0 ? (
            <p>
              You haven't considered any burritos yet. Visit the Burrito
              Consideration page to start!
            </p>
          ) : user.burritoConsiderations === 1 ? (
            <p>You've considered the burrito potential once. Keep going!</p>
          ) : user.burritoConsiderations < 5 ? (
            <p>You're getting the hang of burrito consideration!</p>
          ) : user.burritoConsiderations < 10 ? (
            <p>You're becoming a burrito consideration expert!</p>
          ) : (
            <p>You are a true burrito consideration master! 🌯</p>
          )}
        </div>
      </div>
    </main>
  )
}

```

---

## src/routeTree.gen.ts

```ts
/* eslint-disable */

// @ts-nocheck

// noinspection JSUnusedGlobalSymbols

// This file was automatically generated by TanStack Router.
// You should NOT make any changes in this file as it will be overwritten.
// Additionally, you should also exclude this file from your linter and/or formatter to prevent it from being checked or modified.

import { Route as rootRouteImport } from './routes/__root'
import { Route as ProfileRouteImport } from './routes/profile'
import { Route as BurritoRouteImport } from './routes/burrito'
import { Route as IndexRouteImport } from './routes/index'
import { Route as ApiBurritoConsiderRouteImport } from './routes/api/burrito/consider'
import { Route as ApiAuthLoginRouteImport } from './routes/api/auth/login'

const ProfileRoute = ProfileRouteImport.update({
  id: '/profile',
  path: '/profile',
  getParentRoute: () => rootRouteImport,
} as any)
const BurritoRoute = BurritoRouteImport.update({
  id: '/burrito',
  path: '/burrito',
  getParentRoute: () => rootRouteImport,
} as any)
const IndexRoute = IndexRouteImport.update({
  id: '/',
  path: '/',
  getParentRoute: () => rootRouteImport,
} as any)
const ApiBurritoConsiderRoute = ApiBurritoConsiderRouteImport.update({
  id: '/api/burrito/consider',
  path: '/api/burrito/consider',
  getParentRoute: () => rootRouteImport,
} as any)
const ApiAuthLoginRoute = ApiAuthLoginRouteImport.update({
  id: '/api/auth/login',
  path: '/api/auth/login',
  getParentRoute: () => rootRouteImport,
} as any)

export interface FileRoutesByFullPath {
  '/': typeof IndexRoute
  '/burrito': typeof BurritoRoute
  '/profile': typeof ProfileRoute
  '/api/auth/login': typeof ApiAuthLoginRoute
  '/api/burrito/consider': typeof ApiBurritoConsiderRoute
}
export interface FileRoutesByTo {
  '/': typeof IndexRoute
  '/burrito': typeof BurritoRoute
  '/profile': typeof ProfileRoute
  '/api/auth/login': typeof ApiAuthLoginRoute
  '/api/burrito/consider': typeof ApiBurritoConsiderRoute
}
export interface FileRoutesById {
  __root__: typeof rootRouteImport
  '/': typeof IndexRoute
  '/burrito': typeof BurritoRoute
  '/profile': typeof ProfileRoute
  '/api/auth/login': typeof ApiAuthLoginRoute
  '/api/burrito/consider': typeof ApiBurritoConsiderRoute
}
export interface FileRouteTypes {
  fileRoutesByFullPath: FileRoutesByFullPath
  fullPaths:
    | '/'
    | '/burrito'
    | '/profile'
    | '/api/auth/login'
    | '/api/burrito/consider'
  fileRoutesByTo: FileRoutesByTo
  to:
    | '/'
    | '/burrito'
    | '/profile'
    | '/api/auth/login'
    | '/api/burrito/consider'
  id:
    | '__root__'
    | '/'
    | '/burrito'
    | '/profile'
    | '/api/auth/login'
    | '/api/burrito/consider'
  fileRoutesById: FileRoutesById
}
export interface RootRouteChildren {
  IndexRoute: typeof IndexRoute
  BurritoRoute: typeof BurritoRoute
  ProfileRoute: typeof ProfileRoute
  ApiAuthLoginRoute: typeof ApiAuthLoginRoute
  ApiBurritoConsiderRoute: typeof ApiBurritoConsiderRoute
}

declare module '@tanstack/react-router' {
  interface FileRoutesByPath {
    '/profile': {
      id: '/profile'
      path: '/profile'
      fullPath: '/profile'
      preLoaderRoute: typeof ProfileRouteImport
      parentRoute: typeof rootRouteImport
    }
    '/burrito': {
      id: '/burrito'
      path: '/burrito'
      fullPath: '/burrito'
      preLoaderRoute: typeof BurritoRouteImport
      parentRoute: typeof rootRouteImport
    }
    '/': {
      id: '/'
      path: '/'
      fullPath: '/'
      preLoaderRoute: typeof IndexRouteImport
      parentRoute: typeof rootRouteImport
    }
    '/api/burrito/consider': {
      id: '/api/burrito/consider'
      path: '/api/burrito/consider'
      fullPath: '/api/burrito/consider'
      preLoaderRoute: typeof ApiBurritoConsiderRouteImport
      parentRoute: typeof rootRouteImport
    }
    '/api/auth/login': {
      id: '/api/auth/login'
      path: '/api/auth/login'
      fullPath: '/api/auth/login'
      preLoaderRoute: typeof ApiAuthLoginRouteImport
      parentRoute: typeof rootRouteImport
    }
  }
}

const rootRouteChildren: RootRouteChildren = {
  IndexRoute: IndexRoute,
  BurritoRoute: BurritoRoute,
  ProfileRoute: ProfileRoute,
  ApiAuthLoginRoute: ApiAuthLoginRoute,
  ApiBurritoConsiderRoute: ApiBurritoConsiderRoute,
}
export const routeTree = rootRouteImport
  ._addFileChildren(rootRouteChildren)
  ._addFileTypes<FileRouteTypes>()

import type { getRouter } from './router.tsx'
import type { createStart } from '@tanstack/react-start'
declare module '@tanstack/react-start' {
  interface Register {
    ssr: true
    router: Awaited<ReturnType<typeof getRouter>>
  }
}

```

---

## src/utils/posthog-server.ts

```ts
import { PostHog } from 'posthog-node'

let posthogClient: PostHog | null = null

export function getPostHogClient() {
  if (!posthogClient) {
    posthogClient = new PostHog(
      process.env.VITE_PUBLIC_POSTHOG_PROJECT_TOKEN || import.meta.env.VITE_PUBLIC_POSTHOG_PROJECT_TOKEN!,
      {
        host: process.env.VITE_PUBLIC_POSTHOG_HOST || import.meta.env.VITE_PUBLIC_POSTHOG_HOST,
        flushAt: 1,
        flushInterval: 0,
      },
    )
  }
  return posthogClient
}


```

---

## vite.config.ts

```ts
import { defineConfig } from 'vite'
import { tanstackStart } from '@tanstack/react-start/plugin/vite'
import viteReact from '@vitejs/plugin-react'
import viteTsConfigPaths from 'vite-tsconfig-paths'

const config = defineConfig({
  plugins: [
    // this is the plugin that enables path aliases
    viteTsConfigPaths({
      projects: ['./tsconfig.json'],
    }),
    tanstackStart(),
    viteReact(),
  ],
  server: {
    proxy: {
      '/ingest/static': {
        target: 'https://us-assets.i.posthog.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/ingest/, ''),
        secure: false,
      },
      '/ingest/array': {
        target: 'https://us-assets.i.posthog.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/ingest/, ''),
        secure: false,
      },
      '/ingest': {
        target: 'https://us.i.posthog.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/ingest/, ''),
        secure: false,
      },
    },
  },
})

export default config

```

---

