# PostHog astro-ssr Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/astro-ssr

---

## README.md

# PostHog Astro SSR Example

This is an [Astro](https://astro.build/) server-side rendered (SSR) example demonstrating PostHog integration with both client-side and server-side event tracking.

It uses:

- **Client-side**: PostHog web snippet for browser analytics
- **Server-side**: `posthog-node` for API route event tracking

This shows how to:

- Initialize PostHog on both client and server
- Track events from API routes using `posthog-node`
- Pass session IDs from client to server for unified sessions
- Identify users on both client and server
- Capture errors via `posthog.captureException()`
- Reset PostHog state on logout

## Features

- **Server-side rendering**: Full SSR with `output: 'server'`
- **API routes**: Server-side endpoints for auth and event tracking
- **Dual tracking**: Events captured on both client and server
- **Session continuity**: Session ID passed to server via headers
- **Product analytics**: Track login and burrito consideration events
- **Session replay**: Enabled via PostHog snippet configuration
- **Error tracking**: Manual error capture sent to PostHog
- **Simple auth flow**: Demo login using localStorage + server API

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
# Client-side (PUBLIC_ prefix exposes to browser)
PUBLIC_POSTHOG_PROJECT_TOKEN=your_posthog_project_token
PUBLIC_POSTHOG_HOST=https://us.i.posthog.com

# Server-side (no PUBLIC_ prefix, server-only)
POSTHOG_PROJECT_TOKEN=your_posthog_project_token
POSTHOG_HOST=https://us.i.posthog.com
```

Get your PostHog project token from your project settings in PostHog.

### 3. Run the development server

```bash
npm run dev
# or
pnpm dev
```

Open `http://localhost:4321` in your browser.

## Project structure

```text
src/
  components/
    posthog.astro      # PostHog snippet for client-side tracking
    Header.astro       # Navigation + logout, calls posthog.reset()
  layouts/
    PostHogLayout.astro # Root layout that includes PostHog + Header
  lib/
    auth.ts            # Client-side auth utilities
    posthog-server.ts  # Server-side PostHog client singleton
  pages/
    index.astro        # Login form, calls /api/auth/login
    burrito.astro      # Burrito demo, calls /api/events/burrito
    profile.astro      # Profile + error tracking demo
    api/
      auth/
        login.ts       # Server-side login endpoint with PostHog tracking
      events/
        burrito.ts     # Server-side event capture endpoint
  styles/
    global.css         # Global styles
```

## Key integration points

### Server-side PostHog client (`src/lib/posthog-server.ts`)

A singleton pattern ensures only one PostHog client is created:

```typescript
import { PostHog } from "posthog-node";

let posthogClient: PostHog | null = null;

export function getPostHogServer(): PostHog {
  if (!posthogClient) {
    posthogClient = new PostHog(import.meta.env.POSTHOG_PROJECT_TOKEN, {
      host: import.meta.env.POSTHOG_HOST,
      flushAt: 1,
      flushInterval: 0,
    });
  }
  return posthogClient;
}
```

### API route with server-side tracking (`src/pages/api/auth/login.ts`)

```typescript
import { getPostHogServer } from "../../../lib/posthog-server";

export const POST: APIRoute = async ({ request }) => {
  const body = await request.json();
  const { username } = body;

  // Get session ID from client
  const sessionId = request.headers.get("X-PostHog-Session-Id");

  const posthog = getPostHogServer();

  // Capture server-side event
  posthog.capture({
    distinctId: username,
    event: "server_login",
    properties: {
      $session_id: sessionId || undefined,
      source: "api",
    },
  });

  return new Response(JSON.stringify({ success: true }));
};
```

### Passing session ID to server (`src/pages/index.astro`)

```javascript
// Get the session ID from PostHog to pass to the server
const sessionId = window.posthog?.get_session_id?.() || null;

const response = await fetch("/api/auth/login", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-PostHog-Session-Id": sessionId || "",
  },
  body: JSON.stringify({ username, password }),
});
```

### Client-side identification (`src/pages/index.astro`)

After server login succeeds, also identify on client:

```javascript
window.posthog?.identify(username);
window.posthog?.capture("user_logged_in");
```

### Logout and session reset (`src/components/Header.astro`)

On logout, both the local auth state and PostHog state are cleared:

```javascript
window.posthog?.capture("user_logged_out");
localStorage.removeItem("currentUser");
window.posthog?.reset();
```

## Scripts

```bash
# Run dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Learn more

- [PostHog documentation](https://posthog.com/docs)
- [PostHog Astro guide](https://posthog.com/docs/libraries/astro)
- [PostHog Node.js SDK](https://posthog.com/docs/libraries/node)
- [Astro SSR documentation](https://docs.astro.build/en/guides/server-side-rendering/)

---

## .env.example

```example
# Client-side environment variables (PUBLIC_ prefix)
PUBLIC_POSTHOG_PROJECT_TOKEN=your_posthog_project_token_here
PUBLIC_POSTHOG_HOST=https://us.i.posthog.com

# Server-side environment variables (no PUBLIC_ prefix)
POSTHOG_PROJECT_TOKEN=your_posthog_project_token_here
POSTHOG_HOST=https://us.i.posthog.com

```

---

## astro.config.mjs

```mjs
import { defineConfig } from "astro/config";
import node from "@astrojs/node";

export default defineConfig({
  output: "server",
  adapter: node({
    mode: "standalone",
  }),
  image: {
    service: { entrypoint: "astro/assets/services/noop" },
  },
});

```

---

## src/components/Header.astro

```astro
---
// Header component with navigation and logout functionality
---
<header class="header">
  <div class="header-container">
    <nav>
      <a href="/">Home</a>
      <a href="/burrito" class="auth-link" style="display: none;">Burrito Consideration</a>
      <a href="/profile" class="auth-link" style="display: none;">Profile</a>
    </nav>
    <div class="user-section">
      <span class="welcome-text" style="display: none;">Welcome, <span class="username"></span>!</span>
      <span class="not-logged-in">Not logged in</span>
      <button class="btn-logout" style="display: none;">Logout</button>
    </div>
  </div>
</header>

<script is:inline>
  function updateHeader() {
    const currentUser = localStorage.getItem('currentUser');
    const authLinks = document.querySelectorAll('.auth-link');
    const welcomeText = document.querySelector('.welcome-text');
    const notLoggedIn = document.querySelector('.not-logged-in');
    const logoutBtn = document.querySelector('.btn-logout');
    const usernameSpan = document.querySelector('.username');

    if (currentUser) {
      authLinks.forEach(link => link.style.display = 'inline');
      welcomeText.style.display = 'inline';
      notLoggedIn.style.display = 'none';
      logoutBtn.style.display = 'inline';
      usernameSpan.textContent = currentUser;
    } else {
      authLinks.forEach(link => link.style.display = 'none');
      welcomeText.style.display = 'none';
      notLoggedIn.style.display = 'inline';
      logoutBtn.style.display = 'none';
    }
  }

  function handleLogout() {
    const currentUser = localStorage.getItem('currentUser');
    if (currentUser) {
      window.posthog?.capture('user_logged_out');
    }
    localStorage.removeItem('currentUser');
    localStorage.removeItem('burritoConsiderations');
    // IMPORTANT: Reset the PostHog instance to clear the user session
    window.posthog?.reset();
    window.location.href = '/';
  }

  document.addEventListener('DOMContentLoaded', () => {
    updateHeader();
    document.querySelector('.btn-logout')?.addEventListener('click', handleLogout);
  });

  // Listen for storage changes (login/logout in other tabs)
  window.addEventListener('storage', updateHeader);
</script>

<style>
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

## src/components/posthog.astro

```astro
---
// PostHog analytics snippet for client-side tracking
// Uses is:inline to prevent Astro from processing the script
---
<script is:inline define:vars={{ apiKey: import.meta.env.PUBLIC_POSTHOG_PROJECT_TOKEN, apiHost: import.meta.env.PUBLIC_POSTHOG_HOST }}>
  !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="capture identify alias people.set people.set_once set_config register register_once unregister opt_out_capturing has_opted_out_capturing opt_in_capturing reset isFeatureEnabled onFeatureFlags getFeatureFlag getFeatureFlagPayload reloadFeatureFlags group updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures getActiveMatchingSurveys getSurveys getNextSurveyStep onSessionId".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
  posthog.init(apiKey || '', {
    api_host: apiHost || 'https://us.i.posthog.com',
    defaults: '2026-01-30'
  })
</script>

```

---

## src/layouts/PostHogLayout.astro

```astro
---
import PostHog from '../components/posthog.astro';
import Header from '../components/Header.astro';
import '../styles/global.css';

interface Props {
  title: string;
}

const { title } = Astro.props;
---
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="Astro PostHog SSR Integration Example" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <title>{title}</title>
    <PostHog />
  </head>
  <body>
    <Header />
    <main>
      <slot />
    </main>
  </body>
</html>

```

---

## src/lib/auth.ts

```ts
// Client-side auth utilities for localStorage-based authentication

export interface User {
  username: string;
  burritoConsiderations: number;
}

export function getCurrentUser(): User | null {
  if (typeof window === "undefined") return null;

  const username = localStorage.getItem("currentUser");
  if (!username) return null;

  const considerations = parseInt(
    localStorage.getItem("burritoConsiderations") || "0",
    10,
  );

  return {
    username,
    burritoConsiderations: considerations,
  };
}

export function login(username: string, password: string): boolean {
  if (!username || !password) return false;

  localStorage.setItem("currentUser", username);
  // Initialize burrito considerations if not set
  if (!localStorage.getItem("burritoConsiderations")) {
    localStorage.setItem("burritoConsiderations", "0");
  }

  return true;
}

export function logout(): void {
  localStorage.removeItem("currentUser");
  localStorage.removeItem("burritoConsiderations");
}

export function incrementBurritoConsiderations(): number {
  const current = parseInt(
    localStorage.getItem("burritoConsiderations") || "0",
    10,
  );
  const newCount = current + 1;
  localStorage.setItem("burritoConsiderations", newCount.toString());
  return newCount;
}

```

---

## src/lib/posthog-server.ts

```ts
import { PostHog } from "posthog-node";

let posthogClient: PostHog | null = null;

/**
 * Get the PostHog server-side client.
 * Uses a singleton pattern to avoid creating multiple clients.
 */
export function getPostHogServer(): PostHog {
  if (!posthogClient) {
    posthogClient = new PostHog(import.meta.env.POSTHOG_PROJECT_TOKEN || "", {
      host: import.meta.env.POSTHOG_HOST || "https://us.i.posthog.com",
      // Flush immediately for demo purposes
      // In production, you might want to batch events
      flushAt: 1,
      flushInterval: 0,
    });
  }
  return posthogClient;
}

/**
 * Shutdown the PostHog client gracefully.
 * Call this when your server is shutting down.
 */
export async function shutdownPostHog(): Promise<void> {
  if (posthogClient) {
    await posthogClient.shutdown();
    posthogClient = null;
  }
}

```

---

## src/pages/api/auth/login.ts

```ts
import type { APIRoute } from "astro";
import { getPostHogServer } from "../../../lib/posthog-server";

// In-memory user store for demo purposes
const users = new Map<string, { username: string; createdAt: string }>();

export const POST: APIRoute = async ({ request }) => {
  try {
    const body = await request.json();
    const { username, password } = body;

    if (!username || !password) {
      return new Response(
        JSON.stringify({ error: "Username and password are required" }),
        { status: 400, headers: { "Content-Type": "application/json" } },
      );
    }

    // Check if this is a new user
    const isNewUser = !users.has(username);

    if (isNewUser) {
      users.set(username, {
        username,
        createdAt: new Date().toISOString(),
      });
    }

    // Get the PostHog server client
    const posthog = getPostHogServer();

    // Get session ID from client if available (passed via header)
    const sessionId = request.headers.get("X-PostHog-Session-Id");

    // Capture server-side login event
    posthog.capture({
      distinctId: username,
      event: "server_login",
      properties: {
        $session_id: sessionId || undefined,
        isNewUser,
        source: "api",
        timestamp: new Date().toISOString(),
      },
    });

    // Also identify the user server-side
    posthog.identify({
      distinctId: username,
      properties: {
        username,
        createdAt: isNewUser ? new Date().toISOString() : undefined,
      },
    });

    return new Response(
      JSON.stringify({
        success: true,
        username,
        isNewUser,
      }),
      { status: 200, headers: { "Content-Type": "application/json" } },
    );
  } catch (error) {
    console.error("Login error:", error);
    return new Response(JSON.stringify({ error: "Internal server error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
};

```

---

## src/pages/api/events/burrito.ts

```ts
import type { APIRoute } from "astro";
import { getPostHogServer } from "../../../lib/posthog-server";

export const POST: APIRoute = async ({ request }) => {
  try {
    const body = await request.json();
    const { username, totalConsiderations } = body;

    if (!username) {
      return new Response(JSON.stringify({ error: "Username is required" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Get the PostHog server client
    const posthog = getPostHogServer();

    // Get session ID from client if available (passed via header)
    const sessionId = request.headers.get("X-PostHog-Session-Id");

    // Capture server-side burrito consideration event
    posthog.capture({
      distinctId: username,
      event: "burrito_considered",
      properties: {
        $session_id: sessionId || undefined,
        total_considerations: totalConsiderations,
        source: "api",
        timestamp: new Date().toISOString(),
      },
    });

    return new Response(
      JSON.stringify({
        success: true,
        totalConsiderations,
      }),
      { status: 200, headers: { "Content-Type": "application/json" } },
    );
  } catch (error) {
    console.error("Burrito event error:", error);
    return new Response(JSON.stringify({ error: "Internal server error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
};

```

---

## src/pages/burrito.astro

```astro
---
import PostHogLayout from '../layouts/PostHogLayout.astro';
---
<PostHogLayout title="Burrito Consideration - Astro PostHog SSR Example">
  <div class="container">
    <h1>Burrito consideration zone</h1>
    <p>Take a moment to truly consider the potential of burritos.</p>

    <div style="text-align: center;">
      <button id="consider-btn" class="btn-burrito">
        I have considered the burrito potential
      </button>

      <p id="success-message" class="success" style="display: none;">
        Thank you for your consideration! Count: <span id="consideration-count"></span>
      </p>
    </div>

    <div class="stats">
      <h3>Consideration stats</h3>
      <p>Total considerations: <span id="total-considerations">0</span></p>
    </div>

    <p class="note" style="margin-top: 1rem;">
      Events are tracked both client-side and server-side for demonstration.
    </p>
  </div>
</PostHogLayout>

<script is:inline>
  function checkAuth() {
    const currentUser = localStorage.getItem('currentUser');
    if (!currentUser) {
      window.location.href = '/';
      return false;
    }
    return true;
  }

  function updateStats() {
    const count = localStorage.getItem('burritoConsiderations') || '0';
    document.getElementById('total-considerations').textContent = count;
  }

  async function handleConsideration() {
    const currentUser = localStorage.getItem('currentUser');
    if (!currentUser) return;

    // Increment the count
    const currentCount = parseInt(localStorage.getItem('burritoConsiderations') || '0', 10);
    const newCount = currentCount + 1;
    localStorage.setItem('burritoConsiderations', newCount.toString());

    // Update the UI
    updateStats();

    const successMessage = document.getElementById('success-message');
    const considerationCount = document.getElementById('consideration-count');
    considerationCount.textContent = newCount;
    successMessage.style.display = 'block';

    // Hide success message after 2 seconds
    setTimeout(() => {
      successMessage.style.display = 'none';
    }, 2000);

    // Client-side event tracking
    window.posthog?.capture('burrito_considered', {
      total_considerations: newCount,
      username: currentUser,
      source: 'client'
    });

    // Also send to server-side API for server tracking
    try {
      const sessionId = window.posthog?.get_session_id?.() || null;

      await fetch('/api/events/burrito', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-PostHog-Session-Id': sessionId || ''
        },
        body: JSON.stringify({
          username: currentUser,
          totalConsiderations: newCount
        })
      });
    } catch (error) {
      console.error('Failed to send server-side event:', error);
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    if (!checkAuth()) return;

    updateStats();
    document.getElementById('consider-btn')?.addEventListener('click', handleConsideration);
  });
</script>

```

---

## src/pages/index.astro

```astro
---
import PostHogLayout from '../layouts/PostHogLayout.astro';
---
<PostHogLayout title="Home - Astro PostHog SSR Example">
  <div class="container">
    <div id="logged-in-view" style="display: none;">
      <h1>Welcome back, <span id="welcome-username"></span>!</h1>
      <p>You are now logged in. Feel free to explore:</p>
      <ul>
        <li>Consider the potential of burritos</li>
        <li>View your profile and statistics</li>
      </ul>
    </div>

    <div id="logged-out-view">
      <h1>Welcome to Burrito Consideration App</h1>
      <p>Please sign in to begin your burrito journey</p>

      <form id="login-form" class="form">
        <div class="form-group">
          <label for="username">Username:</label>
          <input
            type="text"
            id="username"
            placeholder="Enter any username"
            required
          />
        </div>

        <div class="form-group">
          <label for="password">Password:</label>
          <input
            type="password"
            id="password"
            placeholder="Enter any password"
            required
          />
        </div>

        <p id="error-message" class="error" style="display: none;"></p>

        <button type="submit" class="btn-primary">Sign In</button>
      </form>

      <p class="note">
        Note: This is a demo app with server-side tracking. Use any username and password to sign in.
      </p>
    </div>
  </div>
</PostHogLayout>

<script is:inline>
  function updateView() {
    const currentUser = localStorage.getItem('currentUser');
    const loggedInView = document.getElementById('logged-in-view');
    const loggedOutView = document.getElementById('logged-out-view');
    const welcomeUsername = document.getElementById('welcome-username');

    if (currentUser) {
      loggedInView.style.display = 'block';
      loggedOutView.style.display = 'none';
      welcomeUsername.textContent = currentUser;
    } else {
      loggedInView.style.display = 'none';
      loggedOutView.style.display = 'block';
    }
  }

  async function handleLogin(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('error-message');

    if (!username || !password) {
      errorMessage.textContent = 'Please provide both username and password';
      errorMessage.style.display = 'block';
      return;
    }

    try {
      // Get the session ID from PostHog to pass to the server
      const sessionId = window.posthog?.get_session_id?.() || null;

      // Call the server-side login API
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-PostHog-Session-Id': sessionId || ''
        },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Login failed');
      }

      // Store in localStorage for client-side state
      localStorage.setItem('currentUser', username);
      if (!localStorage.getItem('burritoConsiderations')) {
        localStorage.setItem('burritoConsiderations', '0');
      }

      // Also identify on the client side (for session continuity)
      window.posthog?.identify(username);
      window.posthog?.capture('user_logged_in');

      // Clear form
      document.getElementById('username').value = '';
      document.getElementById('password').value = '';
      errorMessage.style.display = 'none';

      // Update view
      updateView();

      // Trigger header update
      window.dispatchEvent(new Event('storage'));
    } catch (error) {
      errorMessage.textContent = error.message || 'Login failed';
      errorMessage.style.display = 'block';
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    updateView();
    document.getElementById('login-form')?.addEventListener('submit', handleLogin);
  });

  // Listen for storage changes
  window.addEventListener('storage', updateView);
</script>

```

---

## src/pages/profile.astro

```astro
---
import PostHogLayout from '../layouts/PostHogLayout.astro';
---
<PostHogLayout title="Profile - Astro PostHog SSR Example">
  <div class="container">
    <h1>User Profile</h1>

    <div class="stats">
      <h2>Your Information</h2>
      <p><strong>Username:</strong> <span id="profile-username"></span></p>
      <p><strong>Burrito Considerations:</strong> <span id="profile-considerations">0</span></p>
    </div>

    <div style="margin-top: 2rem;">
      <h3>Your Burrito Journey</h3>
      <p id="journey-message"></p>
    </div>

    <div style="margin-top: 2rem;">
      <h3>Error Tracking Demo</h3>
      <p>Click the button below to trigger a test error and send it to PostHog:</p>
      <button id="error-btn" class="btn-error">
        Trigger Test Error
      </button>
      <p id="error-feedback" class="success" style="display: none;">
        Error captured and sent to PostHog!
      </p>
    </div>
  </div>
</PostHogLayout>

<script is:inline>
  function checkAuth() {
    const currentUser = localStorage.getItem('currentUser');
    if (!currentUser) {
      window.location.href = '/';
      return false;
    }
    return true;
  }

  function updateProfile() {
    const username = localStorage.getItem('currentUser') || '';
    const considerations = parseInt(localStorage.getItem('burritoConsiderations') || '0', 10);

    document.getElementById('profile-username').textContent = username;
    document.getElementById('profile-considerations').textContent = considerations;

    // Update journey message based on consideration count
    const journeyMessage = document.getElementById('journey-message');
    if (considerations === 0) {
      journeyMessage.textContent = "You haven't considered any burritos yet. Visit the Burrito Consideration page to start!";
    } else if (considerations === 1) {
      journeyMessage.textContent = "You've considered the burrito potential once. Keep going!";
    } else if (considerations < 5) {
      journeyMessage.textContent = "You're getting the hang of burrito consideration!";
    } else if (considerations < 10) {
      journeyMessage.textContent = "You're becoming a burrito consideration expert!";
    } else {
      journeyMessage.textContent = "You are a true burrito consideration master!";
    }
  }

  function triggerTestError() {
    try {
      throw new Error('Test error for PostHog error tracking');
    } catch (err) {
      // Capture the error in PostHog
      window.posthog?.captureException(err);
      console.error('Captured error:', err);

      // Show feedback to user
      const feedback = document.getElementById('error-feedback');
      feedback.style.display = 'block';
      setTimeout(() => {
        feedback.style.display = 'none';
      }, 3000);
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    if (!checkAuth()) return;

    updateProfile();
    document.getElementById('error-btn')?.addEventListener('click', triggerTestError);
  });
</script>

```

---

