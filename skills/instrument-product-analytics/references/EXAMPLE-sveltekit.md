# PostHog sveltekit Example Project

Repository: https://github.com/PostHog/context-mill
Path: basics/sveltekit

---

## README.md

# SvelteKit PostHog example

This example demonstrates how to integrate PostHog with a SvelteKit application, including:

- Client-side PostHog initialization using SvelteKit hooks
- Server-side PostHog tracking with the Node.js SDK
- Reverse proxy to avoid ad blockers
- User identification and event tracking
- Error tracking with `captureException`
- Session replay configuration

## Getting started

### 1. Install dependencies

```bash
npm install
```

### 2. Configure environment variables

Copy the example environment file and add your PostHog credentials:

```bash
cp .env.example .env
```

Edit `.env` with your PostHog project token:

```
PUBLIC_POSTHOG_PROJECT_TOKEN=your_posthog_project_token_here
PUBLIC_POSTHOG_HOST=https://us.i.posthog.com
```

You can find your project token in your [PostHog project settings](https://app.posthog.com/project/settings).

### 3. Run the development server

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) to view the app.

## Project structure

```
src/
├── lib/
│   ├── auth.svelte.ts              # Auth context with Svelte 5 runes
│   ├── components/
│   │   └── Header.svelte           # Navigation component
│   └── server/
│       └── posthog.ts              # Server-side PostHog singleton
├── routes/
│   ├── +layout.svelte              # Root layout with auth provider
│   ├── +page.svelte                # Home/login page
│   ├── burrito/
│   │   └── +page.svelte            # Event tracking demo
│   ├── profile/
│   │   └── +page.svelte            # Error tracking demo
│   └── api/
│       └── auth/
│           └── login/
│               └── +server.ts      # Login API with server-side tracking
├── hooks.client.ts                 # Client-side PostHog init + error handling
├── hooks.server.ts                 # Server hooks with reverse proxy
├── app.css                         # Global styles
└── app.html                        # HTML template
```

## Key integration points

### Client-side initialization (`src/hooks.client.ts`)

PostHog is initialized in the SvelteKit client hooks `init` function, which runs once when the app starts:

```typescript
import posthog from 'posthog-js';

export async function init() {
  posthog.init(PUBLIC_POSTHOG_PROJECT_TOKEN, {
    api_host: '/ingest',
    ui_host: 'https://us.posthog.com',
    defaults: '2026-01-30',
    capture_exceptions: true
  });
}
```

### Server-side tracking (`src/lib/server/posthog.ts`)

A singleton pattern ensures one PostHog client instance for server-side tracking:

```typescript
import { PostHog } from 'posthog-node';

let posthogClient: PostHog | null = null;

export function getPostHogClient() {
  if (!posthogClient) {
    posthogClient = new PostHog(PUBLIC_POSTHOG_PROJECT_TOKEN, {
      host: PUBLIC_POSTHOG_HOST,
      flushAt: 1,
      flushInterval: 0
    });
  }
  return posthogClient;
}
```

### Reverse proxy (`src/hooks.server.ts`)

The server hooks handle proxies requests through `/ingest` to avoid ad blockers:

```typescript
export const handle: Handle = async ({ event, resolve }) => {
  if (event.url.pathname.startsWith('/ingest')) {
    const pathname = event.url.pathname.replace('/ingest', '');
    const host = pathname.startsWith('/static')
      ? 'https://us-assets.i.posthog.com'
      : 'https://us.i.posthog.com';
    // Proxy to PostHog...
  }
  return resolve(event);
};
```

### User identification

When a user logs in, they are identified in PostHog:

```typescript
import posthog from 'posthog-js';

// On login
posthog.identify(userId, { username });
posthog.capture('user_logged_in', { username });

// On logout
posthog.capture('user_logged_out');
posthog.reset();
```

### Error tracking

Errors are automatically captured via the `handleError` hook:

```typescript
export const handleError: HandleClientError = async ({ error }) => {
  posthog.captureException(error);
  return { message: 'An error occurred' };
};
```

You can also manually capture errors:

```typescript
try {
  // Some operation
} catch (err) {
  posthog.captureException(err);
}
```

### Session replay configuration

For session replay to work correctly, add this to `svelte.config.js`:

```javascript
export default {
  kit: {
    paths: {
      relative: false
    }
  }
};
```

## Features demonstrated

1. **Login page** (`/`) - User authentication with PostHog identification
2. **Burrito page** (`/burrito`) - Custom event tracking with properties
3. **Profile page** (`/profile`) - Error tracking demonstration

## Learn more

- [PostHog Svelte documentation](https://posthog.com/docs/libraries/svelte)
- [PostHog SvelteKit proxy setup](https://posthog.com/docs/advanced/proxy/sveltekit)
- [SvelteKit documentation](https://svelte.dev/docs/kit)

---

## .env.example

```example
# PostHog configuration
# Get your PostHog project token from: https://app.posthog.com/project/settings
PUBLIC_POSTHOG_PROJECT_TOKEN=your_posthog_project_token_here
PUBLIC_POSTHOG_HOST=https://us.i.posthog.com

```

---

## .npmrc

```
engine-strict=true

```

---

## src/app.d.ts

```ts
// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		// interface Locals {}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};

```

---

## src/app.html

```html
<!doctype html>
<html lang="en">
	<head>
		<meta charset="utf-8" />
		<meta name="viewport" content="width=device-width, initial-scale=1" />
		%sveltekit.head%
	</head>
	<body data-sveltekit-preload-data="hover">
		<div style="display: contents">%sveltekit.body%</div>
	</body>
</html>

```

---

## src/hooks.client.ts

```ts
import posthog from 'posthog-js';
import { PUBLIC_POSTHOG_PROJECT_TOKEN } from '$env/static/public';
import type { HandleClientError } from '@sveltejs/kit';

// Initialize PostHog when the app starts in the browser
export async function init() {
	posthog.init(PUBLIC_POSTHOG_PROJECT_TOKEN, {
		api_host: '/ingest',
		ui_host: 'https://us.posthog.com',
  defaults: '2026-01-30',
		capture_exceptions: true
	});
}

// Capture client-side errors with PostHog
export const handleError: HandleClientError = async ({ error, status, message }) => {
	posthog.captureException(error);

	return {
		message,
		status
	};
};

```

---

## src/hooks.server.ts

```ts
import type { Handle, HandleServerError } from '@sveltejs/kit';
import { getPostHogClient } from '$lib/server/posthog';

// Handle requests - includes reverse proxy for PostHog
export const handle: Handle = async ({ event, resolve }) => {
	const { pathname } = event.url;

	// Reverse proxy for PostHog - route /ingest requests to PostHog servers
	if (pathname.startsWith('/ingest')) {
		const useAssetHost = pathname.startsWith('/ingest/static/') || pathname.startsWith('/ingest/array/')
		const hostname = useAssetHost ? 'us-assets.i.posthog.com' : 'us.i.posthog.com';

		const url = new URL(event.request.url);
		url.protocol = 'https:';
		url.hostname = hostname;
		url.port = '443';
		url.pathname = pathname.replace(/^\/ingest/, '');

		const headers = new Headers(event.request.headers);
		headers.set('host', hostname);
		headers.set('accept-encoding', '');

		const clientIp = event.request.headers.get('x-forwarded-for') || event.getClientAddress();
		if (clientIp) {
			headers.set('x-forwarded-for', clientIp);
		}

		const response = await fetch(url.toString(), {
			method: event.request.method,
			headers,
			body: event.request.body,
			// @ts-expect-error - duplex is required for streaming request bodies
			duplex: 'half'
		});

		return response;
	}

	return resolve(event);
};

// Capture server-side errors with PostHog
export const handleError: HandleServerError = async ({ error, status, message }) => {
	const posthog = getPostHogClient();

	posthog.capture({
		distinctId: 'server',
		event: 'server_error',
		properties: {
			error: error instanceof Error ? error.message : String(error),
			status,
			message
		}
	});

	return {
		message,
		status
	};
};

```

---

## src/lib/auth.svelte.ts

```ts
import { getContext, setContext } from 'svelte';
import posthog from 'posthog-js';
import { browser } from '$app/environment';

export interface User {
	username: string;
	burritoConsiderations: number;
}

const AUTH_KEY = Symbol('auth');

// Class-based auth state using Svelte 5 $state in class fields
// This is the recommended pattern for encapsulating reactive state + behavior
export class AuthState {
	user = $state<User | null>(null);

	constructor() {
		// Restore user from localStorage on creation (browser only)
		if (browser) {
			const storedUsername = localStorage.getItem('currentUser');
			if (storedUsername) {
				this.user = { username: storedUsername, burritoConsiderations: 0 };
			}
		}
	}

	login = async (username: string, password: string): Promise<boolean> => {
		try {
			const response = await fetch('/api/auth/login', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username, password })
			});

			if (response.ok) {
				const { user: userData } = await response.json();
				this.user = userData as User;

				if (browser) {
					localStorage.setItem('currentUser', username);
					posthog.identify(username, { username });
					posthog.capture('user_logged_in', { username });
				}

				return true;
			}
			return false;
		} catch (error) {
			console.error('Login error:', error);
			return false;
		}
	};

	logout = (): void => {
		if (browser) {
			posthog.capture('user_logged_out');
			posthog.reset();
			localStorage.removeItem('currentUser');
		}
		this.user = null;
	};

	incrementBurritoConsiderations = (): void => {
		if (this.user) {
			this.user = {
				...this.user,
				burritoConsiderations: this.user.burritoConsiderations + 1
			};
		}
	};
}

export function setAuthContext(auth: AuthState) {
	setContext(AUTH_KEY, auth);
}

export function getAuthContext(): AuthState {
	return getContext<AuthState>(AUTH_KEY);
}

```

---

## src/lib/components/Header.svelte

```svelte
<script lang="ts">
	import { getAuthContext } from '$lib/auth.svelte';

	const auth = getAuthContext();
</script>

<header class="header">
	<div class="header-container">
		<nav>
			<a href="/">Home</a>
			{#if auth.user}
				<a href="/burrito">Burrito</a>
				<a href="/profile">Profile</a>
			{/if}
		</nav>
		<div class="user-section">
			{#if auth.user}
				<span>Welcome, {auth.user.username}</span>
				<button class="btn-logout" onclick={() => auth.logout()}>Logout</button>
			{/if}
		</div>
	</div>
</header>

```

---

## src/lib/index.ts

```ts
// place files you want to import through the `$lib` alias in this folder.

```

---

## src/lib/server/posthog.ts

```ts
import { PostHog } from 'posthog-node';
import { PUBLIC_POSTHOG_PROJECT_TOKEN, PUBLIC_POSTHOG_HOST } from '$env/static/public';

let posthogClient: PostHog | null = null;

export function getPostHogClient() {
	if (!posthogClient) {
		posthogClient = new PostHog(PUBLIC_POSTHOG_PROJECT_TOKEN, {
			host: PUBLIC_POSTHOG_HOST,
			flushAt: 1,
			flushInterval: 0
		});
	}
	return posthogClient;
}

export async function shutdownPostHog() {
	if (posthogClient) {
		await posthogClient.shutdown();
	}
}

```

---

## src/routes/+layout.svelte

```svelte
<script lang="ts">
	import { AuthState, setAuthContext } from '$lib/auth.svelte';
	import Header from '$lib/components/Header.svelte';
	import '../app.css';

	let { children } = $props();

	// Create and provide auth context
	const auth = new AuthState();
	setAuthContext(auth);
</script>

<svelte:head>
	<title>Burrito consideration app</title>
	<meta name="description" content="Consider the potential of burritos with PostHog analytics" />
</svelte:head>

<Header />
<main>
	{@render children()}
</main>

```

---

## src/routes/+page.svelte

```svelte
<script lang="ts">
	import { getAuthContext } from '$lib/auth.svelte';

	const auth = getAuthContext();

	let username = $state('');
	let password = $state('');
	let error = $state('');

	async function handleSubmit(e: Event) {
		e.preventDefault();
		error = '';

		try {
			const success = await auth.login(username, password);
			if (success) {
				username = '';
				password = '';
			} else {
				error = 'Please provide both username and password';
			}
		} catch (err) {
			console.error('Login failed:', err);
			error = 'An error occurred during login';
		}
	}
</script>

<div class="container">
	{#if auth.user}
		<h1>Welcome back, {auth.user.username}!</h1>
		<p>You are now logged in. Check out the navigation to explore features.</p>
		<ul>
			<li><a href="/burrito">Consider a burrito</a></li>
			<li><a href="/profile">View your profile</a></li>
		</ul>
	{:else}
		<h1>Welcome to Burrito consideration app</h1>
		<p>Sign in to start considering burritos.</p>

		<form class="form" onsubmit={handleSubmit}>
			<div class="form-group">
				<label for="username">Username:</label>
				<input type="text" id="username" bind:value={username} required />
			</div>

			<div class="form-group">
				<label for="password">Password:</label>
				<input type="password" id="password" bind:value={password} required />
			</div>

			{#if error}
				<p class="error">{error}</p>
			{/if}

			<button type="submit" class="btn-primary">Sign In</button>
		</form>

		<p class="note">
			Enter any username and password to sign in. This is a demo app.
		</p>
	{/if}
</div>

```

---

## src/routes/api/auth/login/+server.ts

```ts
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getPostHogClient } from '$lib/server/posthog';

const users = new Map<string, { username: string; burritoConsiderations: number }>();

export const POST: RequestHandler = async ({ request }) => {
	const { username, password } = await request.json();

	if (!username || !password) {
		return json({ error: 'Username and password required' }, { status: 400 });
	}

	let user = users.get(username);
	const isNewUser = !user;

	if (!user) {
		user = { username, burritoConsiderations: 0 };
		users.set(username, user);
	}

	// Capture server-side login event with user context
	const posthog = getPostHogClient();
	posthog.withContext(
		{
			distinctId: username,
			personProperties: {
				username,
				createdAt: isNewUser ? new Date().toISOString() : undefined
			}
		},
		() => {
			posthog.capture({
				event: 'server_login',
				properties: {
					isNewUser,
					source: 'api'
				}
			});
		}
	);

	// Flush events to ensure they're sent
	await posthog.flush();

	return json({ success: true, user });
};

```

---

## src/routes/burrito/+page.svelte

```svelte
<script lang="ts">
	import { goto } from '$app/navigation';
	import { browser } from '$app/environment';
	import posthog from 'posthog-js';
	import { getAuthContext } from '$lib/auth.svelte';

	const auth = getAuthContext();

	let hasConsidered = $state(false);

	// Redirect to home if not logged in
	$effect(() => {
		if (browser && !auth.user) {
			goto('/');
		}
	});

	function handleConsideration() {
		if (!auth.user) return;

		auth.incrementBurritoConsiderations();
		hasConsidered = true;
		setTimeout(() => (hasConsidered = false), 2000);

		// Capture burrito consideration event with PostHog
		posthog.capture('burrito_considered', {
			total_considerations: auth.user.burritoConsiderations,
			username: auth.user.username
		});
	}
</script>

<div class="container">
	{#if auth.user}
		<h1>Burrito consideration zone</h1>
		<p>This is where you consider the infinite potential of burritos.</p>
		<p>Current considerations: <strong>{auth.user.burritoConsiderations}</strong></p>

		<button class="btn-burrito" onclick={handleConsideration}>
			I have considered the burrito potential
		</button>

		{#if hasConsidered}
			<p class="success">
				Thank you for your consideration! Count: {auth.user.burritoConsiderations}
			</p>
		{/if}

		<div class="note">
			<p>Each consideration is tracked as a PostHog event with custom properties.</p>
		</div>
	{:else}
		<p>Please log in to consider burritos.</p>
	{/if}
</div>

```

---

## src/routes/profile/+page.svelte

```svelte
<script lang="ts">
	import { goto } from '$app/navigation';
	import { browser } from '$app/environment';
	import posthog from 'posthog-js';
	import { getAuthContext } from '$lib/auth.svelte';

	const auth = getAuthContext();

	// Redirect to home if not logged in
	$effect(() => {
		if (browser && !auth.user) {
			goto('/');
		}
	});

	function triggerTestError() {
		try {
			throw new Error('Test error for PostHog error tracking');
		} catch (err) {
			posthog.captureException(err);
			console.error('Captured error:', err);
			alert('Error captured and sent to PostHog!');
		}
	}
</script>

<div class="container">
	{#if auth.user}
		<h1>User profile</h1>

		<div class="stats">
			<h2>Your information</h2>
			<p><strong>Username:</strong> {auth.user.username}</p>
			<p><strong>Burrito considerations:</strong> {auth.user.burritoConsiderations}</p>
		</div>

		<h2 style="margin-top: 2rem;">Error tracking demo</h2>
		<p>Click the button below to trigger a test error that will be captured by PostHog.</p>

		<button class="btn-primary" onclick={triggerTestError} style="margin-top: 1rem;">
			Trigger test error (for PostHog)
		</button>

		<div class="note">
			<p>This demonstrates PostHog's error tracking capabilities.</p>
			<p>The error will appear in your PostHog error tracking dashboard.</p>
		</div>
	{:else}
		<p>Please log in to view your profile.</p>
	{/if}
</div>

```

---

## static/robots.txt

```txt
# allow crawling everything by default
User-agent: *
Disallow:

```

---

## svelte.config.js

```js
import adapter from '@sveltejs/adapter-auto';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	// Consult https://svelte.dev/docs/kit/integrations
	// for more information about preprocessors
	preprocess: vitePreprocess(),

	kit: {
		// adapter-auto only supports some environments, see https://svelte.dev/docs/kit/adapter-auto for a list.
		// If your environment is not supported, or you settled on a specific environment, switch out the adapter.
		// See https://svelte.dev/docs/kit/adapters for more information about adapters.
		adapter: adapter(),
		// Required for PostHog session replay to work correctly with SSR
		paths: {
			relative: false
		}
	}
};

export default config;

```

---

## vite.config.ts

```ts
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()]
});

```

---

