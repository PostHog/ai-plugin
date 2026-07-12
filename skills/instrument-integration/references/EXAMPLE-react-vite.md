# PostHog react-vite Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/react-vite

---

## README.md

# PostHog React + Vite example

A minimal [React](https://react.dev) application built with [Vite](https://vite.dev), demonstrating PostHog integration with product analytics, session replay, feature flags, and error tracking.

This example uses no client-side router, making it the simplest possible React + PostHog setup.

## Features

- **Product Analytics**: Track user events and behaviors
- **Session Replay**: Record and replay user sessions
- **Feature Flags**: Toggle features with `useFeatureFlagEnabled()`
- **Error Tracking**: Automatic error capture with `PostHogErrorBoundary`
- **User Authentication**: Demo login system with PostHog user identification

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
src/
├── components/
│   └── Header.jsx           # Navigation header with auth state
├── contexts/
│   └── AuthContext.jsx       # Authentication context
├── pages/
│   ├── Home.jsx              # Home/Login page with event tracking
│   ├── Burrito.jsx           # Demo page with feature flags
│   └── Profile.jsx           # User profile page
├── main.jsx                  # Entry point with PostHog initialization
├── App.jsx                   # App component with page routing
└── globals.css               # Global styles
```

## Key Integration Points

### Initialization (main.jsx)

```javascript
import posthog from 'posthog-js'
import { PostHogErrorBoundary, PostHogProvider } from '@posthog/react'

posthog.init(import.meta.env.VITE_PUBLIC_POSTHOG_PROJECT_TOKEN, {
  api_host: import.meta.env.VITE_PUBLIC_POSTHOG_HOST,
  defaults: '2026-01-30',
})

<PostHogProvider client={posthog}>
  <PostHogErrorBoundary>
    <App />
  </PostHogErrorBoundary>
</PostHogProvider>
```

### User identification (Home.jsx)

```javascript
posthog.identify(username, { name: username })
posthog.capture('user_logged_in')
```

### Feature flags (Burrito.jsx)

```javascript
import { useFeatureFlagEnabled } from '@posthog/react'

const showSpecialBurrito = useFeatureFlagEnabled('special-burrito')
```

### Pageview tracking (Header.jsx)

Without a router, manually capture pageviews on navigation:

```javascript
posthog.capture('$pageview', { $current_url: `/${target}` })
```

## Learn More

- [PostHog Documentation](https://posthog.com/docs)
- [PostHog React SDK](https://posthog.com/docs/libraries/react)
- [Vite Documentation](https://vite.dev)

---

## .env.example

```example
VITE_PUBLIC_POSTHOG_PROJECT_TOKEN=
VITE_PUBLIC_POSTHOG_HOST=
PROJECT_ID=

```

---

## index.html

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>react-vite</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>

```

---

## src/App.jsx

```jsx
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Home from './pages/Home'
import Burrito from './pages/Burrito'
import Profile from './pages/Profile'
import Header from './components/Header'

function AppContent() {
  const { user } = useAuth()

  if (!user) {
    return <Home />
  }

  return <MainApp />
}

function MainApp() {
  const { page } = useAuth()

  return (
    <>
      {page === 'home' && <Home />}
      {page === 'burrito' && <Burrito />}
      {page === 'profile' && <Profile />}
    </>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <Header />
      <main>
        <AppContent />
      </main>
    </AuthProvider>
  )
}

```

---

## src/components/Header.jsx

```jsx
import { useAuth } from '../contexts/AuthContext'
import { usePostHog } from '@posthog/react'

export default function Header() {
  const { user, logout, page, setPage } = useAuth()
  const posthog = usePostHog()

  const handleLogout = () => {
    if (user) {
      posthog.capture('user_logged_out', {
        username: user.username,
      })
    }
    logout()
    posthog.reset()
  }

  const navigate = (target) => {
    setPage(target)
    posthog.capture('$pageview', { $current_url: `/${target}` })
  }

  return (
    <header className="header">
      <div className="header-container">
        <nav>
          <button onClick={() => navigate('home')} className={page === 'home' ? 'active' : ''}>
            Home
          </button>
          {user && (
            <>
              <button onClick={() => navigate('burrito')} className={page === 'burrito' ? 'active' : ''}>
                Burrito Consideration
              </button>
              <button onClick={() => navigate('profile')} className={page === 'profile' ? 'active' : ''}>
                Profile
              </button>
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
  )
}

```

---

## src/contexts/AuthContext.jsx

```jsx
import { createContext, useContext, useState } from 'react'

const AuthContext = createContext(undefined)

const users = new Map()

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    if (typeof window === 'undefined') return null
    const storedUsername = localStorage.getItem('currentUser')
    if (storedUsername) {
      return users.get(storedUsername) || null
    }
    return null
  })
  const [page, setPage] = useState('home')

  const login = async (username, password) => {
    if (!username || !password) return false

    let localUser = users.get(username)
    if (!localUser) {
      localUser = { username, burritoConsiderations: 0 }
      users.set(username, localUser)
    }

    setUser(localUser)
    localStorage.setItem('currentUser', username)
    return true
  }

  const logout = () => {
    setUser(null)
    setPage('home')
    localStorage.removeItem('currentUser')
  }

  const setUserState = (newUser) => {
    setUser(newUser)
    users.set(newUser.username, newUser)
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, setUser: setUserState, page, setPage }}>
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

## src/main.jsx

```jsx
import './globals.css'

import { StrictMode } from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'

import posthog from 'posthog-js'
import { PostHogErrorBoundary, PostHogProvider } from '@posthog/react'

posthog.init(import.meta.env.VITE_PUBLIC_POSTHOG_PROJECT_TOKEN, {
  api_host: import.meta.env.VITE_PUBLIC_POSTHOG_HOST,
  defaults: '2026-01-30',
})

const root = document.getElementById('root')
if (!root) throw new Error('Root element not found')

ReactDOM.createRoot(root).render(
  <StrictMode>
    <PostHogProvider client={posthog}>
      <PostHogErrorBoundary>
        <App />
      </PostHogErrorBoundary>
    </PostHogProvider>
  </StrictMode>,
)

```

---

## src/pages/Burrito.jsx

```jsx
import { useAuth } from '../contexts/AuthContext'
import { usePostHog } from '@posthog/react'

export default function Burrito() {
  const { user, setUser } = useAuth()
  const posthog = usePostHog()

  if (!user) return null

  const handleConsider = () => {
    const updatedUser = {
      ...user,
      burritoConsiderations: user.burritoConsiderations + 1,
    }
    setUser(updatedUser)

    posthog.capture('burrito_considered', {
      total_considerations: updatedUser.burritoConsiderations,
    })
  }

  return (
    <div className="container">
      <h1>Burrito Consideration Zone</h1>

      <div className="burrito-stats">
        <p>Times considered: <strong>{user.burritoConsiderations}</strong></p>
        <button onClick={handleConsider} className="btn-burrito">
          Consider a Burrito
        </button>
      </div>

      <div className="burrito-info">
        <h2>Why Consider Burritos?</h2>
        <ul>
          <li>They are delicious</li>
          <li>They are portable</li>
          <li>They contain multiple food groups</li>
          <li>They bring joy</li>
        </ul>
      </div>
    </div>
  )
}

```

---

## src/pages/Home.jsx

```jsx
import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { usePostHog } from '@posthog/react'

export default function Home() {
  const { user, login } = useAuth()
  const posthog = usePostHog()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    const success = await login(username, password)
    if (success) {
      posthog.identify(username, { name: username })
      posthog.capture('user_logged_in')
      setUsername('')
      setPassword('')
    } else {
      setError('Please provide both username and password')
    }
  }

  if (user) {
    return (
      <div className="container">
        <h1>Welcome back, {user.username}!</h1>
        <p>You are logged in. Feel free to explore:</p>
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

        <button type="submit" className="btn-primary">Sign In</button>
      </form>

      <p className="note">
        Note: This is a demo app. Use any username and password to sign in.
      </p>
    </div>
  )
}

```

---

## src/pages/Profile.jsx

```jsx
import { useAuth } from '../contexts/AuthContext'

export default function Profile() {
  const { user } = useAuth()

  if (!user) return null

  return (
    <div className="container">
      <h1>User Profile</h1>

      <div className="stats">
        <h2>Your Information</h2>
        <p><strong>Username:</strong> {user.username}</p>
        <p><strong>Burrito Considerations:</strong> {user.burritoConsiderations}</p>
      </div>

      <div style={{ marginTop: '2rem' }}>
        <h3>Your Burrito Journey</h3>
        {user.burritoConsiderations === 0 ? (
          <p>You haven&apos;t considered any burritos yet. Visit the Burrito Consideration page to start!</p>
        ) : user.burritoConsiderations < 5 ? (
          <p>You&apos;re getting the hang of burrito consideration!</p>
        ) : user.burritoConsiderations < 10 ? (
          <p>You&apos;re becoming a burrito consideration expert!</p>
        ) : (
          <p>You are a true burrito consideration master!</p>
        )}
      </div>
    </div>
  )
}

```

---

## vite.config.js

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})

```

---

