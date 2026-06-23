# Angular error tracking installation - Docs

1.  1

    ## Install the package

    Required

    Install the PostHog JavaScript library using your package manager:

    PostHog AI

    ### npm

    ```bash
    npm install posthog-js
    ```

    ### yarn

    ```bash
    yarn add posthog-js
    ```

    ### pnpm

    ```bash
    pnpm add posthog-js
    ```

2.  2

    ## Initialize PostHog

    Required

    In your `src/main.ts`, initialize PostHog using your project token and instance address:

    ## Angular 17+

    For Angular v17 and above, you can set up PostHog as a singleton service. To do this, start by creating and injecting a `PosthogService` instance.

    Create a service by running `ng g service services/posthog`. The service should look like this:

    src/main.ts

    PostHog AI

    ```typescript
    // src/app/services/posthog.service.ts
    import { DestroyRef, Injectable, NgZone } from "@angular/core";
    import posthog from "posthog-js";
    import { environment } from "../../environments/environment";
    import { Router } from "@angular/router";
    @Injectable({ providedIn: "root" })
    export class PosthogService {
      constructor(
        private ngZone: NgZone,
        private router: Router,
        private destroyRef: DestroyRef,
      ) {
        this.initPostHog();
      }
      private initPostHog() {
        this.ngZone.runOutsideAngular(() => {
          posthog.init(environment.posthogKey, {
            api_host: environment.posthogHost,
            defaults: '2026-05-30',
          });
        });
      }
    }
    ```

    The service is initialized [outside of the Angular zone](https://angular.dev/api/core/NgZone#runOutsideAngular) to reduce change detection cycles. This is important to avoid performance issues with session recording. Then, inject the service in your app's root component `app.component.ts`. This will make sure PostHog is initialized before any other component is rendered.

    src/app/app.component.ts

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

    ## Angular 16 and below

    In your `src/main.ts`, initialize PostHog using your project API key and instance address. You can find both in your [project settings](https://us.posthog.com/project/settings).

    src/main.ts

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
      defaults: '2026-05-30'
    })
    bootstrapApplication(AppComponent, appConfig)
      .catch((err) => console.error(err));
    ```

3.  3

    ## Send events

    Click around and view a couple pages to generate some events. PostHog automatically captures pageviews, clicks, and other interactions for you.

    If you'd like, you can also manually capture custom events:

    JavaScript

    PostHog AI

    ```javascript
    posthog.capture('my_custom_event', { property: 'value' })
    ```

4.  4

    ## Setting up exception autocapture

    Recommended

    Exception autocapture can be enabled during initialization of the PostHog client to automatically capture any exception thrown by your Angular application.

    This requires overriding Angular's default `ErrorHandler` provider:

    src/app/posthog-error-handler.ts

    PostHog AI

    ```typescript
    import { ErrorHandler, Injectable, Provider } from '@angular/core';
    import { HttpErrorResponse } from '@angular/common/http';
    import posthog from 'posthog-js';
    @Injectable({ providedIn: 'root' })
    class PostHogErrorHandler implements ErrorHandler {
      public constructor() {}
      public handleError(error: unknown): void {
        const extractedError = this._extractError(error) || 'Unknown error';
        runOutsideAngular(() => posthog.captureException(extractedError));
      }
      protected _extractError(errorCandidate: unknown): unknown {
        const error = tryToUnwrapZonejsError(errorCandidate);
        if (error instanceof HttpErrorResponse) {
          return extractHttpModuleError(error);
        }
        if (typeof error === 'string' || isErrorOrErrorLikeObject(error)) {
          return error;
        }
        return null;
      }
    }
    function tryToUnwrapZonejsError(error: unknown): unknown | Error {
      return error && (error as { ngOriginalError: Error }).ngOriginalError
        ? (error as { ngOriginalError: Error }).ngOriginalError
        : error;
    }
    function extractHttpModuleError(error: HttpErrorResponse): string | Error {
      if (isErrorOrErrorLikeObject(error.error)) {
        return error.error;
      }
      if (
        typeof ErrorEvent !== 'undefined' &&
        error.error instanceof ErrorEvent &&
        error.error.message
      ) {
        return error.error.message;
      }
      if (typeof error.error === 'string') {
        return `Server returned code ${error.status} with body "${error.error}"`;
      }
      return error.message;
    }
    function isErrorOrErrorLikeObject(value: unknown): value is Error {
      if (value instanceof Error) {
        return true;
      }
      if (value === null || typeof value !== 'object' || Array.isArray(value)) {
        return false;
      }
      return 'name' in value && 'message' in value && 'stack' in value;
    }
    declare const Zone: any;
    // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
    const isNgZoneEnabled = typeof Zone !== 'undefined' && Zone.root?.run;
    export function runOutsideAngular<T>(callback: () => T): T {
      // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
      return isNgZoneEnabled ? Zone.root.run(callback) : callback();
    }
    export function providePostHogErrorHandler(): Provider {
      return {
        provide: ErrorHandler,
        useValue: new PostHogErrorHandler(),
      };
    }
    ```

    Then, in your `src/app/app.config.ts`, import the `providePostHogErrorHandler` function and add it to the providers array:

    src/app/app.config.ts

    PostHog AI

    ```typescript
    // src/app/app.config.ts
    import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
    import { provideRouter } from '@angular/router';
    import { routes } from './app.routes';
    import { providePostHogErrorHandler } from './posthog-error-handler';
    export const appConfig: ApplicationConfig = {
      providers: [
        ...
        providePostHogErrorHandler(),
      ],
    };
    ```

5.  5

    ## Manually capture exceptions

    Optional

    If there are more errors you'd like to capture, you can manually call the `captureException` method:

    TypeScript

    PostHog AI

    ```typescript
    posthog.captureException(e, additionalProperties)
    ```

6.  ## Verify error tracking

    Recommended

    *Confirm events are being sent to PostHog*

    Before proceeding, let's make sure exception events are being captured and sent to PostHog. You should see events appear in the activity feed.

    ![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_ouxl_f788dd8cd2.png)![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_owae_7c3490822c.png)

    [Check for exceptions in PostHog](https://app.posthog.com/activity/explore)

7.  6

    ## Upload source maps

    Required

    Great, you're capturing exceptions! If you serve minified bundles, the next step is to upload source maps to generate accurate stack traces.

    Let's continue to the next section.

    [Upload source maps](/docs/error-tracking/upload-source-maps/angular.md)

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better