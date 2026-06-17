# PostHog react-react-router-6 Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/react-react-router-6

---

## README.md

# PostHog React Router 6 example

This is a [React Router 6](https://reactrouter.com) example demonstrating PostHog integration with product analytics, session replay, feature flags, and error tracking.

## Features

- **Product Analytics**: Track user events and behaviors
- **Session Replay**: Record and replay user sessions
- **Error Tracking**: Capture and track errors
- **User Authentication**: Demo login system with PostHog user identification
- **Client-side Tracking**: Examples of client-side tracking methods

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
│   └── AuthContext.jsx      # Authentication context with PostHog integration
├── routes/
│   ├── Root.jsx             # Root route component
│   ├── Home.jsx             # Home/Login page
│   ├── Burrito.jsx          # Demo feature page with event tracking
│   └── Profile.jsx            # User profile with error tracking demo
├── main.jsx                 # App entry point with PostHog initialization
└── globals.css              # Global styles
```

## Key Integration Points

### Client-side initialization (main.jsx)

```javascript
import posthog from "posthog-js"
import { PostHogProvider } from "@posthog/react"

posthog.init(import.meta.env.VITE_PUBLIC_POSTHOG_PROJECT_TOKEN, {
  api_host: import.meta.env.VITE_PUBLIC_POSTHOG_HOST,
  defaults: '2026-01-30',
});

<PostHogProvider client={posthog}>
  <RouterProvider router={router} />
</PostHogProvider>
```

### User identification (AuthContext.jsx)

The user is identified when the user logs in on the **client-side**.

```javascript
posthog.identify(username);
posthog.capture('user_logged_in');
```

The session and distinct ID can be passed to the backend by including the `X-POSTHOG-SESSION-ID` and `X-POSTHOG-DISTINCT-ID` headers.

You should use these headers in the backend to identify events. 

**Important**: do not identify users on the server-side.

### Event tracking (Burrito.jsx)

```javascript
posthog?.capture('burrito_considered', {
  total_considerations: updatedUser.burritoConsiderations,
  username: user.username,
});
```

### Error tracking

**Note**: The app can be wrapped with `PostHogErrorBoundary` from `@posthog/react` (imported in `main.jsx`) to automatically capture unhandled React errors. Manual error capture can be added to components using `posthog?.captureException(err)`.

## Learn More

- [PostHog Documentation](https://posthog.com/docs)
- [React Router 6 Documentation](https://reactrouter.com/en/6.28.0)
- [PostHog React Integration Guide](https://posthog.com/docs/libraries/react)

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
    <title>react-react-router-6</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>

```

---

## src/components/Header.jsx

```jsx
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { usePostHog } from '@posthog/react';

export default function Header() {
  const { user, logout } = useAuth();
  const posthog = usePostHog();

  const handleLogout = () => {
    if (user) {
      posthog.capture('user_logged_out', {
        username: user.username,
        distinct_id: user.username,
      });
    }
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

## src/contexts/AuthContext.jsx

```jsx
import { createContext, useContext, useState } from 'react';

const AuthContext = createContext(undefined);

const users = new Map();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
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

  const login = async (username, password) => {
    if (!username || !password) {
      return false;
    }

    let localUser = users.get(username);
    if (!localUser) {
      localUser = { 
        username, 
        burritoConsiderations: 0 
      };
      users.set(username, localUser);
    }

    setUser(localUser);
    localStorage.setItem('currentUser', username);
    
    return true;
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('currentUser');
  };

  const setUserState = (newUser) => {
    setUser(newUser);
    users.set(newUser.username, newUser);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, setUser: setUserState }}>
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

## src/main.jsx

```jsx
import './globals.css'

import { StrictMode } from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Root from './routes/Root';
import Home from './routes/Home';
import Burrito from './routes/Burrito';
import Profile from './routes/Profile';

import posthog from 'posthog-js'; 
import { PostHogErrorBoundary, PostHogProvider } from '@posthog/react' 

// Initialize PostHog
posthog.init(import.meta.env.VITE_PUBLIC_POSTHOG_PROJECT_TOKEN, { 
  api_host: import.meta.env.VITE_PUBLIC_POSTHOG_HOST, 
  defaults: '2026-01-30', 
}); 

const root = document.getElementById("root");
if (!root) throw new Error("Root element not found");

ReactDOM.createRoot(root).render(
  <StrictMode>
    <PostHogProvider client={posthog}> 
    <PostHogErrorBoundary>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Root />}>
          <Route index element={<Home />} />
          <Route path="burrito" element={<Burrito />} />
          <Route path="profile" element={<Profile />} />
        </Route>
      </Routes>
    </BrowserRouter>
    </PostHogErrorBoundary>
    </PostHogProvider>
  </StrictMode>,
);

```

---

## src/routes/Burrito.jsx

```jsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { usePostHog } from '@posthog/react';

export default function BurritoPage() {
  const { user, setUser } = useAuth();
  const navigate = useNavigate();
  const [hasConsidered, setHasConsidered] = useState(false);
  const posthog = usePostHog()

  useEffect(() => {
    if (!user) {
      navigate('/');
    }
  }, [user, navigate]);

  if (!user) {
    return null;
  }

  const handleConsideration = () => {
    const updatedUser = {
      ...user,
      burritoConsiderations: user.burritoConsiderations + 1
    };
    setUser(updatedUser);
    setHasConsidered(true);
    setTimeout(() => setHasConsidered(false), 2000);
    posthog.capture('burrito_considered', {
      total_considerations: updatedUser.burritoConsiderations,
      username: user.username,
      distinct_id: user.username,
    });
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

## src/routes/Home.jsx

```jsx
import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { usePostHog } from '@posthog/react';

export default function Home() {
  const { user, login } = useAuth();
  const posthog = usePostHog();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const success = await login(username, password);
    if (success) {
      posthog.capture('user_logged_in', {
        username: username,
        distinct_id: username,
      });
      setUsername('');
      setPassword('');
    } else {
      setError('Please provide both username and password');
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

## src/routes/Profile.jsx

```jsx
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function ProfilePage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) {
      navigate('/');
    }
  }, [user, navigate]);

  if (!user) {
    return null;
  }

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

## src/routes/Root.jsx

```jsx
import { Outlet } from "react-router-dom";
import Header from "../components/Header";
import { AuthProvider } from "../contexts/AuthContext";

export default function Root() {
  return (
    <AuthProvider>
      <Header />
      <main>
        <Outlet />
      </main>
    </AuthProvider>
  );
}


```

---

## vite.config.js

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
})

```

---

