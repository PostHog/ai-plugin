# PostHog convex Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/convex

---

## README.md

# PostHog Convex example

A [Convex](https://www.convex.dev) example showing PostHog product analytics, user identification, feature flags, and error tracking from inside Convex functions with the `@posthog/convex` component, plus a small React + Vite frontend that uses `posthog-js` with the same ids.

## Features

- **Product analytics**: capture a custom event (`burrito_considered`) from a mutation
- **User identification**: identify on login with the same id in the browser and in Convex; signed-out visitors use `posthog-js`'s random id and send anonymous events
- **Feature flags**: evaluate a flag from an action with `evaluateFlag()`
- **Error tracking**: report a handled error with `captureException()`
- **No flushing**: the component schedules each send with `ctx.scheduler.runAfter`, so nothing needs to be flushed or shut down

## Getting started

### 1. Install dependencies

```bash
pnpm install
```

To add the component to your own Convex app (requires Convex 1.39 or newer):

```bash
pnpm add @posthog/convex
```

### 2. Configure environment variables

The Convex functions read PostHog config from the Convex deployment. The component declares `POSTHOG_PROJECT_TOKEN` as required, so set it before the first deploy:

```bash
npx convex env set POSTHOG_PROJECT_TOKEN phc_your_project_token_here
npx convex env set POSTHOG_HOST https://us.i.posthog.com
```

Use `https://eu.i.posthog.com` for EU Cloud. To evaluate flags locally in queries, also set `POSTHOG_PERSONAL_API_KEY` to a secret API key.

The frontend reads its config from `.env.local` (see `.env.example`):

```bash
cp .env.example .env.local
```

A missing `VITE_POSTHOG_PROJECT_TOKEN` skips `posthog-js` and logs an error in development. `npx convex dev` writes `VITE_CONVEX_URL` to `.env.local`.

### 3. Run the app

```bash
npx convex dev   # in one terminal: deploys functions and generates convex/_generated
pnpm dev         # in another terminal: starts the Vite frontend
```

Check types and the production build:

```bash
pnpm codegen
pnpm typecheck
pnpm build
```

## Project structure

```
convex/
├── convex.config.ts   # Registers the PostHog component and forwards its env vars
├── posthog.ts         # The PostHog client shared by all functions
├── burrito.ts         # Mutations and actions: login, events, flags, error tracking
└── tsconfig.json
src/
├── main.tsx           # posthog-js init and providers
└── App.tsx            # Login, burrito, dashboard and profile buttons
```

## Key integration points

### Register the component (convex/convex.config.ts)

Forward the credentials from the app down to the component.

```ts
const app = defineApp({
    env: {
        POSTHOG_PROJECT_TOKEN: v.string(),
        POSTHOG_HOST: v.optional(v.string()),
    },
})

app.use(posthog, {
    env: {
        POSTHOG_PROJECT_TOKEN: app.env.POSTHOG_PROJECT_TOKEN,
        POSTHOG_HOST: app.env.POSTHOG_HOST,
    },
})
```

### Client (convex/posthog.ts)

```ts
export const posthog = new PostHog(components.posthog)
```

### User identification (convex/burrito.ts)

Use your app's stable user id as `distinctId` and call `identify` once, on login. The browser calls `posthog.identify()` with the same id so frontend and backend events land on one person.

```ts
await posthog.identify(ctx, {
    distinctId: args.userId,
    properties: { email: args.email },
})
```

The demo has no auth provider, so the client passes its user id. In a real app, resolve the id on the server (for example with `ctx.auth`).

### Signed-out visitors (convex/burrito.ts)

The browser passes `posthog.get_distinct_id()`, a random id kept for the visit, and the function sets `$process_person_profile` to `false` so PostHog creates no person profile.

```ts
const properties = args.userId ? {} : { $process_person_profile: false }
```

### Event tracking (convex/burrito.ts)

`capture` works in mutations and actions and returns immediately. The send is rolled back if the mutation throws.

```ts
await posthog.capture(ctx, {
    distinctId: args.userId ?? args.anonymousId,
    event: "burrito_considered",
    properties: { total_considerations: args.totalConsiderations },
})
```

### Feature flags (convex/burrito.ts)

Remote evaluation works in actions without a personal API key. Errors are caught so PostHog never fails the action.

```ts
const enabled = await posthog.evaluateFlag(ctx, {
    key: "new-dashboard-feature",
    distinctId: args.userId ?? args.anonymousId,
})
```

### Error tracking (convex/burrito.ts)

```ts
await posthog.captureException(ctx, {
    error,
    distinctId: args.userId ?? args.anonymousId,
})
```

To forward every uncaught exception without wrapping call sites, configure Convex's [PostHog exception reporting](https://docs.convex.dev/production/integrations/exception-reporting) in the dashboard.

## Reverse proxy

The Convex functions send events from the server, so they do not need a reverse proxy. For the `posthog-js` frontend, see the [managed reverse proxy guide](https://posthog.com/docs/advanced/proxy/managed-reverse-proxy.md).

## Learn more

- [PostHog Convex docs](https://posthog.com/docs/libraries/convex.md)
- [`@posthog/convex` README](https://github.com/PostHog/posthog-js/tree/main/packages/convex)

---

## .env.example

```example
# Frontend (posthog-js). Vite exposes only variables prefixed with VITE_.
VITE_POSTHOG_PROJECT_TOKEN=phc_your_project_token_here
VITE_POSTHOG_HOST=https://us.i.posthog.com

# Convex functions read their PostHog config from the Convex deployment, not from this file:
#   npx convex env set POSTHOG_PROJECT_TOKEN phc_your_project_token_here
#   npx convex env set POSTHOG_HOST https://us.i.posthog.com
# VITE_CONVEX_URL is written to .env.local by `npx convex dev`.

```

---

## convex/burrito.d.ts

```ts
export declare const login: import("convex/server").RegisteredMutation<"public", {
    email: string;
    sessionId?: string | undefined;
    userId: string;
}, Promise<void>>;
export declare const considerBurrito: import("convex/server").RegisteredMutation<"public", {
    anonymousId: string;
    sessionId?: string | undefined;
    totalConsiderations: number;
    userId?: string | undefined;
}, Promise<void>>;
export declare const dashboard: import("convex/server").RegisteredAction<"public", {
    anonymousId: string;
    sessionId?: string | undefined;
    userId?: string | undefined;
}, Promise<{
    showNewFeature: boolean;
}>>;
export declare const profile: import("convex/server").RegisteredAction<"public", {
    anonymousId: string;
    sessionId?: string | undefined;
    userId?: string | undefined;
}, Promise<{
    message: string;
}>>;

```

---

## convex/burrito.js

```js
import { action, mutation } from "./_generated/server";
import { v } from "convex/values";
import { posthog } from "./posthog";
// The demo has no auth provider, so the client passes its user id. In a real
// app, resolve the user id on the server (for example with ctx.auth) and use
// that as the distinctId.
const visitorArgs = {
    userId: v.optional(v.string()),
    anonymousId: v.string(),
    sessionId: v.optional(v.string()),
};
// Signed-in users keep their own id. Signed-out visitors use the random id
// posthog-js keeps for the visit, and send $process_person_profile: false so
// PostHog creates no person profile for them.
function visitorProperties(args) {
    return {
        ...(args.userId ? {} : { $process_person_profile: false }),
        ...(args.sessionId ? { $session_id: args.sessionId } : {}),
    };
}
export const login = mutation({
    args: { userId: v.string(), email: v.string(), sessionId: v.optional(v.string()) },
    handler: async (ctx, args) => {
        // Identify once, on login. Use the same id in posthog.identify() in the browser.
        await posthog.identify(ctx, {
            distinctId: args.userId,
            properties: { email: args.email },
        });
        await posthog.capture(ctx, {
            distinctId: args.userId,
            event: "user_logged_in",
            properties: {
                login_method: "email",
                ...(args.sessionId ? { $session_id: args.sessionId } : {}),
            },
        });
    },
});
export const considerBurrito = mutation({
    args: { ...visitorArgs, totalConsiderations: v.number() },
    handler: async (ctx, args) => {
        await posthog.capture(ctx, {
            distinctId: args.userId ?? args.anonymousId,
            event: "burrito_considered",
            properties: {
                total_considerations: args.totalConsiderations,
                ...visitorProperties(args),
            },
        });
    },
});
// Remote evaluation runs in an action and needs no personal API key. Queries
// can use the local getFeatureFlag() once POSTHOG_PERSONAL_API_KEY is set.
export const dashboard = action({
    args: visitorArgs,
    handler: async (ctx, args) => {
        try {
            const enabled = await posthog.evaluateFlag(ctx, {
                key: "new-dashboard-feature",
                distinctId: args.userId ?? args.anonymousId,
            });
            return { showNewFeature: Boolean(enabled) };
        }
        catch (error) {
            console.warn("Feature flag evaluation failed", error);
            return { showNewFeature: false };
        }
    },
});
export const profile = action({
    args: visitorArgs,
    handler: async (ctx, args) => {
        try {
            throw new Error("Profile data is unavailable");
        }
        catch (error) {
            await posthog.captureException(ctx, {
                error,
                distinctId: args.userId ?? args.anonymousId,
                additionalProperties: visitorProperties(args),
            });
            return { message: "Profile data is unavailable. The error was reported." };
        }
    },
});

```

---

## convex/burrito.ts

```ts
import { action, mutation } from "./_generated/server"
import { v } from "convex/values"
import { posthog } from "./posthog"

// The demo has no auth provider, so the client passes its user id. In a real
// app, resolve the user id on the server (for example with ctx.auth) and use
// that as the distinctId.
const visitorArgs = {
    userId: v.optional(v.string()),
    anonymousId: v.string(),
    sessionId: v.optional(v.string()),
}

// Signed-in users keep their own id. Signed-out visitors use the random id
// posthog-js keeps for the visit, and send $process_person_profile: false so
// PostHog creates no person profile for them.
function visitorProperties(args: { userId?: string; sessionId?: string }) {
    return {
        ...(args.userId ? {} : { $process_person_profile: false }),
        ...(args.sessionId ? { $session_id: args.sessionId } : {}),
    }
}

export const login = mutation({
    args: { userId: v.string(), email: v.string(), sessionId: v.optional(v.string()) },
    handler: async (ctx, args) => {
        // Identify once, on login. Use the same id in posthog.identify() in the browser.
        await posthog.identify(ctx, {
            distinctId: args.userId,
            properties: { email: args.email },
        })

        await posthog.capture(ctx, {
            distinctId: args.userId,
            event: "user_logged_in",
            properties: {
                login_method: "email",
                ...(args.sessionId ? { $session_id: args.sessionId } : {}),
            },
        })
    },
})

export const considerBurrito = mutation({
    args: { ...visitorArgs, totalConsiderations: v.number() },
    handler: async (ctx, args) => {
        await posthog.capture(ctx, {
            distinctId: args.userId ?? args.anonymousId,
            event: "burrito_considered",
            properties: {
                total_considerations: args.totalConsiderations,
                ...visitorProperties(args),
            },
        })
    },
})

// Remote evaluation runs in an action and needs no personal API key. Queries
// can use the local getFeatureFlag() once POSTHOG_PERSONAL_API_KEY is set.
export const dashboard = action({
    args: visitorArgs,
    handler: async (ctx, args) => {
        try {
            const enabled = await posthog.evaluateFlag(ctx, {
                key: "new-dashboard-feature",
                distinctId: args.userId ?? args.anonymousId,
            })
            return { showNewFeature: Boolean(enabled) }
        } catch (error) {
            console.warn("Feature flag evaluation failed", error)
            return { showNewFeature: false }
        }
    },
})

export const profile = action({
    args: visitorArgs,
    handler: async (ctx, args) => {
        try {
            throw new Error("Profile data is unavailable")
        } catch (error) {
            await posthog.captureException(ctx, {
                error,
                distinctId: args.userId ?? args.anonymousId,
                additionalProperties: visitorProperties(args),
            })
            return { message: "Profile data is unavailable. The error was reported." }
        }
    },
})

```

---

## convex/convex.config.ts

```ts
import { defineApp } from "convex/server"
import { v } from "convex/values"
import posthog from "@posthog/convex/convex.config.js"

const app = defineApp({
    env: {
        POSTHOG_PROJECT_TOKEN: v.string(),
        POSTHOG_HOST: v.optional(v.string()),
        POSTHOG_PERSONAL_API_KEY: v.optional(v.string()),
        POSTHOG_FLAGS_POLLING_INTERVAL_SECONDS: v.optional(v.string()),
    },
})

app.use(posthog, {
    env: {
        POSTHOG_PROJECT_TOKEN: app.env.POSTHOG_PROJECT_TOKEN,
        POSTHOG_HOST: app.env.POSTHOG_HOST,
        POSTHOG_PERSONAL_API_KEY: app.env.POSTHOG_PERSONAL_API_KEY,
        POSTHOG_FLAGS_POLLING_INTERVAL_SECONDS: app.env.POSTHOG_FLAGS_POLLING_INTERVAL_SECONDS,
    },
})

export default app

```

---

## convex/posthog.d.ts

```ts
import { PostHog } from "@posthog/convex";
export declare const posthog: PostHog;

```

---

## convex/posthog.js

```js
import { PostHog } from "@posthog/convex";
import { components } from "./_generated/api";
// Credentials live on the component (see convex.config.ts), so the client only
// needs the component reference. Convex functions are short-lived isolates, so
// there is nothing to flush or shut down.
export const posthog = new PostHog(components.posthog);

```

---

## convex/posthog.ts

```ts
import { PostHog } from "@posthog/convex"
import { components } from "./_generated/api"

// Credentials live on the component (see convex.config.ts), so the client only
// needs the component reference. Convex functions are short-lived isolates, so
// there is nothing to flush or shut down.
export const posthog = new PostHog(components.posthog)

```

---

## index.html

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>PostHog Convex example</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>

```

---

## src/App.d.ts

```ts
export default function App(): import("react").JSX.Element;

```

---

## src/App.js

```js
import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from "react";
import { useAction, useMutation } from "convex/react";
import { usePostHog } from "@posthog/react";
import { api } from "../convex/_generated/api";
export default function App() {
    const posthog = usePostHog();
    const login = useMutation(api.burrito.login);
    const considerBurrito = useMutation(api.burrito.considerBurrito);
    const dashboard = useAction(api.burrito.dashboard);
    const profile = useAction(api.burrito.profile);
    const [userId, setUserId] = useState(null);
    const [count, setCount] = useState(0);
    const [message, setMessage] = useState("");
    // Backend functions identify the visitor with the same id the browser uses.
    // Signed-out visitors send posthog-js's random id for the visit.
    const visitor = () => ({
        userId: userId ?? undefined,
        anonymousId: posthog.get_distinct_id(),
        sessionId: posthog.get_session_id(),
    });
    async function handleLogin(formData) {
        const id = String(formData.get("userId"));
        const email = String(formData.get("email"));
        posthog.identify(id, { email });
        await login({ userId: id, email, sessionId: posthog.get_session_id() });
        setUserId(id);
    }
    function handleLogout() {
        posthog.reset();
        setUserId(null);
    }
    async function handleBurrito() {
        const next = count + 1;
        setCount(next);
        await considerBurrito({ ...visitor(), totalConsiderations: next });
        setMessage(`You have considered a burrito ${next} time(s).`);
    }
    async function handleDashboard() {
        const { showNewFeature } = await dashboard(visitor());
        setMessage(showNewFeature ? "You are seeing the new dashboard feature." : "You are seeing the standard dashboard.");
    }
    async function handleProfile() {
        const result = await profile(visitor());
        setMessage(result.message);
    }
    return (_jsxs("main", { children: [_jsx("h1", { children: "Burrito app" }), userId ? (_jsxs("p", { children: ["Signed in as ", _jsx("strong", { children: userId }), " ", _jsx("button", { onClick: handleLogout, children: "Log out" })] })) : (_jsxs("form", { action: handleLogin, children: [_jsxs("label", { children: ["User id ", _jsx("input", { name: "userId", defaultValue: "burrito-fan-42" })] }), _jsxs("label", { children: ["Email ", _jsx("input", { name: "email", defaultValue: "fan@example.com" })] }), _jsx("button", { children: "Log in" })] })), _jsxs("p", { children: [_jsx("button", { onClick: handleBurrito, children: "Consider a burrito" }), _jsx("button", { onClick: handleDashboard, children: "Dashboard" }), _jsx("button", { onClick: handleProfile, children: "Profile" })] }), _jsx("p", { children: message })] }));
}

```

---

## src/App.tsx

```tsx
import { useState } from "react"
import { useAction, useMutation } from "convex/react"
import { usePostHog } from "@posthog/react"
import { api } from "../convex/_generated/api"

export default function App() {
    const posthog = usePostHog()
    const login = useMutation(api.burrito.login)
    const considerBurrito = useMutation(api.burrito.considerBurrito)
    const dashboard = useAction(api.burrito.dashboard)
    const profile = useAction(api.burrito.profile)

    const [userId, setUserId] = useState<string | null>(null)
    const [count, setCount] = useState(0)
    const [message, setMessage] = useState("")

    // Backend functions identify the visitor with the same id the browser uses.
    // Signed-out visitors send posthog-js's random id for the visit.
    const visitor = () => ({
        userId: userId ?? undefined,
        anonymousId: posthog.get_distinct_id(),
        sessionId: posthog.get_session_id(),
    })

    async function handleLogin(formData: FormData) {
        const id = String(formData.get("userId"))
        const email = String(formData.get("email"))

        posthog.identify(id, { email })
        await login({ userId: id, email, sessionId: posthog.get_session_id() })
        setUserId(id)
    }

    function handleLogout() {
        posthog.reset()
        setUserId(null)
    }

    async function handleBurrito() {
        const next = count + 1
        setCount(next)
        await considerBurrito({ ...visitor(), totalConsiderations: next })
        setMessage(`You have considered a burrito ${next} time(s).`)
    }

    async function handleDashboard() {
        const { showNewFeature } = await dashboard(visitor())
        setMessage(showNewFeature ? "You are seeing the new dashboard feature." : "You are seeing the standard dashboard.")
    }

    async function handleProfile() {
        const result = await profile(visitor())
        setMessage(result.message)
    }

    return (
        <main>
            <h1>Burrito app</h1>
            {userId ? (
                <p>
                    Signed in as <strong>{userId}</strong> <button onClick={handleLogout}>Log out</button>
                </p>
            ) : (
                <form action={handleLogin}>
                    <label>
                        User id <input name="userId" defaultValue="burrito-fan-42" />
                    </label>
                    <label>
                        Email <input name="email" defaultValue="fan@example.com" />
                    </label>
                    <button>Log in</button>
                </form>
            )}
            <p>
                <button onClick={handleBurrito}>Consider a burrito</button>
                <button onClick={handleDashboard}>Dashboard</button>
                <button onClick={handleProfile}>Profile</button>
            </p>
            <p>{message}</p>
        </main>
    )
}

```

---

## src/main.d.ts

```ts
export {};

```

---

## src/main.js

```js
import { jsx as _jsx } from "react/jsx-runtime";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import posthog from "posthog-js";
import { PostHogProvider } from "@posthog/react";
import { ConvexProvider, ConvexReactClient } from "convex/react";
import App from "./App";
const posthogToken = import.meta.env.VITE_POSTHOG_PROJECT_TOKEN;
if (posthogToken) {
    posthog.init(posthogToken, {
        api_host: import.meta.env.VITE_POSTHOG_HOST,
        defaults: "2026-08-30",
    });
}
else if (import.meta.env.DEV) {
    console.error("VITE_POSTHOG_PROJECT_TOKEN variable required by PostHog is missing or un-configured, this causes events to be silently missed. This error stops appearing once VITE_POSTHOG_PROJECT_TOKEN is configured");
}
const convexUrl = import.meta.env.VITE_CONVEX_URL;
const convex = convexUrl ? new ConvexReactClient(convexUrl) : null;
createRoot(document.getElementById("root")).render(_jsx(StrictMode, { children: _jsx(PostHogProvider, { client: posthog, children: convex ? (_jsx(ConvexProvider, { client: convex, children: _jsx(App, {}) })) : (_jsx("p", { children: "VITE_CONVEX_URL is not set. Run `npx convex dev` to create a deployment." })) }) }));

```

---

## src/main.tsx

```tsx
import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import posthog from "posthog-js"
import { PostHogProvider } from "@posthog/react"
import { ConvexProvider, ConvexReactClient } from "convex/react"
import App from "./App"

const posthogToken = import.meta.env.VITE_POSTHOG_PROJECT_TOKEN

if (posthogToken) {
    posthog.init(posthogToken, {
        api_host: import.meta.env.VITE_POSTHOG_HOST,
        defaults: "2026-08-30",
    })
} else if (import.meta.env.DEV) {
    console.error(
        "VITE_POSTHOG_PROJECT_TOKEN variable required by PostHog is missing or un-configured, this causes events to be silently missed. This error stops appearing once VITE_POSTHOG_PROJECT_TOKEN is configured"
    )
}

const convexUrl = import.meta.env.VITE_CONVEX_URL
const convex = convexUrl ? new ConvexReactClient(convexUrl) : null

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <PostHogProvider client={posthog}>
            {convex ? (
                <ConvexProvider client={convex}>
                    <App />
                </ConvexProvider>
            ) : (
                <p>VITE_CONVEX_URL is not set. Run `npx convex dev` to create a deployment.</p>
            )}
        </PostHogProvider>
    </StrictMode>
)

```

---

## vite.config.ts

```ts
import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"

export default defineConfig({
    plugins: [react()],
})

```

---

