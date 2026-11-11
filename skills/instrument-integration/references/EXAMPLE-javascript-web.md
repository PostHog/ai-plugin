# PostHog javascript-web Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/javascript-web

---

## README.md

# PostHog JavaScript Example - Browser Todo App

A simple browser-based todo application built with vanilla JavaScript and Vite, demonstrating PostHog integration for non-framework JavaScript projects.

## Purpose

This example serves as:
- **Verification** that the context-mill wizard works for plain JavaScript projects
- **Reference implementation** of PostHog best practices for vanilla JS browser apps
- **Working example** you can run and modify

## Features Demonstrated

- **PostHog initialization** - `posthog.init()` with `api_host` configuration
- **Autocapture** - Automatic tracking of clicks, form submissions, and pageviews (enabled by default)
- **Custom event tracking** - Manual `posthog.capture()` calls with event properties
- **User identification** - `posthog.identify()` on login and `posthog.reset()` on logout
- **Error tracking** - `posthog.captureException()` for unhandled errors and promise rejections

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure PostHog

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your PostHog project token
# VITE_POSTHOG_PROJECT_TOKEN=phc_your_project_token_here
# VITE_POSTHOG_HOST=https://us.i.posthog.com
```

### 3. Run the App

```bash
npm run dev
```

Open http://localhost:3000 in your browser.

## What Gets Tracked

The app tracks these custom events in PostHog (in addition to autocaptured clicks and pageviews):

| Event | Properties | Purpose |
|-------|-----------|---------|
| `todo_added` | `todo_id`, `text_length`, `total_todos` | When user adds a new todo |
| `todo_completed` | `todo_id`, `time_to_complete_hours` | When user completes a todo |
| `todo_deleted` | `todo_id`, `was_completed` | When user deletes a todo |
| `user_logged_in` | (none) | When user logs in |
| `user_logged_out` | (none) | When user logs out |

## Code Structure

```
example-apps/javascript-web/
├── index.html           # Entry HTML page
├── package.json         # Dependencies (posthog-js, vite)
├── vite.config.js       # Vite configuration
├── .env.example         # Environment variable template
├── .gitignore           # Git ignore rules
├── README.md            # This file
└── src/
    ├── posthog.js       # PostHog initialization (import this first)
    ├── main.js          # Todo app logic with event tracking
    └── style.css        # App styles
```

## Key Implementation Patterns

### 1. Initialization (posthog.js)

```javascript
import posthog from 'posthog-js'

posthog.init(import.meta.env.VITE_POSTHOG_PROJECT_TOKEN, {
  api_host: import.meta.env.VITE_POSTHOG_HOST || 'https://us.i.posthog.com',
  defaults: '2026-08-30',
})
```

Initialize PostHog once, early in your app. All other modules import the same instance. If the project token is not set, `posthog.js` skips initialization and logs a warning in development.

### 2. Event Tracking

```javascript
// Track events with properties — never send PII or user-generated content
posthog.capture('event_name', {
  item_count: 5,           // Metadata is OK
  action_type: 'create',   // Categories are OK
})
```

### 3. User Identification

```javascript
// On login — links events to a known user
posthog.identify('user_123')

// On logout — resets to a new anonymous distinct_id
posthog.reset()
```

### 4. Error Tracking

```javascript
// Global error handlers
window.addEventListener('error', (event) => {
  posthog.captureException(event.error)
})

window.addEventListener('unhandledrejection', (event) => {
  posthog.captureException(event.reason)
})
```

## Running Without PostHog

The app works fine without PostHog configured. You'll see a console warning but the app continues to function normally.

## Next Steps

- Modify the app to experiment with PostHog tracking
- Explore feature flags: `posthog.isFeatureEnabled('flag-key')`
- Check your PostHog dashboard to see tracked events and autocaptured data
- Try session recording (enable in PostHog project settings)

## Reverse proxy

Ad blockers drop requests sent to PostHog's domain, so some events never arrive. A reverse proxy sends events through your own domain instead.

The recommended option is the [managed reverse proxy](https://posthog.com/docs/advanced/proxy/managed-reverse-proxy), which PostHog hosts for you. You create a subdomain in your [organization proxy settings](https://app.posthog.com/settings/organization-proxy) and add a CNAME record at your DNS provider.

If you prefer to run your own, PostHog has guides for [Vercel](https://posthog.com/docs/advanced/proxy/vercel), [Netlify](https://posthog.com/docs/advanced/proxy/netlify) and [Cloudflare](https://posthog.com/docs/advanced/proxy/cloudflare), among others. See [Deploy a reverse proxy](https://posthog.com/docs/advanced/proxy) for the full list.

Once the proxy is live, set `VITE_POSTHOG_HOST` to the proxy URL, for example `https://yoursubdomain.myapp.com`. Also add `ui_host` to the `posthog.init` options, set to your PostHog app URL (`https://us.posthog.com` or `https://eu.posthog.com`), so the toolbar and links into PostHog keep working.

## Learn More

- [PostHog JavaScript SDK Documentation](https://posthog.com/docs/libraries/js)
- [PostHog JavaScript SDK API Reference](https://posthog.com/docs/references/posthog-js)
- [PostHog Product Analytics](https://posthog.com/docs/product-analytics)

---

## .env.example

```example
# PostHog Configuration
VITE_POSTHOG_PROJECT_TOKEN=your_posthog_project_token
VITE_POSTHOG_HOST=https://us.i.posthog.com

```

---

## index.html

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Todo App - PostHog JavaScript Example</title>
    <link rel="stylesheet" href="/src/style.css" />
  </head>
  <body>
    <div id="app">
      <header>
        <h1>Todo App</h1>
        <div id="auth-section">
          <div id="logged-out">
            <input type="text" id="username-input" placeholder="Enter username" />
            <button id="login-btn">Log In</button>
          </div>
          <div id="logged-in" hidden>
            <span id="username-display"></span>
            <button id="logout-btn">Log Out</button>
          </div>
        </div>
      </header>

      <main>
        <form id="todo-form">
          <input type="text" id="todo-input" placeholder="What needs to be done?" required />
          <button type="submit">Add</button>
        </form>

        <ul id="todo-list"></ul>

        <div id="stats">
          <span id="total-count">0 items</span>
          <span id="completed-count">0 completed</span>
        </div>
      </main>
    </div>

    <script type="module" src="/src/main.js"></script>
  </body>
</html>

```

---

## src/main.js

```js
/**
 * Simple Todo App with PostHog Analytics
 *
 * A minimal vanilla JavaScript application demonstrating PostHog integration
 * for non-framework browser JavaScript projects.
 */
import posthog from './posthog.js';

// --- State ---

let todos = JSON.parse(localStorage.getItem('todos') || '[]');
let currentUser = localStorage.getItem('currentUser') || null;

// --- DOM Elements ---

const todoForm = document.getElementById('todo-form');
const todoInput = document.getElementById('todo-input');
const todoList = document.getElementById('todo-list');
const totalCount = document.getElementById('total-count');
const completedCount = document.getElementById('completed-count');
const loginBtn = document.getElementById('login-btn');
const logoutBtn = document.getElementById('logout-btn');
const usernameInput = document.getElementById('username-input');
const usernameDisplay = document.getElementById('username-display');
const loggedOutSection = document.getElementById('logged-out');
const loggedInSection = document.getElementById('logged-in');

// --- Auth ---

function login() {
  const username = usernameInput.value.trim();
  if (!username) return;

  currentUser = username;
  localStorage.setItem('currentUser', username);

  // Identify user in PostHog — links all future events to this user
  // Pass person properties as second arg (this is where name/email belong, NOT in capture())
  posthog.identify(username, { name: username });

  posthog.capture('user_logged_in');

  updateAuthUI();
  usernameInput.value = '';
}

function logout() {
  currentUser = null;
  localStorage.removeItem('currentUser');

  // Reset PostHog — unlinks future events from the current user
  // and generates a new anonymous distinct_id
  posthog.reset();

  posthog.capture('user_logged_out');

  updateAuthUI();
}

function updateAuthUI() {
  if (currentUser) {
    loggedOutSection.hidden = true;
    loggedInSection.hidden = false;
    usernameDisplay.textContent = currentUser;
  } else {
    loggedOutSection.hidden = false;
    loggedInSection.hidden = true;
  }
}

// --- Todos ---

function addTodo(text) {
  const todo = {
    id: Date.now(),
    text,
    completed: false,
    createdAt: new Date().toISOString(),
  };

  todos.push(todo);
  saveTodos();
  renderTodos();

  // Track the event — only metadata, never PII or user-generated content
  posthog.capture('todo_added', {
    todo_id: todo.id,
    text_length: text.length,
    total_todos: todos.length,
  });
}

function toggleTodo(id) {
  const todo = todos.find((t) => t.id === id);
  if (!todo) return;

  todo.completed = !todo.completed;
  saveTodos();
  renderTodos();

  if (todo.completed) {
    const timeToComplete =
      (Date.now() - new Date(todo.createdAt).getTime()) / 3600000;

    posthog.capture('todo_completed', {
      todo_id: todo.id,
      time_to_complete_hours: Math.round(timeToComplete * 100) / 100,
    });
  }
}

function deleteTodo(id) {
  const todo = todos.find((t) => t.id === id);
  if (!todo) return;

  todos = todos.filter((t) => t.id !== id);
  saveTodos();
  renderTodos();

  posthog.capture('todo_deleted', {
    todo_id: todo.id,
    was_completed: todo.completed,
  });
}

function saveTodos() {
  localStorage.setItem('todos', JSON.stringify(todos));
}

// --- Rendering ---

function renderTodos() {
  todoList.innerHTML = '';

  for (const todo of todos) {
    const li = document.createElement('li');
    li.className = `todo-item${todo.completed ? ' completed' : ''}`;

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.checked = todo.completed;
    checkbox.addEventListener('change', () => toggleTodo(todo.id));

    const text = document.createElement('span');
    text.className = 'todo-text';
    text.textContent = todo.text;

    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'delete-btn';
    deleteBtn.textContent = 'Delete';
    deleteBtn.addEventListener('click', () => deleteTodo(todo.id));

    li.append(checkbox, text, deleteBtn);
    todoList.appendChild(li);
  }

  // Update stats
  const completed = todos.filter((t) => t.completed).length;
  totalCount.textContent = `${todos.length} item${todos.length !== 1 ? 's' : ''}`;
  completedCount.textContent = `${completed} completed`;
}

// --- Error Tracking ---

// Capture unhandled errors with PostHog
window.addEventListener('error', (event) => {
  posthog.captureException(event.error);
});

window.addEventListener('unhandledrejection', (event) => {
  posthog.captureException(event.reason);
});

// --- Event Listeners ---

todoForm.addEventListener('submit', (e) => {
  e.preventDefault();
  const text = todoInput.value.trim();
  if (text) {
    addTodo(text);
    todoInput.value = '';
  }
});

loginBtn.addEventListener('click', login);
usernameInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') login();
});
logoutBtn.addEventListener('click', logout);

// --- Init ---

// Restore auth state and re-identify if already logged in
if (currentUser) {
  posthog.identify(currentUser, { name: currentUser });
}

updateAuthUI();
renderTodos();

```

---

## src/posthog.js

```js
/**
 * PostHog initialization for vanilla JavaScript.
 *
 * Initializes posthog-js once and exports the instance for use across the app.
 * This file should be imported before any other modules that call PostHog methods.
 */
import posthog from 'posthog-js';

const projectToken = import.meta.env.VITE_POSTHOG_PROJECT_TOKEN;
const apiHost = import.meta.env.VITE_POSTHOG_HOST || 'https://us.i.posthog.com';

if (!projectToken) {
  if (import.meta.env.DEV) {
    console.warn('VITE_POSTHOG_PROJECT_TOKEN is not set. Skipping PostHog initialization.');
  }
} else {
  posthog.init(projectToken, {
    api_host: apiHost,
    defaults: '2026-08-30',
    // Autocapture is ON by default — tracks clicks, form submissions, pageviews
    // capture_pageview: true (default) — captures $pageview on init
    // For SPAs with History API routing, use: capture_pageview: 'history_change'
  });
}

export default posthog;

```

---

## vite.config.js

```js
import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    port: 3000,
  },
});

```

---

