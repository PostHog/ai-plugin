# PostHog angular Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/angular

---

## README.md

# PostHog Angular Example

This is an [Angular](https://angular.dev/) example demonstrating PostHog integration with product analytics, session replay, and error tracking.

## Features

- **Product analytics**: Track user events and behaviors
- **Session replay**: Record and replay user sessions
- **Error tracking**: Capture and track errors
- **User authentication**: Demo login system with PostHog user identification
- **SSR-safe**: Uses platform checks for browser-only PostHog calls
- **Reverse proxy**: PostHog ingestion through Angular proxy

## Getting started

### 1. Install dependencies

```bash
pnpm install
```

### 2. Configure environment variables

Create a `.env` file in the root directory:

```bash
VITE_POSTHOG_PROJECT_TOKEN=your_posthog_project_token
VITE_POSTHOG_HOST=https://us.posthog.com
```

Get your PostHog project token from your [PostHog project settings](https://app.posthog.com/project/settings).

### 3. Run the development server

```bash
pnpm start
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the app.

## Project structure

```
src/
├── app/
│   ├── components/
│   │   └── header/            # Navigation header with auth state
│   ├── pages/
│   │   ├── home/              # Home/Login page
│   │   ├── burrito/           # Demo feature page with event tracking
│   │   └── profile/           # User profile with error tracking demo
│   ├── services/
│   │   ├── posthog.service.ts # PostHog service wrapper (SSR-safe)
│   │   └── auth.service.ts    # Auth service with PostHog integration
│   ├── guards/
│   │   └── auth.guard.ts      # Route guard for protected pages
│   ├── app.component.ts       # Root component with PostHog init
│   ├── app.routes.ts          # Route definitions
│   └── app.config.ts          # App configuration
├── environments/
│   ├── environment.ts         # Dev environment config
│   └── environment.production.ts
└── main.ts                    # App entry point
```

## Key integration points

### PostHog service (services/posthog.service.ts)

A wrapper service that handles SSR safety and provides access to the PostHog instance:

```typescript
import { Injectable, inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import posthog from 'posthog-js';

@Injectable({ providedIn: 'root' })
export class PostHogService {
  private readonly platformId = inject(PLATFORM_ID);

  get posthog(): typeof posthog {
    if (isPlatformBrowser(this.platformId)) {
      return posthog;
    }
    // Return a no-op proxy for SSR safety
    return new Proxy({} as typeof posthog, {
      get: () => () => undefined,
    });
  }

  init(apiKey: string, options: Partial<PostHogConfig>): void {
    if (isPlatformBrowser(this.platformId)) {
      posthog.init(apiKey, options);
    }
  }
}
```

### PostHog initialization (app.component.ts)

PostHog is initialized in the root component's `ngOnInit`:

```typescript
import { PostHogService } from './services/posthog.service';
import { environment } from '../environments/environment';

export class AppComponent implements OnInit {
  private readonly posthogService = inject(PostHogService);

  ngOnInit(): void {
    this.posthogService.init(environment.posthogKey, {
      api_host: '/ingest',
      ui_host: environment.posthogHost || 'https://us.posthog.com',
      capture_exceptions: true,
    });
  }
}
```

### User identification (services/auth.service.ts)

```typescript
import { PostHogService } from './posthog.service';

const posthogService = inject(PostHogService);

posthogService.posthog.identify(username, {
  username,
  isNewUser,
});
```

### Event tracking (pages/burrito/burrito.component.ts)

```typescript
import { PostHogService } from '../../services/posthog.service';

const posthogService = inject(PostHogService);

posthogService.posthog.capture('burrito_considered', {
  total_considerations: count,
  username: username,
});
```

### Error tracking (pages/profile/profile.component.ts)

```typescript
posthogService.posthog.captureException(error);
```

## Angular-specific details

This example uses Angular 21 with modern features:

1. **Standalone components**: No NgModules, all components use `standalone: true`
2. **Signals**: Reactive state management with Angular signals
3. **SSR support**: Uses `isPlatformBrowser()` checks for SSR safety
4. **Dependency injection**: PostHog wrapped in an injectable service
5. **Proxy configuration**: Uses `proxy.conf.json` for PostHog API calls
6. **Environment files**: Generated from `.env` at build time via prebuild script

## Environment variable handling

Angular CLI doesn't natively support `.env` files. This project uses a prebuild script:

1. `scripts/generate-env.js` reads `.env` and generates `environment.generated.ts`
2. The script runs automatically before `pnpm start` and `pnpm build`
3. Environment files import from the generated file

## Learn more

- [PostHog Documentation](https://posthog.com/docs)
- [Angular Documentation](https://angular.dev/)
- [PostHog JavaScript Web SDK](https://posthog.com/docs/libraries/js)

---

## .env.example

```example
NG_APP_POSTHOG_PROJECT_TOKEN=<ph_project_token>
NG_APP_POSTHOG_HOST=https://us.posthog.com

```

---

## src/app/app.component.ts

```ts
import {
  Component,
  inject,
  OnInit,
  PLATFORM_ID,
  ChangeDetectionStrategy,
} from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { HeaderComponent } from './components/header/header.component';
import { PostHogService } from './services/posthog.service';
import { environment } from '../environments/environment';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, HeaderComponent],
  template: `
    <app-header />
    <router-outlet />
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AppComponent implements OnInit {
  private readonly platformId = inject(PLATFORM_ID);
  private readonly posthogService = inject(PostHogService);

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.posthogService.init(environment.posthogKey, {
        api_host: '/ingest',
        ui_host: environment.posthogHost || 'https://us.posthog.com',
        capture_exceptions: true,
      });
    }
  }
}

```

---

## src/app/app.config.server.ts

```ts
import { mergeApplicationConfig, ApplicationConfig } from '@angular/core';
import { provideServerRendering, withRoutes } from '@angular/ssr';
import { appConfig } from './app.config';
import { serverRoutes } from './app.routes.server';

const serverConfig: ApplicationConfig = {
  providers: [provideServerRendering(withRoutes(serverRoutes))],
};

export const config = mergeApplicationConfig(appConfig, serverConfig);

```

---

## src/app/app.config.ts

```ts
import { ApplicationConfig } from '@angular/core';
import { provideRouter, withComponentInputBinding } from '@angular/router';
import {
  provideClientHydration,
  withEventReplay,
} from '@angular/platform-browser';
import { provideHttpClient, withFetch } from '@angular/common/http';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes, withComponentInputBinding()),
    provideHttpClient(withFetch()),
    provideClientHydration(withEventReplay()),
  ],
};

```

---

## src/app/app.routes.server.ts

```ts
import { RenderMode, ServerRoute } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  {
    path: '',
    renderMode: RenderMode.Server,
  },
  {
    path: 'burrito',
    renderMode: RenderMode.Client, // Protected route, render client-side
  },
  {
    path: 'profile',
    renderMode: RenderMode.Client, // Protected route, render client-side
  },
  {
    path: '**',
    renderMode: RenderMode.Server,
  },
];

```

---

## src/app/app.routes.ts

```ts
import { Routes } from '@angular/router';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
  {
    path: '',
    title: 'Burrito Consideration App',
    loadComponent: () =>
      import('./pages/home/home.component').then((m) => m.HomeComponent),
  },
  {
    path: 'burrito',
    title: 'Burrito Consideration - Burrito Consideration App',
    loadComponent: () =>
      import('./pages/burrito/burrito.component').then(
        (m) => m.BurritoComponent
      ),
    canActivate: [authGuard],
  },
  {
    path: 'profile',
    title: 'Profile - Burrito Consideration App',
    loadComponent: () =>
      import('./pages/profile/profile.component').then(
        (m) => m.ProfileComponent
      ),
    canActivate: [authGuard],
  },
  {
    path: '**',
    redirectTo: '',
  },
];

```

---

## src/app/components/header/header.component.ts

```ts
import { Component, inject, ChangeDetectionStrategy } from '@angular/core';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-header',
  imports: [RouterLink],
  template: `
    <a class="skip-link" href="#main-content">Skip to main content</a>
    <header class="header" role="banner">
      <div class="header-container">
        <nav aria-label="Main navigation">
          <a routerLink="/">Home</a>
          @if (auth.isAuthenticated()) {
            <a routerLink="/burrito">Burrito Consideration</a>
            <a routerLink="/profile">Profile</a>
          }
        </nav>
        <div class="user-section">
          @if (auth.user(); as user) {
            <span>Welcome, {{ user.username }}!</span>
            <button (click)="auth.logout()" class="btn-logout">Logout</button>
          } @else {
            <span>Not logged in</span>
          }
        </div>
      </div>
    </header>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HeaderComponent {
  readonly auth = inject(AuthService);
}

```

---

## src/app/guards/auth.guard.ts

```ts
import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (auth.isAuthenticated()) {
    return true;
  }

  return router.createUrlTree(['/']);
};

```

---

## src/app/pages/burrito/burrito.component.ts

```ts
import {
  Component,
  inject,
  signal,
  ChangeDetectionStrategy,
} from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { PostHogService } from '../../services/posthog.service';

@Component({
  selector: 'app-burrito',
  template: `
    <main id="main-content" tabindex="-1">
      <div class="container">
        <h1>Burrito consideration zone</h1>
        <p>Take a moment to truly consider the potential of burritos.</p>

        <div style="text-align: center">
          <button (click)="handleConsideration()" class="btn-burrito">
            I have considered the burrito potential
          </button>

          @if (hasConsidered()) {
            <p class="success" role="status" aria-live="polite">
              Thank you for your consideration! Count:
              {{ auth.user()?.burritoConsiderations }}
            </p>
          }
        </div>

        <div class="stats">
          <h3>Consideration stats</h3>
          <p>Total considerations: {{ auth.user()?.burritoConsiderations }}</p>
        </div>
      </div>
    </main>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class BurritoComponent {
  readonly auth = inject(AuthService);
  private readonly posthogService = inject(PostHogService);
  private readonly router = inject(Router);

  hasConsidered = signal(false);

  constructor() {
    // Redirect if not authenticated
    if (!this.auth.isAuthenticated()) {
      this.router.navigate(['/']);
    }
  }

  handleConsideration(): void {
    const user = this.auth.user();
    if (!user) return;

    this.auth.incrementBurritoConsiderations();
    this.hasConsidered.set(true);
    setTimeout(() => this.hasConsidered.set(false), 2000);

    this.posthogService.posthog.capture('burrito_considered', {
      total_considerations: user.burritoConsiderations + 1,
      username: user.username,
    });
  }
}

```

---

## src/app/pages/home/home.component.ts

```ts
import {
  Component,
  inject,
  signal,
  ChangeDetectionStrategy,
} from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-home',
  imports: [ReactiveFormsModule],
  template: `
    <main id="main-content" tabindex="-1">
      @if (auth.user(); as user) {
        <div class="container">
          <h1>Welcome back, {{ user.username }}!</h1>
          <p>You are now logged in. Feel free to explore:</p>
          <ul>
            <li>Consider the potential of burritos</li>
            <li>View your profile and statistics</li>
          </ul>
        </div>
      } @else {
        <div class="container">
          <h1>Welcome to Burrito Consideration App</h1>
          <p>Please sign in to begin your burrito journey</p>

          <form [formGroup]="loginForm" (ngSubmit)="handleSubmit()" class="form">
            <div class="form-group">
              <label for="username">Username:</label>
              <input
                type="text"
                id="username"
                formControlName="username"
                placeholder="Enter any username"
                autocomplete="username"
              />
            </div>

            <div class="form-group">
              <label for="password">Password:</label>
              <input
                type="password"
                id="password"
                formControlName="password"
                placeholder="Enter any password"
                autocomplete="current-password"
              />
            </div>

            @if (error()) {
              <p class="error" role="alert">{{ error() }}</p>
            }

            <button type="submit" class="btn-primary">Sign In</button>
          </form>

          <p class="note">
            Note: This is a demo app. Use any username and password to sign in.
          </p>
        </div>
      }
    </main>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HomeComponent {
  private readonly fb = inject(FormBuilder);
  readonly auth = inject(AuthService);

  loginForm = this.fb.nonNullable.group({
    username: ['', Validators.required],
    password: ['', Validators.required],
  });

  error = signal('');

  handleSubmit(): void {
    this.error.set('');

    if (this.loginForm.invalid) {
      this.error.set('Please provide both username and password');
      return;
    }

    const { username, password } = this.loginForm.getRawValue();

    const success = this.auth.login(username, password);
    if (success) {
      this.loginForm.reset();
    } else {
      this.error.set('Please provide both username and password');
    }
  }
}

```

---

## src/app/pages/profile/profile.component.ts

```ts
import {
  Component,
  inject,
  computed,
  ChangeDetectionStrategy,
} from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { PostHogService } from '../../services/posthog.service';

@Component({
  selector: 'app-profile',
  template: `
    <main id="main-content" tabindex="-1">
      <div class="container">
        <h1>User Profile</h1>

        <div class="stats">
          <h2>Your Information</h2>
          <p><strong>Username:</strong> {{ auth.user()?.username }}</p>
          <p>
            <strong>Burrito Considerations:</strong>
            {{ auth.user()?.burritoConsiderations }}
          </p>
        </div>

        <div style="margin-top: 2rem">
          <button
            (click)="triggerTestError()"
            class="btn-primary"
            style="background-color: #dc3545"
          >
            Trigger Test Error (for PostHog)
          </button>
        </div>

        <div style="margin-top: 2rem">
          <h3>Your Burrito Journey</h3>
          <p>{{ journeyMessage() }}</p>
        </div>
      </div>
    </main>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProfileComponent {
  readonly auth = inject(AuthService);
  private readonly posthogService = inject(PostHogService);
  private readonly router = inject(Router);

  journeyMessage = computed(() => {
    const count = this.auth.user()?.burritoConsiderations ?? 0;

    if (count === 0) {
      return "You haven't considered any burritos yet. Visit the Burrito Consideration page to start!";
    } else if (count === 1) {
      return "You've considered the burrito potential once. Keep going!";
    } else if (count < 5) {
      return "You're getting the hang of burrito consideration!";
    } else if (count < 10) {
      return "You're becoming a burrito consideration expert!";
    } else {
      return 'You are a true burrito consideration master!';
    }
  });

  constructor() {
    if (!this.auth.isAuthenticated()) {
      this.router.navigate(['/']);
    }
  }

  triggerTestError(): void {
    try {
      throw new Error('Test error for PostHog error tracking');
    } catch (err) {
      const error = err as Error;
      this.posthogService.posthog.captureException(error);
      console.error('Captured error:', err);
      alert('Error captured and sent to PostHog!');
    }
  }
}

```

---

## src/app/services/auth.service.ts

```ts
import {
  Injectable,
  signal,
  computed,
  inject,
  PLATFORM_ID,
} from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { PostHogService } from './posthog.service';

export interface User {
  username: string;
  burritoConsiderations: number;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly platformId = inject(PLATFORM_ID);
  private readonly posthogService = inject(PostHogService);

  // In-memory user store (matches TanStack behavior)
  private readonly users = new Map<string, User>();

  // Signals for reactive state
  private readonly _user = signal<User | null>(null);

  // Public computed signals
  readonly user = this._user.asReadonly();
  readonly isAuthenticated = computed(() => this._user() !== null);

  constructor() {
    // Initialize from localStorage on browser
    if (isPlatformBrowser(this.platformId)) {
      const storedUsername = localStorage.getItem('currentUser');
      if (storedUsername) {
        const existingUser = this.users.get(storedUsername);
        if (existingUser) {
          this._user.set(existingUser);
        }
      }
    }
  }

  login(username: string, password: string): boolean {
    if (!username || !password) {
      return false;
    }

    // Get or create user in local map (no API call)
    let user = this.users.get(username);
    const isNewUser = !user;

    if (!user) {
      user = { username, burritoConsiderations: 0 };
      this.users.set(username, user);
    }

    this._user.set(user);

    if (isPlatformBrowser(this.platformId)) {
      localStorage.setItem('currentUser', username);
    }

    // PostHog identification (client-side only)
    this.posthogService.posthog.identify(username, {
      username,
      isNewUser,
    });

    this.posthogService.posthog.capture('user_logged_in', {
      username,
      isNewUser,
    });

    return true;
  }

  logout(): void {
    this.posthogService.posthog.capture('user_logged_out');
    this.posthogService.posthog.reset();

    this._user.set(null);

    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem('currentUser');
    }
  }

  incrementBurritoConsiderations(): void {
    const currentUser = this._user();
    if (currentUser) {
      const updated = {
        ...currentUser,
        burritoConsiderations: currentUser.burritoConsiderations + 1,
      };
      this.users.set(currentUser.username, updated);
      this._user.set(updated);
    }
  }
}

```

---

## src/app/services/posthog.service.ts

```ts
import { Injectable, inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import posthog, { PostHogConfig } from 'posthog-js';

@Injectable({ providedIn: 'root' })
export class PostHogService {
  private readonly platformId = inject(PLATFORM_ID);
  private initialized = false;

  /**
   * The posthog instance. Use this directly to call posthog methods.
   * Returns the actual posthog instance on browser, or a no-op proxy on server.
   */
  get posthog(): typeof posthog {
    if (isPlatformBrowser(this.platformId) && this.initialized) {
      return posthog;
    }
    // Return a no-op proxy for SSR safety
    return new Proxy({} as typeof posthog, {
      get: () => () => undefined,
    });
  }

  init(apiKey: string, options: Partial<PostHogConfig>): void {
    if (isPlatformBrowser(this.platformId) && !this.initialized) {
      posthog.init(apiKey, options);
      this.initialized = true;
    }
  }
}

```

---

## src/env.d.ts

```ts
// Define the type of the environment variables.
declare interface Env {
  readonly NODE_ENV: string;
  readonly NG_APP_POSTHOG_PROJECT_TOKEN: string;
  readonly NG_APP_POSTHOG_HOST: string;
}

// Use import.meta.env.YOUR_ENV_VAR in your code.
declare interface ImportMeta {
  readonly env: Env;
}

```

---

## src/environments/environment.prod.ts

```ts
export const environment = {
  production: true,
  posthogKey: import.meta.env['NG_APP_POSTHOG_PROJECT_TOKEN'] || '<ph_project_token>',
  posthogHost: import.meta.env['NG_APP_POSTHOG_HOST'] || 'https://us.posthog.com',
};

```

---

## src/environments/environment.production.ts

```ts
export const environment = {
  production: true,
  posthogKey: import.meta.env['NG_APP_POSTHOG_PROJECT_TOKEN'] || '<ph_project_token>',
  posthogHost: import.meta.env['NG_APP_POSTHOG_HOST'] || 'https://us.posthog.com',
};

```

---

## src/environments/environment.ts

```ts
export const environment = {
  production: false,
  posthogKey: import.meta.env['NG_APP_POSTHOG_PROJECT_TOKEN'] || '<ph_project_token>',
  posthogHost: import.meta.env['NG_APP_POSTHOG_HOST'] || 'https://us.posthog.com',
};

```

---

## src/index.html

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Burrito Consideration App</title>
  <base href="/">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Consider the potential of burritos">
  <link rel="icon" type="image/x-icon" href="favicon.ico">
</head>
<body>
  <app-root></app-root>
</body>
</html>

```

---

## src/main.server.ts

```ts
import { bootstrapApplication, BootstrapContext } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';
import { config } from './app/app.config.server';

const bootstrap = (context: BootstrapContext) =>
  bootstrapApplication(AppComponent, config, context);

export default bootstrap;

```

---

## src/main.ts

```ts
import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';

bootstrapApplication(AppComponent, appConfig).catch((err) =>
  console.error(err)
);

```

---

