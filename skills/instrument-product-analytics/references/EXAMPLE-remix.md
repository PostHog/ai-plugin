# PostHog remix Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/remix

---

## README.md

# PostHog Remix example

A [Remix](https://remix.run) v2 (Vite) app demonstrating PostHog with `posthog-js` in the browser and `posthog-node` on the server, plus a reverse proxy served by a Remix resource route.

Using Remix v3? It is now React Router v7 framework mode. See the `react-react-router-7-framework` example instead.

## Features

- **Product analytics**: autocapture, pageviews and custom events from the browser and the server
- **Session replay**: recordings start with `posthog-js`
- **Feature flags**: `useFeatureFlagEnabled()` gates a tip on the burrito page
- **Error tracking**: an `ErrorBoundary` and `captureException()` in the browser, and Remix's `handleError` on the server
- **User identification**: a demo sign-in that calls `identify()`, and a sign-out that calls `reset()`
- **Server and browser linked**: `tracing_headers` sends the PostHog distinct id and session id to the server routes
- **Reverse proxy**: PostHog traffic goes through `/ingest`

## Getting started

### 1. Install dependencies

```bash
pnpm install
# or
npm install
```

### 2. Configure environment variables

Copy `.env.example` to `.env`:

```bash
VITE_PUBLIC_POSTHOG_PROJECT_TOKEN=phc_your_project_token_here
VITE_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com
```

Get your project token from your [PostHog project settings](https://app.posthog.com/project/settings). Use `https://eu.i.posthog.com` as the host for an EU Cloud project.

Vite reads these at build time, so rebuild after you change them. If the token is missing, the app still builds and runs, skips PostHog, and logs a warning outside production.

### 3. Run the app

```bash
pnpm dev   # http://localhost:5173
pnpm build && pnpm start
```

## Project structure

```
app/
├── auth.tsx             # In-memory demo auth context
├── entry.server.tsx     # Server entry, handleError reports server errors
├── posthog.server.ts    # posthog-node client and capture helpers
├── provider.tsx         # posthog-js initialization and PostHogProvider
├── root.tsx             # Layout, providers and ErrorBoundary
└── routes/
    ├── _index.tsx       # Sign-in page: identify and reset
    ├── burrito.tsx      # Server action with a server-side event, feature flag, error capture
    └── ingest.$.tsx     # Reverse proxy to PostHog
```

## Key integration points

### Browser initialization (provider.tsx)

```typescript
posthog.init(token, {
  api_host: "/ingest",
  ui_host: "https://us.posthog.com",
  defaults: "2026-08-30",
  tracing_headers: [window.location.hostname],
});
```

`posthog-js` and `@posthog/react` are listed under `ssr.noExternal` in `vite.config.ts` so Vite bundles them for server rendering. `PHProvider` initializes PostHog after hydration and wraps the app in `PostHogProvider`.

### Identify and reset (routes/_index.tsx)

```typescript
posthog.identify(username, { username });
posthog.capture("user_logged_in");

posthog.reset(); // on sign-out
```

Identify once when the user signs in, with your own stable user id (a primary key or UUID, never an email), and call `reset()` on sign-out.

### Server-side client (posthog.server.ts)

One `PostHog` client is created per process. Remix handlers are short-lived, so it sends each event straight away (`flushAt: 1`, `flushInterval: 0`, a short `requestTimeout`, no retries) and each helper awaits `posthog.flush().catch(() => {})` so a PostHog outage never fails a request.

```typescript
posthog.capture({
  distinctId: identity.distinctId,
  event,
  properties: { ...properties, ...identity.properties },
});
await posthog.flush().catch(() => {});
```

Identity belongs to the request. `posthog-js` adds `X-POSTHOG-DISTINCT-ID` and `X-POSTHOG-SESSION-ID` headers to same-origin requests, and the helpers use them so server events land on the same person and session as the browser. A request without them gets a random id and `$process_person_profile: false`, so it never shares one person with other visitors.

### Server events (routes/burrito.tsx)

```typescript
await captureEvent(request, "burrito_considered", { total_considerations: count });
```

### Server errors (entry.server.tsx)

Remix handles many loader and action errors inside its router, so the `handleError` export reports them:

```typescript
export function handleError(error: unknown, { request }: { request: Request }) {
  if (request.signal.aborted) return;

  console.error(error);
  void captureError(request, error);
}
```

### Feature flags and browser errors

```typescript
const showTip = useFeatureFlagEnabled("burrito-tip");

posthog.captureException(error); // in the root ErrorBoundary and in event handlers
```

## Reverse proxy

Ad blockers drop events sent to PostHog's domain. This example sends them through your own domain instead, following the [Remix reverse proxy guide](https://posthog.com/docs/advanced/proxy/remix). The splat resource route `app/routes/ingest.$.tsx` forwards `/ingest/static/*` and `/ingest/array/*` to PostHog's assets host and every other `/ingest/*` request to the ingestion host. It sets the `host` header, removes cookies and non-PostHog credentials from the forwarded request, and strips content encoding so compressed responses are not decoded twice. It exports a `loader` for GET requests and an `action` for POST requests.

The region comes from `VITE_PUBLIC_POSTHOG_HOST`. The route derives the ingestion host, the assets host (`-assets.i.posthog.com`) and `ui_host` (`https://us.posthog.com` or `https://eu.posthog.com`) from that one value.

Pick a proxy path unique to your app rather than a common name such as `/analytics` or `/telemetry`. Every PostHog request passes through your server, which can add bandwidth cost on serverless hosts. The [managed reverse proxy](https://posthog.com/docs/advanced/proxy/managed-reverse-proxy.md) avoids that.

## Learn more

- [PostHog Remix docs](https://posthog.com/docs/libraries/remix)
- [Remix docs](https://remix.run/docs)

---

## .env.example

```example
# Get your PostHog project token from: https://app.posthog.com/project/settings
VITE_PUBLIC_POSTHOG_PROJECT_TOKEN=phc_your_project_token_here
# Ingestion host: https://us.i.posthog.com or https://eu.i.posthog.com
VITE_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com

```

---

## app/auth.tsx

```tsx
import { createContext, useContext, useState } from "react";

const AuthContext = createContext<{
  user: string | null;
  setUser: (user: string | null) => void;
} | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<string | null>(null);

  return <AuthContext.Provider value={{ user, setUser }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
}

```

---

## app/entry.server.tsx

```tsx
import { PassThrough } from "node:stream";

import type { AppLoadContext, EntryContext } from "@remix-run/node";
import { createReadableStreamFromReadable } from "@remix-run/node";
import { RemixServer } from "@remix-run/react";
import { isbot } from "isbot";
import { renderToPipeableStream } from "react-dom/server";

import { captureError } from "./posthog.server";

const ABORT_DELAY = 5_000;

// Remix handles loader and action errors inside its router, so report them here
export function handleError(error: unknown, { request }: { request: Request }) {
  if (request.signal.aborted) return;

  console.error(error);
  void captureError(request, error);
}

export default function handleRequest(
  request: Request,
  responseStatusCode: number,
  responseHeaders: Headers,
  remixContext: EntryContext,
  _loadContext: AppLoadContext
) {
  const readyOption = isbot(request.headers.get("user-agent") || "")
    ? "onAllReady"
    : "onShellReady";

  return new Promise((resolve, reject) => {
    let shellRendered = false;

    const { pipe, abort } = renderToPipeableStream(
      <RemixServer context={remixContext} url={request.url} abortDelay={ABORT_DELAY} />,
      {
        [readyOption]() {
          shellRendered = true;
          const body = new PassThrough();
          const stream = createReadableStreamFromReadable(body);

          responseHeaders.set("Content-Type", "text/html");

          resolve(
            new Response(stream, {
              headers: responseHeaders,
              status: responseStatusCode,
            })
          );

          pipe(body);
        },
        onShellError(error: unknown) {
          reject(error);
        },
        onError(error: unknown) {
          responseStatusCode = 500;
          if (shellRendered) {
            console.error(error);
          }
        },
      }
    );

    setTimeout(abort, ABORT_DELAY);
  });
}

```

---

## app/posthog.server.ts

```ts
import { PostHog } from "posthog-node";

const token = import.meta.env.VITE_PUBLIC_POSTHOG_PROJECT_TOKEN;

if (!token && process.env.NODE_ENV !== "production") {
  console.warn(
    "VITE_PUBLIC_POSTHOG_PROJECT_TOKEN variable required by PostHog is missing or un-configured, this causes events to be silently missed. This error stops appearing once VITE_PUBLIC_POSTHOG_PROJECT_TOKEN is configured"
  );
}

// One client for the whole process. Remix handlers are short-lived, so send each event straight away.
export const posthog = token
  ? new PostHog(token, {
      host: import.meta.env.VITE_PUBLIC_POSTHOG_HOST,
      flushAt: 1,
      flushInterval: 0,
      requestTimeout: 2000,
      fetchRetryCount: 0,
      enableExceptionAutocapture: true,
    })
  : null;

// posthog-js adds these headers to same-origin requests because of `tracing_headers`.
// Without them the visitor is anonymous: use a random id and skip creating a person profile.
function identityFrom(request: Request) {
  const distinctId = request.headers.get("X-POSTHOG-DISTINCT-ID");
  const sessionId = request.headers.get("X-POSTHOG-SESSION-ID");

  return {
    distinctId: distinctId ?? crypto.randomUUID(),
    properties: {
      ...(sessionId && { $session_id: sessionId }),
      ...(!distinctId && { $process_person_profile: false }),
    },
  };
}

export async function captureEvent(
  request: Request,
  event: string,
  properties: Record<string, unknown> = {}
) {
  if (!posthog) return;

  const identity = identityFrom(request);
  posthog.capture({
    distinctId: identity.distinctId,
    event,
    properties: { ...properties, ...identity.properties },
  });
  await posthog.flush().catch(() => {});
}

export async function captureError(request: Request, error: unknown) {
  if (!posthog) return;

  const identity = identityFrom(request);
  posthog.captureException(error, identity.distinctId, identity.properties);
  await posthog.flush().catch(() => {});
}

```

---

## app/provider.tsx

```tsx
import { useEffect, useState } from "react";
import posthog from "posthog-js";
import { PostHogProvider } from "@posthog/react";

const token = import.meta.env.VITE_PUBLIC_POSTHOG_PROJECT_TOKEN;

export function PHProvider({ children }: { children: React.ReactNode }) {
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    if (token) {
      posthog.init(token, {
        api_host: "/ingest",
        // The PostHog app for your region
        ui_host: import.meta.env.VITE_PUBLIC_POSTHOG_HOST?.includes("eu.")
          ? "https://eu.posthog.com"
          : "https://us.posthog.com",
        defaults: "2026-08-30",
        // Sends the PostHog distinct and session ids to this app's own server routes
        tracing_headers: [window.location.hostname],
      });
    } else if (import.meta.env.DEV) {
      console.warn(
        "VITE_PUBLIC_POSTHOG_PROJECT_TOKEN variable required by PostHog is missing or un-configured, this causes events to be silently missed. This error stops appearing once VITE_PUBLIC_POSTHOG_PROJECT_TOKEN is configured"
      );
    }

    setHydrated(true);
  }, []);

  if (!hydrated) return <>{children}</>;
  return <PostHogProvider client={posthog}>{children}</PostHogProvider>;
}

```

---

## app/root.tsx

```tsx
import { useEffect } from "react";
import { usePostHog } from "@posthog/react";
import {
  Link,
  Links,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
  isRouteErrorResponse,
  useRouteError,
} from "@remix-run/react";

import { AuthProvider } from "./auth";
import { PHProvider } from "./provider";

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
        <PHProvider>
          <AuthProvider>
            <nav>
              <Link to="/">Home</Link> | <Link to="/burrito">Burrito</Link>
            </nav>
            {children}
          </AuthProvider>
          <ScrollRestoration />
          <Scripts />
        </PHProvider>
      </body>
    </html>
  );
}

export default function App() {
  return <Outlet />;
}

export function ErrorBoundary() {
  const error = useRouteError();
  const posthog = usePostHog();

  useEffect(() => {
    posthog.captureException(error);
  }, [error, posthog]);

  return (
    <main>
      <h1>{isRouteErrorResponse(error) ? error.status : "Oops!"}</h1>
      <p>Something went wrong.</p>
    </main>
  );
}

```

---

## app/routes/_index.tsx

```tsx
import { useState } from "react";
import { usePostHog } from "@posthog/react";
import type { MetaFunction } from "@remix-run/node";

import { useAuth } from "../auth";

// Stands in for your auth system: each username gets a stable user id, the way a user
// record's primary key would. Identify with that id, never with the username or email.
function getUserId(username: string): string {
  const key = `demo-user-id:${username}`;
  const existing = window.localStorage.getItem(key);
  if (existing) return existing;
  const id = crypto.randomUUID();
  window.localStorage.setItem(key, id);
  return id;
}

export const meta: MetaFunction = () => [{ title: "Burrito consideration app" }];

export default function Index() {
  const { user, setUser } = useAuth();
  const posthog = usePostHog();
  const [username, setUsername] = useState("");

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (!username) return;

    posthog.identify(getUserId(username), { username });
    posthog.capture("user_logged_in");
    setUser(username);
    setUsername("");
  };

  const handleLogout = () => {
    posthog.reset();
    setUser(null);
  };

  if (user) {
    return (
      <main>
        <h1>Welcome back, {user}</h1>
        <button onClick={handleLogout}>Sign out</button>
      </main>
    );
  }

  return (
    <main>
      <h1>Burrito consideration app</h1>
      <form onSubmit={handleLogin}>
        <label htmlFor="username">Username</label>{" "}
        <input id="username" value={username} onChange={(e) => setUsername(e.target.value)} />{" "}
        <button type="submit">Sign in</button>
      </form>
    </main>
  );
}

```

---

## app/routes/burrito.tsx

```tsx
import { useFeatureFlagEnabled, usePostHog } from "@posthog/react";
import type { ActionFunctionArgs, MetaFunction } from "@remix-run/node";
import { useFetcher } from "@remix-run/react";
import { useState } from "react";

import { useAuth } from "../auth";
import { captureEvent } from "../posthog.server";

export const meta: MetaFunction = () => [{ title: "Burrito - Burrito consideration app" }];

const considerations = new Map<string, number>();

export async function action({ request }: ActionFunctionArgs) {
  const formData = await request.formData();
  const username = String(formData.get("username") ?? "");
  if (!username) return Response.json({ error: "Username required" }, { status: 400 });

  const count = (considerations.get(username) ?? 0) + 1;
  considerations.set(username, count);

  await captureEvent(request, "burrito_considered", { total_considerations: count });

  return { count };
}

export default function Burrito() {
  const { user } = useAuth();
  const posthog = usePostHog();
  const showTip = useFeatureFlagEnabled("burrito-tip");
  const fetcher = useFetcher<typeof action>();
  const [crash, setCrash] = useState(false);

  if (crash) throw new Error("Demo burrito error");

  if (!user) return <main>Please sign in on the home page first.</main>;

  const handleError = () => {
    try {
      throw new Error("Demo caught burrito error");
    } catch (err) {
      posthog.captureException(err);
    }
  };

  return (
    <main>
      <h1>Burrito consideration zone</h1>
      {showTip && <p>Tip: consider the beans.</p>}
      <fetcher.Form method="post">
        <input type="hidden" name="username" value={user} />
        <button type="submit">Consider a burrito</button>
      </fetcher.Form>
      {fetcher.data && "count" in fetcher.data && (
        <p>Total considerations: {fetcher.data.count}</p>
      )}
      <button onClick={handleError}>Capture a caught error</button>{" "}
      <button onClick={() => setCrash(true)}>Crash the page</button>
    </main>
  );
}

```

---

## app/routes/ingest.$.tsx

```tsx
import type { ActionFunctionArgs, LoaderFunctionArgs } from "@remix-run/node";

// Proxy to the region in VITE_PUBLIC_POSTHOG_HOST: us.i.posthog.com or eu.i.posthog.com
const API_HOST = new URL(
  import.meta.env.VITE_PUBLIC_POSTHOG_HOST || "https://us.i.posthog.com"
).hostname;
const ASSET_HOST = API_HOST.replace(".i.posthog.com", "-assets.i.posthog.com");

async function posthogProxy(request: Request) {
  const url = new URL(request.url);
  const pathname = url.pathname;
  const useAssetHost = pathname.startsWith("/ingest/static/") || pathname.startsWith("/ingest/array/");
  const hostname = useAssetHost ? ASSET_HOST : API_HOST;

  const newUrl = new URL(url);
  newUrl.protocol = "https";
  newUrl.hostname = hostname;
  newUrl.port = "443";
  newUrl.pathname = newUrl.pathname.replace(/^\/ingest/, "");

  const headers = new Headers(request.headers);
  headers.set("host", hostname);
  // Remove cookies before forwarding to PostHog
  headers.delete("cookie");
  // Forward PostHog keys (Bearer phc_, phs_ or phx_), which the SDKs need. Strip any other credentials.
  if (!/^Bearer ph[csx]_/.test(headers.get("authorization") ?? "")) {
    headers.delete("authorization");
  }
  headers.delete("accept-encoding");

  const response = await fetch(newUrl, {
    method: request.method,
    headers,
    body: request.body,
    duplex: "half",
  });

  const responseHeaders = new Headers(response.headers);
  responseHeaders.delete("content-encoding");
  responseHeaders.delete("content-length");

  const data = await response.arrayBuffer();

  return new Response(data, {
    status: response.status,
    statusText: response.statusText,
    headers: responseHeaders,
  });
}

export const loader = ({ request }: LoaderFunctionArgs) => posthogProxy(request);

export const action = ({ request }: ActionFunctionArgs) => posthogProxy(request);

```

---

## vite.config.ts

```ts
import { vitePlugin as remix } from "@remix-run/dev";
import { defineConfig } from "vite";

declare module "@remix-run/node" {
  interface Future {
    v3_singleFetch: true;
  }
}

export default defineConfig({
  plugins: [
    remix({
      future: {
        v3_fetcherPersist: true,
        v3_relativeSplatPath: true,
        v3_throwAbortReason: true,
        v3_singleFetch: true,
        v3_lazyRouteDiscovery: true,
      },
    }),
  ],
  ssr: {
    noExternal: ["posthog-js", "@posthog/react"],
  },
});

```

---

