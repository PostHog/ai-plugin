# PostHog react-tanstack-router-file-based Example Project

Repository: https://github.com/PostHog/context-mill
Path: basics/react-tanstack-router-file-based

---

## README.md

# PostHog TanStack Router Example

This is a React and [TanStack Router](https://tanstack.com/router) example demonstrating PostHog integration with product analytics, session replay, and error tracking.

## Features

- **Product analytics**: Track user events and behaviors
- **Session replay**: Record and replay user sessions
- **Error tracking**: Capture and track errors
- **User authentication**: Demo login system with PostHog user identification
- **Client-side tracking**: Pure client-side React implementation
- **Reverse proxy**: PostHog ingestion through Vite proxy

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
│   └── Header.tsx         # Navigation header with auth state
├── contexts/
│   └── AuthContext.tsx    # Authentication context with PostHog integration
├── routes/
│   ├── __root.tsx         # Root layout with PostHogProvider
│   ├── index.tsx          # Home/Login page
│   ├── burrito.tsx        # Demo feature page with event tracking
│   └── profile.tsx        # User profile with error tracking demo
├── main.tsx               # App entry point
└── styles.css             # Global styles
```

## Key integration points

### PostHog provider setup (routes/__root.tsx)

PostHog is initialized using `PostHogProvider` from `@posthog/react`. The provider wraps the entire app and handles calling `posthog.init()` automatically:

```typescript
import { PostHogProvider } from '@posthog/react'

export const Route = createRootRoute({
  component: () => (
    <PostHogProvider
      apiKey={import.meta.env.VITE_PUBLIC_POSTHOG_PROJECT_TOKEN!}
      options={{
        api_host: '/ingest',
        ui_host: import.meta.env.VITE_PUBLIC_POSTHOG_HOST || 'https://us.posthog.com',
        defaults: '2026-01-30',
        capture_exceptions: true,
        debug: import.meta.env.DEV,
      }}
    >
      {/* your app */}
    </PostHogProvider>
  ),
})
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
  total_considerations: count,
  username: username,
})
```

### Error tracking (routes/profile.tsx)

```typescript
posthog.captureException(error)
```


## TanStack Router details

This example uses TanStack Router. Key details:

1. **Client-side only**: No server-side logic, no API routes, no posthog-node
2. **File-based routing**: Routes are files in `src/routes` directory
3. **Standard hooks**: Uses `useNavigate()` from @tanstack/react-router
4. **Vite proxy**: Uses Vite's proxy config for PostHog calls
5. **Environment variables**: Uses `import.meta.env.VITE_*`
6. **PostHog provider**: Uses `PostHogProvider` from `@posthog/react` in root route

## Learn more

- [PostHog Documentation](https://posthog.com/docs)
- [TanStack Router Documentation](https://tanstack.com/router)
- [PostHog React Integration Guide](https://posthog.com/docs/libraries/react)

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

## index.html

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="icon" href="/favicon.ico" />
    <meta name="theme-color" content="#000000" />
    <meta
      name="description"
      content="Web site created using create-tsrouter-app"
    />
    <link rel="apple-touch-icon" href="/logo192.png" />
    <link rel="manifest" href="/manifest.json" />
    <title>Create TanStack App - react-tanstack</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>

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
import { createContext, useContext, useState, type ReactNode } from 'react';
import { usePostHog } from '@posthog/react';

interface User {
  username: string;
  burritoConsiderations: number;
}

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  incrementBurritoConsiderations: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const users: Map<string, User> = new Map();

export function AuthProvider({ children }: { children: ReactNode }) {
  // Use lazy initializer to read from localStorage only once on mount
  const [user, setUser] = useState<User | null>(() => {
    if (typeof window === 'undefined') return null;

    const storedUsername = localStorage.getItem('currentUser');
    if (storedUsername) {
      const existingUser = users.get(storedUsername);
      if (existingUser) {
        return existingUser;
      }
    }
    return null;
  });
  const posthog = usePostHog();

  const login = async (username: string, password: string): Promise<boolean> => {
    if (!username || !password) {
      return false;
    }

    // Get or create user in local map
    let user = users.get(username);
    const isNewUser = !user;

    if (!user) {
      user = { username, burritoConsiderations: 0 };
      users.set(username, user);
    }

    setUser(user);
    localStorage.setItem('currentUser', username);

    // Identify user in PostHog using username as distinct ID
    posthog.identify(username, {
      username: username,
      isNewUser: isNewUser,
    });

    // Capture login event
    posthog.capture('user_logged_in', {
      username: username,
      isNewUser: isNewUser,
    });

    return true;
  };

  const logout = () => {
    // Capture logout event before resetting
    posthog.capture('user_logged_out');
    posthog.reset();

    setUser(null);
    localStorage.removeItem('currentUser');
  };

  const incrementBurritoConsiderations = () => {
    if (user) {
      user.burritoConsiderations++;
      users.set(user.username, user);
      setUser({ ...user });
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, incrementBurritoConsiderations }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

```

---

## src/main.tsx

```tsx
import { StrictMode } from 'react'
import ReactDOM from 'react-dom/client'
import { RouterProvider, createRouter } from '@tanstack/react-router'

// Import the generated route tree
import { routeTree } from './routeTree.gen.ts'

import './styles.css'
import reportWebVitals from './reportWebVitals.ts'

// Create a new router instance
const router = createRouter({
  routeTree,
  context: {},
  defaultPreload: 'intent',
  scrollRestoration: true,
  defaultStructuralSharing: true,
  defaultPreloadStaleTime: 0,
})

// Register the router instance for type safety
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}

// Render the app
const rootElement = document.getElementById('app')
if (rootElement && !rootElement.innerHTML) {
  const root = ReactDOM.createRoot(rootElement)
  root.render(
    <StrictMode>
      <RouterProvider router={router} />
    </StrictMode>,
  )
}

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals()

```

---

## src/reportWebVitals.ts

```ts
const reportWebVitals = (onPerfEntry?: () => void) => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then(({ onCLS, onINP, onFCP, onLCP, onTTFB }) => {
      onCLS(onPerfEntry)
      onINP(onPerfEntry)
      onFCP(onPerfEntry)
      onLCP(onPerfEntry)
      onTTFB(onPerfEntry)
    })
  }
}

export default reportWebVitals

```

---

## src/routes/__root.tsx

```tsx
import { Outlet, createRootRoute } from '@tanstack/react-router'
import { TanStackRouterDevtoolsPanel } from '@tanstack/react-router-devtools'
import { TanStackDevtools } from '@tanstack/react-devtools'
import { PostHogProvider } from '@posthog/react'

import Header from '../components/Header'
import { AuthProvider } from '../contexts/AuthContext'

export const Route = createRootRoute({
  component: () => (
    <PostHogProvider
      apiKey={import.meta.env.VITE_PUBLIC_POSTHOG_PROJECT_TOKEN!}
      options={{
        api_host: '/ingest',
        ui_host: import.meta.env.VITE_PUBLIC_POSTHOG_HOST || 'https://us.posthog.com',
        defaults: '2026-01-30',
        capture_exceptions: true,
        debug: import.meta.env.DEV,
      }}
    >
      <AuthProvider>
        <Header />
        <main>
          <Outlet />
        </main>
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
  ),
})

```

---

## src/routes/burrito.tsx

```tsx
import { useState } from 'react'
import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { usePostHog } from '@posthog/react'
import { useAuth } from '../contexts/AuthContext'

export const Route = createFileRoute('/burrito')({
  component: BurritoPage,
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

  const handleConsideration = () => {
    incrementBurritoConsiderations()
    setHasConsidered(true)
    setTimeout(() => setHasConsidered(false), 2000)

    // Capture burrito consideration event
    console.log('posthog', posthog)
    posthog.capture('burrito_considered', {
      total_considerations: user.burritoConsiderations + 1,
      username: user.username,
    })
  }

  return (
    <div className="container">
      <h1>Burrito consideration zone</h1>
      <p>Take a moment to truly consider the potential of burritos.</p>

      <div style={{ textAlign: 'center' }}>
        <button onClick={handleConsideration} className="btn-burrito">
          I have considered the burrito potential
        </button>

        {hasConsidered && (
          <p className="success">
            Thank you for your consideration! Count: {user.burritoConsiderations}
          </p>
        )}
      </div>

      <div className="stats">
        <h3>Consideration stats</h3>
        <p>Total considerations: {user.burritoConsiderations}</p>
      </div>
    </div>
  )
}

```

---

## src/routes/index.tsx

```tsx
import { useState } from 'react'
import { createFileRoute } from '@tanstack/react-router'
import { useAuth } from '../contexts/AuthContext'

export const Route = createFileRoute('/')({
  component: Home,
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

  if (user) {
    return (
      <div className="container">
        <h1>Welcome back, {user.username}!</h1>
        <p>You are now logged in. Feel free to explore:</p>
        <ul>
          <li>Consider the potential of burritos</li>
          <li>View your profile and statistics</li>
        </ul>
      </div>
    )
  }

  return (
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
  )
}

```

---

## src/routes/profile.tsx

```tsx
import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { usePostHog } from 'posthog-js/react'
import { useAuth } from '../contexts/AuthContext'

export const Route = createFileRoute('/profile')({
  component: ProfilePage,
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
    <div className="container">
      <h1>User Profile</h1>

      <div className="stats">
        <h2>Your Information</h2>
        <p>
          <strong>Username:</strong> {user.username}
        </p>
        <p>
          <strong>Burrito Considerations:</strong> {user.burritoConsiderations}
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
          <p>You haven't considered any burritos yet. Visit the Burrito Consideration page to start!</p>
        ) : user.burritoConsiderations === 1 ? (
          <p>You've considered the burrito potential once. Keep going!</p>
        ) : user.burritoConsiderations < 5 ? (
          <p>You're getting the hang of burrito consideration!</p>
        ) : user.burritoConsiderations < 10 ? (
          <p>You're becoming a burrito consideration expert!</p>
        ) : (
          <p>You are a true burrito consideration master!</p>
        )}
      </div>
    </div>
  )
}

```

---

## vite.config.ts

```ts
import { defineConfig, loadEnv } from 'vite'
import viteReact from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

import { tanstackRouter } from '@tanstack/router-plugin/vite'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [
      tanstackRouter({
        target: 'react',
        autoCodeSplitting: true,
      }),
      viteReact(),
      tailwindcss(),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    server: {
      proxy: {
        '/ingest/static': {
          target: 'https://us-assets.i.posthog.com',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/ingest/, ''),
        },
        '/ingest/array': {
          target: 'https://us-assets.i.posthog.com',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/ingest/, ''),
        },
        '/ingest': {
          target: env.VITE_PUBLIC_POSTHOG_HOST || 'https://us.i.posthog.com',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/ingest/, ''),
        },
      },
    },
  }
})

```

---

