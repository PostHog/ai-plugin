# PostHog react-react-router-7-framework Example Project

Repository: https://github.com/PostHog/context-mill
Path: basics/react-react-router-7-framework

---

## README.md

# PostHog React Router 7 Framework example

This is a [React Router 7](https://reactrouter.com) Framework example demonstrating PostHog integration with product analytics, session replay, feature flags, and error tracking.

## Features

- **Product Analytics**: Track user events and behaviors
- **Session Replay**: Record and replay user sessions
- **Error Tracking**: Capture and track errors
- **User Authentication**: Demo login system with PostHog user identification
- **Server-side & Client-side Tracking**: Examples of both tracking methods
- **SSR Support**: Server-side rendering with React Router 7 Framework

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
VITE_PUBLIC_POSTHOG_PROJECT_TOKEN=your_posthog_project_token
VITE_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com
```

Get your PostHog project token from your [PostHog project settings](https://app.posthog.com/project/settings).

### 3. Run the Development Server

```bash
npm run dev
# or
pnpm dev
```

Open [http://localhost:5173](http://localhost:5173) with your browser to see the app.

## Project Structure

```
app/
├── components/
│   └── Header.tsx           # Navigation header with auth state
├── contexts/
│   └── AuthContext.tsx      # Authentication context
├── lib/
│   ├── posthog-middleware.ts # Server-side PostHog middleware
│   └── db.ts                # Database utilities
├── routes/
│   ├── home.tsx             # Home/Login page
│   ├── burrito.tsx          # Demo feature page with event tracking
│   ├── profile.tsx          # User profile with error tracking demo
│   ├── api.auth.login.ts    # Login API with server-side tracking
│   └── api.burrito.consider.ts # Burrito API with server-side tracking
├── entry.client.tsx         # Client entry with PostHog initialization
├── entry.server.tsx         # Server entry
└── root.tsx                 # Root route with error boundary
```

## Key Integration Points

### Client-side initialization (entry.client.tsx)

```typescript
import posthog from 'posthog-js';
import { PostHogProvider } from '@posthog/react'

posthog.init(import.meta.env.VITE_PUBLIC_POSTHOG_PROJECT_TOKEN, {
  api_host: import.meta.env.VITE_PUBLIC_POSTHOG_HOST,
  defaults: '2026-01-30',
  __add_tracing_headers: [ window.location.host, 'localhost' ],
});

<PostHogProvider client={posthog}>
  <HydratedRouter />
</PostHogProvider>
```

### User identification (home.tsx)

The user is identified when the user logs in on the **client-side**.

```typescript
posthog?.identify(username, {
  username: username,
});
posthog?.capture('user_logged_in', {
  username: username,
});
```

The session and distinct ID are automatically passed to the backend via the `X-POSTHOG-SESSION-ID` and `X-POSTHOG-DISTINCT-ID` headers because we set the `__add_tracing_headers` option in the PostHog initialization.

**Important**: do not identify users on the server-side.

### Server-side middleware (posthog-middleware.ts)

The PostHog middleware creates a server-side PostHog client for each request and extracts session and user context from request headers:

```typescript
export const posthogMiddleware: Route.MiddlewareFunction = async ({ request, context }, next) => {
  const posthog = new PostHog(process.env.VITE_PUBLIC_POSTHOG_PROJECT_TOKEN!, {
    host: process.env.VITE_PUBLIC_POSTHOG_HOST!,
    flushAt: 1,
    flushInterval: 0,
  });

  const sessionId = request.headers.get('X-POSTHOG-SESSION-ID');
  const distinctId = request.headers.get('X-POSTHOG-DISTINCT-ID');

  context.posthog = posthog;

  const response = await posthog.withContext(
    { sessionId: sessionId ?? undefined, distinctId: distinctId ?? undefined },
    next
  );

  await posthog.shutdown().catch(() => {});
  return response;
};
```

**Key Points:**
- Creates a new PostHog Node client for each request
- Extracts `sessionId` and `distinctId` from request headers (automatically set by the client-side SDK)
- Sets the PostHog client on the request context for use in route handlers
- Uses `withContext()` to associate server-side events with the correct session/user
- Properly shuts down the client after each request

### Event tracking (burrito.tsx)

```typescript
posthog?.capture('burrito_considered', {
  total_considerations: count,
  username: username,
});
```

### Error tracking (root.tsx, profile.tsx)

Errors are captured in two ways:

1. **Error boundary** - The `ErrorBoundary` in `root.tsx` automatically captures unhandled React Router errors:
```typescript
export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  const posthog = usePostHog();
  posthog.captureException(error);
  // ... error UI
}
```

2. **Manual error capture** in components (profile.tsx):
```typescript
posthog.captureException(err);
```

### Server-side tracking (api.auth.login.ts, api.burrito.consider.ts)

Server-side events use the PostHog client from the request context (set by the middleware):

```typescript
const posthog = (context as any).posthog as PostHog | undefined;
if (posthog) {
  posthog.capture({ event: 'server_login' });
}
```

**Key Points:**
- The PostHog client is available via `context.posthog` (set by the middleware)
- Events are automatically associated with the correct user/session via the middleware's `withContext()` call
- The `distinctId` and `sessionId` are extracted from request headers and used to maintain context between client and server

## Learn More

- [PostHog Documentation](https://posthog.com/docs)
- [React Router 7 Documentation](https://reactrouter.com)
- [PostHog React Integration Guide](https://posthog.com/docs/libraries/react)

---

## .env.example

```example
VITE_PUBLIC_POSTHOG_PROJECT_TOKEN=
VITE_PUBLIC_POSTHOG_HOST=
PROJECT_ID=
```

---

## app/components/Header.tsx

```tsx
import { Link } from 'react-router';
import { useAuth } from '../contexts/AuthContext';
import { usePostHog } from '@posthog/react';

export default function Header() {
  const { user, logout } = useAuth();
  const posthog = usePostHog();

  const handleLogout = () => {
    posthog?.capture('user_logged_out');
    posthog?.reset();
    logout();
  };

  return (
    <header className="header">
      <div className="header-container">
        <nav>
          <Link to="/">Home</Link>
          {user && (
            <>
              <Link to="/burrito">Burrito Consideration</Link>
              <Link to="/profile">Profile</Link>
              <Link to="/error">Error</Link>
            </>
          )}
        </nav>
        <div className="user-section">
          {user ? (
            <>
              <span>Welcome, {user.username}!</span>
              <button onClick={handleLogout} className="btn-logout">
                Logout
              </button>
            </>
          ) : (
            <span>Not logged in</span>
          )}
        </div>
      </div>
    </header>
  );
}


```

---

## app/contexts/AuthContext.tsx

```tsx
import { createContext, useContext, useState, type ReactNode } from 'react';

interface User {
  username: string;
  burritoConsiderations: number;
}

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  incrementBurritoConsiderations: () => void;
  setUser: (user: User) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const users: Map<string, User> = new Map();

export function AuthProvider({ children }: { children: ReactNode }) {
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

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      if (response.ok) {
        const { user: userData } = await response.json();

        let localUser = users.get(username);
        if (!localUser) {
          localUser = userData as User;
          users.set(username, localUser);
        }

        setUser(localUser);
        localStorage.setItem('currentUser', username);
        
        return true;
      }
      return false;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const logout = () => {
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

  const setUserState = (newUser: User) => {
    setUser(newUser);
    users.set(newUser.username, newUser);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, incrementBurritoConsiderations, setUser: setUserState }}>
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

## app/entry.client.tsx

```tsx
import { startTransition, StrictMode } from "react";
import { hydrateRoot } from "react-dom/client";
import { HydratedRouter } from "react-router/dom";

import posthog from 'posthog-js';
import { PostHogProvider } from '@posthog/react'

posthog.init(import.meta.env.VITE_PUBLIC_POSTHOG_PROJECT_TOKEN, {
  api_host: import.meta.env.VITE_PUBLIC_POSTHOG_HOST,
  defaults: '2026-01-30',
  __add_tracing_headers: [ window.location.host, 'localhost' ],
});


startTransition(() => {
  hydrateRoot(
    document,
    <PostHogProvider client={posthog}>
      <StrictMode>
        <HydratedRouter />
      </StrictMode>
    </PostHogProvider>,
  );
});

```

---

## app/entry.server.tsx

```tsx
import { PassThrough } from "node:stream";

import type { EntryContext, RouterContextProvider } from "react-router";
import { createReadableStreamFromReadable } from "@react-router/node";
import { ServerRouter } from "react-router";
import { isbot } from "isbot";
import type { RenderToPipeableStreamOptions } from "react-dom/server";
import { renderToPipeableStream } from "react-dom/server";

export const streamTimeout = 5_000;

export default function handleRequest(
  request: Request,
  responseStatusCode: number,
  responseHeaders: Headers,
  routerContext: EntryContext,
  loadContext: RouterContextProvider,
) {
  // https://httpwg.org/specs/rfc9110.html#HEAD
  if (request.method.toUpperCase() === "HEAD") {
    return new Response(null, {
      status: responseStatusCode,
      headers: responseHeaders,
    });
  }

  return new Promise((resolve, reject) => {
    let shellRendered = false;
    let userAgent = request.headers.get("user-agent");

    // Ensure requests from bots and SPA Mode renders wait for all content to load before responding
    // https://react.dev/reference/react-dom/server/renderToPipeableStream#waiting-for-all-content-to-load-for-crawlers-and-static-generation
    let readyOption: keyof RenderToPipeableStreamOptions =
      (userAgent && isbot(userAgent)) || routerContext.isSpaMode
        ? "onAllReady"
        : "onShellReady";

    // Abort the rendering stream after the `streamTimeout` so it has time to
    // flush down the rejected boundaries
    let timeoutId: ReturnType<typeof setTimeout> | undefined = setTimeout(
      () => abort(),
      streamTimeout + 1000,
    );

    const { pipe, abort } = renderToPipeableStream(
      <ServerRouter context={routerContext} url={request.url} />,
      {
        [readyOption]() {
          shellRendered = true;
          const body = new PassThrough({
            final(callback) {
              // Clear the timeout to prevent retaining the closure and memory leak
              clearTimeout(timeoutId);
              timeoutId = undefined;
              callback();
            },
          });
          const stream = createReadableStreamFromReadable(body);

          responseHeaders.set("Content-Type", "text/html");

          pipe(body);

          resolve(
            new Response(stream, {
              headers: responseHeaders,
              status: responseStatusCode,
            }),
          );
        },
        onShellError(error: unknown) {
          reject(error);
        },
        onError(error: unknown) {
          responseStatusCode = 500;
          // Log streaming rendering errors from inside the shell.  Don't log
          // errors encountered during initial shell rendering since they'll
          // reject and get logged in handleDocumentRequest.
          if (shellRendered) {
            console.error(error);
          }
        },
      },
    );
  });
}

```

---

## app/lib/db.ts

```ts
import sqlite3 from "sqlite3";
import { join } from "node:path";
import { promisify } from "node:util";

const dbPath = join(process.cwd(), "burrito-considerations.db");

const db = new sqlite3.Database(dbPath);

// Initialize schema
db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS burrito_considerations (
      username TEXT PRIMARY KEY,
      count INTEGER NOT NULL DEFAULT 0
    )
  `);
});

const dbGet = promisify(db.get.bind(db));
const dbRun = promisify(db.run.bind(db));

export function getBurritoConsiderations(username: string): Promise<number> {
  return dbGet("SELECT count FROM burrito_considerations WHERE username = ?", [username])
    .then((row: any) => row?.count ?? 0);
}

export function incrementBurritoConsiderations(username: string): Promise<number> {
  return dbRun(`
    INSERT INTO burrito_considerations (username, count)
    VALUES (?, 1)
    ON CONFLICT(username) DO UPDATE SET count = count + 1
  `, [username])
    .then(() => {
      return dbGet("SELECT count FROM burrito_considerations WHERE username = ?", [username]);
    })
    .then((row: any) => row.count);
}

```

---

## app/lib/posthog-middleware.ts

```ts
import { PostHog } from "posthog-node";
import type { RouterContextProvider } from "react-router";
import type { Route } from "../+types/root";

export interface PostHogContext extends RouterContextProvider {
  posthog?: PostHog;
}

export const posthogMiddleware: Route.MiddlewareFunction = async ({ request, context }, next) => {
  const posthog = new PostHog(process.env.VITE_PUBLIC_POSTHOG_PROJECT_TOKEN!, {
    host: process.env.VITE_PUBLIC_POSTHOG_HOST!,
    flushAt: 1,
    flushInterval: 0,
  });

  const sessionId = request.headers.get('X-POSTHOG-SESSION-ID');
  const distinctId = request.headers.get('X-POSTHOG-DISTINCT-ID');

  (context as PostHogContext).posthog = posthog;

  const response = await posthog.withContext(
    { sessionId: sessionId ?? undefined, distinctId: distinctId ?? undefined },
    next
  );

  await posthog.shutdown().catch(() => {});

  return response;
};


```

---

## app/root.tsx

```tsx
import { usePostHog } from '@posthog/react';
import {
  isRouteErrorResponse,
  Links,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
} from "react-router";

import type { Route } from "./+types/root";
import "./app.css";
import "./globals.css";
import Header from "./components/Header";
import { AuthProvider } from "./contexts/AuthContext";
import { posthogMiddleware } from "./lib/posthog-middleware";

export const middleware: Route.MiddlewareFunction[] = [
  posthogMiddleware,
];

export const links: Route.LinksFunction = () => [
  { rel: "preconnect", href: "https://fonts.googleapis.com" },
  {
    rel: "preconnect",
    href: "https://fonts.gstatic.com",
    crossOrigin: "anonymous",
  },
  {
    rel: "stylesheet",
    href: "https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap",
  },
];

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <Meta />
        <Links />
      </head>
      <body>
        {children}
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Header />
      <main>
        <Outlet />
      </main>
    </AuthProvider>
  );
}

export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  let message = "Oops!";
  let details = "An unexpected error occurred.";
  let stack: string | undefined;

  const posthog = usePostHog();
  posthog.captureException(error);

  if (isRouteErrorResponse(error)) {
    message = error.status === 404 ? "404" : "Error";
    details =
      error.status === 404
        ? "The requested page could not be found."
        : error.statusText || details;
  } else if (import.meta.env.DEV && error && error instanceof Error) {
    details = error.message;
    stack = error.stack;
  }

  return (
    <main className="pt-16 p-4 container mx-auto">
      <h1>{message}</h1>
      <p>{details}</p>
      {stack && (
        <pre className="w-full p-4 overflow-x-auto">
          <code>{stack}</code>
        </pre>
      )}
    </main>
  );
}

```

---

## app/routes.ts

```ts
import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/home.tsx"),
  route("burrito", "routes/burrito.tsx"),
  route("profile", "routes/profile.tsx"),
  route("error", "routes/error.tsx"),
  route("api/auth/login", "routes/api.auth.login.ts"),
  route("api/burrito/consider", "routes/api.burrito.consider.ts"),
] satisfies RouteConfig;

```

---

## app/routes/api.auth.login.ts

```ts
import type { Route } from "./+types/api.auth.login";
import { getBurritoConsiderations } from "../lib/db";
import type { PostHogContext } from "../lib/posthog-middleware";

const users = new Map<string, { username: string }>();

export { users };

export async function action({ request, context }: Route.ActionArgs) {
  const body = await request.json();
  const { username, password } = body;

  if (!username || !password) {
    return Response.json({ error: 'Username and password required' }, { status: 400 });
  }

  let user = users.get(username);
  
  if (!user) {
    user = { username };
    users.set(username, user);
  }

  const posthog = (context as PostHogContext).posthog;
  if (posthog) {
    posthog.capture({ event: 'server_login' });
  }

  const burritoConsiderations = await getBurritoConsiderations(username);

  return Response.json({ 
    success: true, 
    user: { ...user, burritoConsiderations } 
  });
}

```

---

## app/routes/api.burrito.consider.ts

```ts
import type { Route } from "./+types/api.burrito.consider";
import { users } from "./api.auth.login";
import { incrementBurritoConsiderations } from "../lib/db";
import type { PostHogContext } from "../lib/posthog-middleware";

export async function action({ request, context }: Route.ActionArgs) {
  const body = await request.json();
  const { username } = body;

  if (!username) {
    return Response.json({ error: 'Username required' }, { status: 400 });
  }

  const user = users.get(username);
  
  if (!user) {
    return Response.json({ error: 'User not found' }, { status: 404 });
  }

  const burritoConsiderations = await incrementBurritoConsiderations(username);

  const posthog = (context as PostHogContext).posthog;
  posthog?.capture({ event: 'burrito_considered' });
  
  return Response.json({ 
    success: true, 
    user: { ...user, burritoConsiderations } 
  });
}


```

---

## app/routes/burrito.tsx

```tsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router';
import type { Route } from "./+types/burrito";
import { useAuth } from '../contexts/AuthContext';

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Burrito Consideration - Burrito Consideration App" },
    { name: "description", content: "Consider the potential of burritos" },
  ];
}

export default function BurritoPage() {
  const { user, setUser } = useAuth();
  const navigate = useNavigate();
  const [hasConsidered, setHasConsidered] = useState(false);

  useEffect(() => {
    if (!user) {
      navigate('/');
    }
  }, [user, navigate]);

  if (!user) {
    return null;
  }

  const handleConsideration = async () => {
    try {
      const response = await fetch('/api/burrito/consider', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: user.username }),
      });

      if (response.ok) {
        const { user: updatedUser } = await response.json();
        setUser(updatedUser);
        setHasConsidered(true);
        setTimeout(() => setHasConsidered(false), 2000);
      } else {
        console.error('Failed to increment burrito considerations');
      }
    } catch (err) {
      console.error('Error considering burrito:', err);
    }
  };

  return (
    <div className="container">
      <h1>Burrito consideration zone</h1>
      <p>Take a moment to truly consider the potential of burritos.</p>

      <div style={{ textAlign: 'center' }}>
        <button
          onClick={handleConsideration}
          className="btn-burrito"
        >
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
  );
}


```

---

## app/routes/error.tsx

```tsx
import type { Route } from "./+types/error";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Error Test - Burrito Consideration App" },
    { name: "description", content: "Test error boundary" },
  ];
}

export default function ErrorPage() {
  // This will throw an error during render, which will be caught by ErrorBoundary
  throw new Error('Test error for ErrorBoundary - this is a render-time error');
}


```

---

## app/routes/home.tsx

```tsx
import { useState } from 'react';
import type { Route } from "./+types/home";
import { useAuth } from '../contexts/AuthContext';
import { usePostHog } from '@posthog/react';

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Burrito Consideration App" },
    { name: "description", content: "Consider the potential of burritos" },
  ];
}

export default function Home() {
  const { user, login } = useAuth();
  const posthog = usePostHog();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const success = await login(username, password);
      if (success) {
        // Identifying the user once on login/sign up is enough.
        posthog?.identify(username);
        
        // Capture login event
        posthog?.capture('user_logged_in');
        
        setUsername('');
        setPassword('');
      } else {
        setError('Please provide both username and password');
      }
    } catch (err) {
      console.error('Login failed:', err);
      setError('An error occurred during login');
    }
  };

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
    );
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

        <button type="submit" className="btn-primary">Sign In</button>
      </form>

      <p className="note">
        Note: This is a demo app. Use any username and password to sign in.
      </p>
    </div>
  );
}

```

---

## app/routes/profile.tsx

```tsx
import { useEffect } from 'react';
import { useNavigate } from 'react-router';
import type { Route } from "./+types/profile";
import { useAuth } from '../contexts/AuthContext';
import posthog from 'posthog-js';
import { usePostHog } from '@posthog/react';

export function meta({}: Route.MetaArgs) {
  return [
    { title: "User Profile - Burrito Consideration App" },
    { name: "description", content: "View your profile and burrito consideration stats" },
  ];
}

export default function ProfilePage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const posthog = usePostHog();
  

  useEffect(() => {
    if (!user) {
      navigate('/');
    }
  }, [user, navigate]);

  if (!user) {
    return null;
  }

  const triggerTestError = () => {
    try {
      throw new Error('Test error for PostHog error tracking');
    } catch (err) {
      console.error('Captured error:', err);
      posthog.captureException(err);
    }
  };

  return (
    <div className="container">
      <h1>User Profile</h1>

      <div className="stats">
        <h2>Your Information</h2>
        <p><strong>Username:</strong> {user.username}</p>
        <p><strong>Burrito Considerations:</strong> {user.burritoConsiderations}</p>
      </div>

      <div style={{ marginTop: '2rem' }}>
        <button onClick={triggerTestError} className="btn-primary" style={{ backgroundColor: '#dc3545' }}>
          Trigger Test Error (for PostHog)
        </button>
      </div>

      <div style={{ marginTop: '2rem' }}>
        <h3>Your Burrito Journey</h3>
        {user.burritoConsiderations === 0 ? (
          <p>You haven&apos;t considered any burritos yet. Visit the Burrito Consideration page to start!</p>
        ) : user.burritoConsiderations === 1 ? (
          <p>You&apos;ve considered the burrito potential once. Keep going!</p>
        ) : user.burritoConsiderations < 5 ? (
          <p>You&apos;re getting the hang of burrito consideration!</p>
        ) : user.burritoConsiderations < 10 ? (
          <p>You&apos;re becoming a burrito consideration expert!</p>
        ) : (
          <p>You are a true burrito consideration master! 🌯</p>
        )}
      </div>
    </div>
  );
}


```

---

## app/welcome/welcome.tsx

```tsx
import logoDark from "./logo-dark.svg";
import logoLight from "./logo-light.svg";

export function Welcome() {
  return (
    <main className="flex items-center justify-center pt-16 pb-4">
      <div className="flex-1 flex flex-col items-center gap-16 min-h-0">
        <header className="flex flex-col items-center gap-9">
          <div className="w-[500px] max-w-[100vw] p-4">
            <img
              src={logoLight}
              alt="React Router"
              className="block w-full dark:hidden"
            />
            <img
              src={logoDark}
              alt="React Router"
              className="hidden w-full dark:block"
            />
          </div>
        </header>
        <div className="max-w-[300px] w-full space-y-6 px-4">
          <nav className="rounded-3xl border border-gray-200 p-6 dark:border-gray-700 space-y-4">
            <p className="leading-6 text-gray-700 dark:text-gray-200 text-center">
              What&apos;s next?
            </p>
            <ul>
              {resources.map(({ href, text, icon }) => (
                <li key={href}>
                  <a
                    className="group flex items-center gap-3 self-stretch p-3 leading-normal text-blue-700 hover:underline dark:text-blue-500"
                    href={href}
                    target="_blank"
                    rel="noreferrer"
                  >
                    {icon}
                    {text}
                  </a>
                </li>
              ))}
            </ul>
          </nav>
        </div>
      </div>
    </main>
  );
}

const resources = [
  {
    href: "https://reactrouter.com/docs",
    text: "React Router Docs",
    icon: (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="20"
        viewBox="0 0 20 20"
        fill="none"
        className="stroke-gray-600 group-hover:stroke-current dark:stroke-gray-300"
      >
        <path
          d="M9.99981 10.0751V9.99992M17.4688 17.4688C15.889 19.0485 11.2645 16.9853 7.13958 12.8604C3.01467 8.73546 0.951405 4.11091 2.53116 2.53116C4.11091 0.951405 8.73546 3.01467 12.8604 7.13958C16.9853 11.2645 19.0485 15.889 17.4688 17.4688ZM2.53132 17.4688C0.951566 15.8891 3.01483 11.2645 7.13974 7.13963C11.2647 3.01471 15.8892 0.951453 17.469 2.53121C19.0487 4.11096 16.9854 8.73551 12.8605 12.8604C8.73562 16.9853 4.11107 19.0486 2.53132 17.4688Z"
          strokeWidth="1.5"
          strokeLinecap="round"
        />
      </svg>
    ),
  },
  {
    href: "https://rmx.as/discord",
    text: "Join Discord",
    icon: (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="20"
        viewBox="0 0 24 20"
        fill="none"
        className="stroke-gray-600 group-hover:stroke-current dark:stroke-gray-300"
      >
        <path
          d="M15.0686 1.25995L14.5477 1.17423L14.2913 1.63578C14.1754 1.84439 14.0545 2.08275 13.9422 2.31963C12.6461 2.16488 11.3406 2.16505 10.0445 2.32014C9.92822 2.08178 9.80478 1.84975 9.67412 1.62413L9.41449 1.17584L8.90333 1.25995C7.33547 1.51794 5.80717 1.99419 4.37748 2.66939L4.19 2.75793L4.07461 2.93019C1.23864 7.16437 0.46302 11.3053 0.838165 15.3924L0.868838 15.7266L1.13844 15.9264C2.81818 17.1714 4.68053 18.1233 6.68582 18.719L7.18892 18.8684L7.50166 18.4469C7.96179 17.8268 8.36504 17.1824 8.709 16.4944L8.71099 16.4904C10.8645 17.0471 13.128 17.0485 15.2821 16.4947C15.6261 17.1826 16.0293 17.8269 16.4892 18.4469L16.805 18.8725L17.3116 18.717C19.3056 18.105 21.1876 17.1751 22.8559 15.9238L23.1224 15.724L23.1528 15.3923C23.5873 10.6524 22.3579 6.53306 19.8947 2.90714L19.7759 2.73227L19.5833 2.64518C18.1437 1.99439 16.6386 1.51826 15.0686 1.25995ZM16.6074 10.7755L16.6074 10.7756C16.5934 11.6409 16.0212 12.1444 15.4783 12.1444C14.9297 12.1444 14.3493 11.6173 14.3493 10.7877C14.3493 9.94885 14.9378 9.41192 15.4783 9.41192C16.0471 9.41192 16.6209 9.93851 16.6074 10.7755ZM8.49373 12.1444C7.94513 12.1444 7.36471 11.6173 7.36471 10.7877C7.36471 9.94885 7.95323 9.41192 8.49373 9.41192C9.06038 9.41192 9.63892 9.93712 9.6417 10.7815C9.62517 11.6239 9.05462 12.1444 8.49373 12.1444Z"
          strokeWidth="1.5"
        />
      </svg>
    ),
  },
];

```

---

## react-router.config.ts

```ts
import type { Config } from "@react-router/dev/config";

export default {
  // Config options...
  // Server-side render by default, to enable SPA mode set this to `false`
  ssr: true,
  future: {
    v8_middleware: true,
  },
} satisfies Config;

```

---

## vite.config.ts

```ts
import { reactRouter } from "@react-router/dev/vite";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig, loadEnv } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [tailwindcss(), reactRouter(), tsconfigPaths()],
    ssr: {
      noExternal: ['posthog-js', '@posthog/react'],
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
  };
});

```

---

