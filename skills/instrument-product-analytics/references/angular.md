# Angular - Docs

PostHog makes it easy to get data about traffic and usage of your [Angular](https://angular.dev/) app. Integrating PostHog into your site enables analytics about user behavior, custom events capture, session recordings, feature flags, and more.

This guide walks you through integrating PostHog into your Angular app using the [JavaScript Web SDK](/docs/libraries/js.md).

## Installation

Install `posthog-js` using your package manager:

PostHog AI

### npm

```bash
npm install --save posthog-js
```

### Yarn

```bash
yarn add posthog-js
```

### pnpm

```bash
pnpm add posthog-js
```

### Bun

```bash
bun add posthog-js
```

### Initialize the PostHog client

Generate environment files for your project with `ng g environments`. Configure the following environment variables:

-   `posthogKey`: Your project token from your [project settings](https://app.posthog.com/settings/project#variables).
-   `posthogHost`: Your project's client API host. Usually `https://us.i.posthog.com` for US-based projects and `https://eu.i.posthog.com` for EU-based projects.

## Angular v17+

For Angular v17 and above, you can set up PostHog as a singleton service. To do this, start by creating and injecting a `PosthogService` instance.

Create a service by running `ng g service services/posthog`. The service should look like this:

posthog.service.ts

PostHog AI

```typescript
// src/app/services/posthog.service.ts
import { Injectable, NgZone } from "@angular/core";
import posthog from "posthog-js";
import { environment } from "../../environments/environment";
@Injectable({ providedIn: "root" })
export class PosthogService {
  constructor(
    private ngZone: NgZone,
  ) {
    this.initPostHog();
  }
  private initPostHog() {
    this.ngZone.runOutsideAngular(() => {
      posthog.init(environment.posthogKey, {
        api_host: environment.posthogHost,
        defaults: '2026-01-30',
      });
    });
  }
}
```

The service is initialized [outside of the Angular zone](https://angular.dev/api/core/NgZone#runOutsideAngular) to reduce change detection cycles. This is important to avoid performance issues with session recording.

Then, inject the service in your app's root component `app.component.ts`. This will make sure PostHog is initialized before any other component is rendered.

app.component.ts

PostHog AI

```typescript
// src/app/app.component.ts
import { Component } from "@angular/core";
import { RouterOutlet } from "@angular/router";
import { PosthogService } from "./services/posthog.service";
@Component({
  selector: "app-root",
  styleUrls: ["./app.component.scss"],
  template: `
    <router-outlet />`,
  imports: [RouterOutlet],
})
export class AppComponent {
  title = "angular-app";
  constructor(posthogService: PosthogService) {}
}
```

## Angular v16 and below

In your `src/main.ts`, initialize PostHog using your project token and instance address. You can find both in your [project settings](https://us.posthog.com/project/settings).

main.ts

PostHog AI

```typescript
// src/main.ts
import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';
import { environment } from "./environments/environment";
import posthog from 'posthog-js'
posthog.init(environment.posthogKey, {
  api_host: environment.posthogHost,
  defaults: '2026-01-30'
})
bootstrapApplication(AppComponent, appConfig)
  .catch((err) => console.error(err));
```

## Identifying users

> **Identifying users is required.** Call `posthog.identify('your-user-id')` after login to link events to a known user. This is what connects frontend event captures, [session replays](/docs/session-replay.md), [LLM traces](/docs/ai-engineering.md), and [error tracking](/docs/error-tracking.md) to the same person — and lets backend events link back too.
>
> See our guide on [identifying users](/docs/getting-started/identify-users.md) for how to set this up.

> **Note:** If you're using Typescript, you might have some trouble getting your types to compile because we depend on `rrweb` but don't ship all of their types. To accommodate that, you'll need to add `@rrweb/types@2.0.0-alpha.17` and `rrweb-snapshot@2.0.0-alpha.17` as a dependency if you want your Angular compiler to typecheck correctly.
>
> Given the nature of this library, you might need to completely clear your `.npm` cache to get this to work as expected. Make sure your clear your CI's cache as well.
>
> In the rare case the versions above get out-of-date, you can check our [JavaScript SDK's `package.json`](https://github.com/PostHog/posthog-js/blob/main/package.json) to understand what's the exact version you need to depend on.

Set up a reverse proxy (recommended)

We recommend [setting up a reverse proxy](/docs/advanced/proxy.md), so that events are less likely to be intercepted by tracking blockers.

We have our [own managed reverse proxy service](/docs/advanced/proxy/managed-reverse-proxy.md), which is free for all PostHog Cloud users, routes through our infrastructure, and makes setting up your proxy easy.

If you don't want to use our managed service then there are several other options for creating a reverse proxy, including using [Cloudflare](/docs/advanced/proxy/cloudflare.md), [AWS Cloudfront](/docs/advanced/proxy/cloudfront.md), and [Vercel](/docs/advanced/proxy/vercel.md).

Grouping products in one project (recommended)

If you have multiple customer-facing products (e.g. a marketing website + mobile app + web app), it's best to install PostHog on them all and [group them in one project](/docs/settings/projects.md).

This makes it possible to track users across their entire journey (e.g. from visiting your marketing website to signing up for your product), or how they use your product across multiple platforms.

Add IPs to Firewall/WAF allowlists (recommended)

For certain features like [heatmaps](/docs/toolbar/heatmaps.md), your Web Application Firewall (WAF) may be blocking PostHog’s requests to your site. Add these IP addresses to your WAF allowlist or rules to let PostHog access your site.

**EU**: `3.75.65.221`, `18.197.246.42`, `3.120.223.253`

**US**: `44.205.89.55`, `52.4.194.122`, `44.208.188.173`

These are public, stable IPs used by PostHog services (e.g., Celery tasks for snapshots).

## Tracking pageviews

PostHog automatically tracks your pageviews by hooking up to the browser's `navigator` API as long as you initialize PostHog with the `defaults` config option set after `2026-01-30`.

## Capture custom events

To [capture custom events](/docs/product-analytics/capture-events.md), import `posthog` and call `posthog.capture()`. Below is an example of how to do this in a component:

app.component.ts

PostHog AI

```typescript
import { Component } from '@angular/core';
import posthog from 'posthog-js'
@Component({
 // existing component code
})
export class AppComponent {
  handleClick() {
    posthog.capture(
      'home_button_clicked',
    )
  }
}
```

## Session replay

Session replay uses change detection to record the DOM. This can clash with Angular's change detection.

The recorder tool attempts to detect when an Angular zone is present and avoid the clash but might not always succeed.

-   If you followed the installation instructions for Angular v17 and above, you don't need to do anything.
-   If you followed the installation instructions for Angular v16 and below and you see performance impact from recording in an Angular project, ensure that you use [`ngZone.runOutsideAngular`](https://angular.io/api/core/NgZone#runoutsideangular).

posthog.service.ts

PostHog AI

```typescript
import { Injectable } from '@angular/core';
import posthog from 'posthog-js'
@Injectable({ providedIn: 'root' })
export class PostHogSessionRecordingService {
  constructor(private ngZone: NgZone) {}
initPostHog() {
    this.ngZone.runOutsideAngular(() => {
      posthog.init(
        /* your config */
      )
    })
  }
}
```

## Angular with SSR

To use PostHog with Angular server-side rendering (SSR), you need to:

1.  Update the PostHog web JS client to only initialize on the client-side.
2.  Initialize PostHog Node on the server-side.

### 1\. Update the PostHog web JS client

Update your `posthog.service.ts` to restrict the initialization of the PostHog web JS client to the client-side. The web SDK uses methods that are not available on the server side, so we need to check if we're on the client side before initializing PostHog.

posthog.service.ts

PostHog AI

```typescript
import { PLATFORM_ID } from "@angular/core";
@Injectable({ providedIn: "root" })
export class PosthogService {
  constructor(
    private ngZone: NgZone,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
    // Only initialize PostHog in browser environment
    if (isPlatformBrowser(this.platformId)) {
      this.initPostHog(); //+
    }
  }
  private initPostHog() {
    this.ngZone.runOutsideAngular(() => {
      posthog.init(environment.posthogKey, {
```

### 2\. Add server-side initialization

Angular SSR uses a `server.ts` file to handle requests. We can add any server-side initialization code to this file.

First, install the `posthog-node` package to run on the server side.

PostHog AI

### npm

```bash
npm install posthog-node --save
```

### Yarn

```bash
yarn add posthog-node
```

### pnpm

```bash
pnpm add posthog-node
```

### Bun

```bash
bun add posthog-node
```

Then, add the following code to the `server.ts` file:

server.ts

PostHog AI

```typescript
// src/server.ts
import { environment } from './environments/environment';
import { PostHog } from 'posthog-node'
/**
 * Extract distinct ID from PostHog cookie
 */
function getDistinctIdFromCookie(cookieHeader: string | undefined): string | null {
  if (!cookieHeader) return null;
  const cookieMatch = cookieHeader.match(`ph_${environment.posthogKey}_posthog=([^;]+)`);
  if (cookieMatch) {
    try {
      const parsed = JSON.parse(decodeURIComponent(cookieMatch[1]));
      return parsed?.distinct_id || null;
    } catch (error) {
      console.error('Error parsing PostHog cookie:', error);
      return null;
    }
  }
  return null;
}
/**
 * Handle all other requests by rendering the Angular application.
 */
app.get('**', async (req, res, next) => {
  const { protocol, originalUrl, baseUrl, headers } = req;
  const distinctId = getDistinctIdFromCookie(headers.cookie);
  let isFeatureEnabled = false;
  const client = new PostHog(
      environment.posthogKey,
      { host: environment.posthogHost }
  );
  if (distinctId) {
    client.capture({
      distinctId: distinctId,
      event: 'test_ssr_event',
      properties: {
        message: 'Hello from Angular SSR!'
      }
    })
    isFeatureEnabled = await client.isFeatureEnabled(
      'your_feature_flag_key', distinctId) || false;
  }
  commonEngine
    .render({
      bootstrap,
      documentFilePath: indexHtml,
      url: `${protocol}://${headers.host}${originalUrl}`,
      publicPath: browserDistFolder,
      providers: [
        { provide: APP_BASE_HREF, useValue: baseUrl },
        { provide: 'FEATURE_FLAG_ENABLED', useValue: isFeatureEnabled }
      ],
    })
    .then((html) => res.send(html))
    .catch((err) => next(err));
  await client.shutdown()
});
```

This code does the following:

-   Extracts the distinct ID from the cookie header. This is set by the web JS client.
-   Captures an event on the server side.
-   Evaluates a feature flag on the server side. This can be passed as a provider to the Angular application.
-   Calls `shutdown` on the PostHog Node client to ensure all events are flushed.

**Using PostHog in server-side code**

Angular SSR does not allow Node.js code to be bundled into client-side components. Even though resolvers and other server-side code can be written along with client-side components, you cannot use PostHog Node in those components.

## Next steps

For any technical questions for how to integrate specific PostHog features into Angular (such as feature flags, A/B testing, surveys, etc.), have a look at our [JavaScript Web SDK docs](/docs/libraries/js/features.md).

Alternatively, the following tutorials can help you get started:

-   [How to set up Angular analytics, feature flags, and more](/tutorials/angular-analytics.md)
-   [How to set up A/B tests in Angular](/tutorials/angular-ab-tests.md)
-   [How to set up surveys in Angular](/tutorials/angular-surveys.md)

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better