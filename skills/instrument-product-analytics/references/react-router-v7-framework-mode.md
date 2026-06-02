# React Router V7 framework mode (Remix V3) - Docs

This guide walks you through setting up PostHog for React Router V7 in framework mode. If you're using React Router in another mode, find the guide for that mode in the [React Router page](/docs/libraries/react-router.md). If you're using React with another framework, go to the [React integration guide](/docs/libraries/react.md).

1.  1

    ## Install client-side SDKs

    Required

    First, you'll need to install [`posthog-js`](https://github.com/posthog/posthog-js) and `@posthog/react` using your package manager. These packages allow you to capture **client-side** events.

    PostHog AI

    ### npm

    ```bash
    npm install --save posthog-js @posthog/react
    ```

    ### Yarn

    ```bash
    yarn add posthog-js @posthog/react
    ```

    ### pnpm

    ```bash
    pnpm add posthog-js @posthog/react
    ```

    ### Bun

    ```bash
    bun add posthog-js @posthog/react
    ```

    In framework mode, you'll also need to set `posthog-js` and `@posthog/react` as external packages in your `vite.config.ts` file to avoid SSR errors.

    vite.config.ts

    PostHog AI

    ```typescript
    // ... imports
    export default defineConfig({
      plugins: [tailwindcss(), reactRouter(), tsconfigPaths()],
      ssr: {
        noExternal: ['posthog-js', '@posthog/react']
      }
    });
    ```

2.  2

    ## Add your environment variables

    Required

    Add your environment variables to your `.env.local` file and to your hosting provider (e.g. Vercel, Netlify, AWS). You can find your project token and host in [your project settings](https://us.posthog.com/settings/project). If you're using Vite, prefixing variable names with `VITE_` ensures they are accessible in the frontend.

    .env.local

    PostHog AI

    ```shell
    VITE_POSTHOG_PROJECT_TOKEN=<ph_project_token>
    VITE_POSTHOG_HOST=https://us.i.posthog.com
    ```

3.  3

    ## Add the PostHogProvider to your app

    Required

    In framework mode, your app enters from the `app/entry.client.tsx` file. In this file, you'll need to initialize the PostHog SDK and pass it to your app through the `PostHogProvider` context.

    app/entry.client.tsx

    PostHog AI

    ```jsx
    import { startTransition, StrictMode } from "react";
    import { hydrateRoot } from "react-dom/client";
    import { HydratedRouter } from "react-router/dom";
    import posthog from 'posthog-js';
    import { PostHogProvider } from '@posthog/react'
    posthog.init(import.meta.env.VITE_POSTHOG_PROJECT_TOKEN, {
      api_host: import.meta.env.VITE_POSTHOG_HOST,
      defaults: '2026-01-30',
      __add_tracing_headers: [ window.location.host, 'localhost' ],
    });
    startTransition(() => {
      hydrateRoot(
        document,
        {/* Pass PostHog client through PostHogProvider */}
        <PostHogProvider client={posthog}>
          <StrictMode>
            <HydratedRouter />
          </StrictMode>
        </PostHogProvider>,
      );
    });
    ```

    To help PostHog track your user sessions across the client and server, you'll need to add the `__add_tracing_headers: ['your-backend-domain1.com', 'your-backend-domain2.com', ...]` option to your PostHog initialization. This adds the `X-POSTHOG-DISTINCT-ID` and `X-POSTHOG-SESSION-ID` headers to your requests, which we'll later use on the server-side.

    TypeError: Cannot read properties of undefined

    If you see the error `TypeError: Cannot read properties of undefined (reading '...')` this is likely because you tried to call a posthog function when posthog was not initialized (such as during the initial render). On purpose, we still render the children even if PostHog is not initialized so that your app still loads even if PostHog can't load.

    To fix this error, add a check that posthog has been initialized such as:

    React

    PostHog AI

    ```jsx
    useEffect(() => {
      posthog?.capture('test') // using optional chaining (recommended)
      if (posthog) {
        posthog.capture('test') // using an if statement
      }
    }, [posthog])
    ```

    Typescript helps protect against these errors.

4.  ## Verify client-side events are captured

    Checkpoint

    *Confirm that you can capture client-side events and see them in your PostHog project*

    At this point, you should be able to capture client-side events and see them in your PostHog project. This includes basic events like page views and button clicks that are [autocaptured](/docs/product-analytics/autocapture.md).

    You can also try to capture a custom event to verify it's working. You can access PostHog in any component using the `usePostHog` hook.

    TSX

    PostHog AI

    ```jsx
    import { usePostHog } from '@posthog/react'
    function App() {
      const posthog = usePostHog()
      return <button onClick={() => posthog?.capture('button_clicked')}>Click me</button>
    }
    ```

    You should see these events in a minute or two in the [activity tab](https://app.posthog.com/activity/explore).

5.  4

    ## Access PostHog methods

    Required

    On the client-side, you can access the PostHog client using the `usePostHog` hook. This hook returns the initialized PostHog client, which you can use to call PostHog methods. For example:

    TSX

    PostHog AI

    ```jsx
    import { usePostHog } from '@posthog/react'
    function App() {
      const posthog = usePostHog()
      return <button onClick={() => posthog?.capture('button_clicked')}>Click me</button>
    }
    ```

    For a complete list of available methods, see the [posthog-js documentation](/docs/libraries/js.md).

6.  5

    ## Identify your user

    Recommended

    Now that you can capture basic client-side events, you'll want to identify your user so you can associate users with captured events.

    Generally, you identify users when they log in or when they input some identifiable information (e.g. email, name, etc.). You can identify users by calling the `identify` method on the PostHog client:

    TSX

    PostHog AI

    ```jsx
    export default function Login() {
      const { user, login } = useAuth();
      const posthog = usePostHog();
      const handleLogin = async (e: React.FormEvent) => {
        // existing code to handle login...
        const user = await login({ email, password });
        posthog?.identify(user.email,
          {
            email: user.email,
            name: user.name,
          }
        );
        posthog?.capture('user_logged_in');
      };
      return (
        <div>
          {/* ... existing code ... */}
          <button onClick={handleLogin}>Login</button>
        </div>
      );
    }
    ```

    PostHog automatically generates anonymous IDs for users before they're identified. When you call identify, a new identified person is created. All previous events tracked with the anonymous ID link to the new identified distinct ID, and all future captures on the same browser associate with the identified person.

7.  6

    ## Create an error boundary

    Recommended

    PostHog can capture exceptions thrown in your app through an error boundary. React Router in framework mode has a built-in error boundary that you can use to capture exceptions. You can create an error boundary by exporting `ErrorBoundary` from your `app/root.tsx` file.

    app/root.tsx

    PostHog AI

    ```jsx
    import { usePostHog } from '@posthog/react'
    export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
      const posthog = usePostHog();
      posthog?.captureException(error);
      // other error handling code...
      return (
        <div>
          <h1>Something went wrong</h1>
          <p>{error.message}</p>
        </div>
      );
    }
    ```

    This automatically captures exceptions thrown in your React Router app using the `posthog.captureException()` method.

8.  7

    ## Tracking element visibility

    Recommended

    The `PostHogCaptureOnViewed` component enables you to automatically capture events when elements scroll into view in the browser. This is useful for tracking impressions of important content, monitoring user engagement with specific sections, or understanding which parts of your page users are actually seeing.

    The component wraps your content and sends a `$element_viewed` event to PostHog when the wrapped element becomes visible in the viewport. It only fires once per component instance.

    **Basic usage:**

    React

    PostHog AI

    ```jsx
    import { PostHogCaptureOnViewed } from '@posthog/react'
    function App() {
        return (
            <PostHogCaptureOnViewed name="hero-banner">
                <div>Your important content here</div>
            </PostHogCaptureOnViewed>
        )
    }
    ```

    **With custom properties:**

    You can include additional properties with the event to provide more context:

    React

    PostHog AI

    ```jsx
    <PostHogCaptureOnViewed
        name="product-card"
        properties={{
            product_id: '123',
            category: 'electronics',
            price: 299.99
        }}
    >
        <ProductCard />
    </PostHogCaptureOnViewed>
    ```

    **Tracking multiple children:**

    Use `trackAllChildren` to track each child element separately. This is useful for galleries or lists where you want to know which specific items were viewed:

    React

    PostHog AI

    ```jsx
    <PostHogCaptureOnViewed
        name="product-gallery"
        properties={{ gallery_type: 'featured' }}
        trackAllChildren
    >
        <ProductCard id="1" />
        <ProductCard id="2" />
        <ProductCard id="3" />
    </PostHogCaptureOnViewed>
    ```

    When `trackAllChildren` is enabled, each child element sends its own event with a `child_index` property indicating its position.

    **Custom intersection observer options:**

    You can customize when elements are considered "viewed" by passing options to the `IntersectionObserver`:

    React

    PostHog AI

    ```jsx
    <PostHogCaptureOnViewed
        name="footer"
        observerOptions={{
            threshold: 0.5,  // Element is 50% visible
            rootMargin: '0px'
        }}
    >
        <Footer />
    </PostHogCaptureOnViewed>
    ```

    The component passes all other props to the wrapper `div`, so you can add styling, classes, or other HTML attributes as needed.

9.  8

    ## Install server-side SDKs

    Recommended

    Install the [PostHog Node SDK](/docs/libraries/node.md) using your package manager. This is the SDK you'll use to capture server-side events.

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

10.  9

     ## Create a server-side middleware

     Recommended

     Next, create a server-side middleware to help you capture server-side events. This middleware helps you achieve the following:

     -   Initialize a PostHog client
     -   Fetch the session and distinct ID from the `X-POSTHOG-SESSION-ID` and `X-POSTHOG-DISTINCT-ID` headers and pass them to your request as a [context](/docs/libraries/node.md#contexts). This automatically identifies the user and session for you in all subsequent event captures.
     -   Calls `shutdown()` on the PostHog client to ensure all events are sent before the request is completed.

     app/lib/posthog-middleware.ts

     PostHog AI

     ```typescript
     import { PostHog } from "posthog-node";
     import type { RouterContextProvider } from "react-router";
     import type { Route } from "../+types/root";
     export interface PostHogContext extends RouterContextProvider {
       posthog?: PostHog;
     }
     export const posthogMiddleware: Route.MiddlewareFunction = async ({ request, context }, next) => {
       const posthog = new PostHog(process.env.VITE_POSTHOG_PROJECT_TOKEN!, {
         host: process.env.VITE_POSTHOG_HOST!,
         flushAt: 1,
         flushInterval: 0,
       });
       const sessionId = request.headers.get('X-POSTHOG-SESSION-ID');
       const distinctId = request.headers.get('X-POSTHOG-DISTINCT-ID');
       (context as PostHogContext).posthog = posthog;
       const response = await posthog.withContext(
         { sessionId: sessionId ?? undefined, distinctId: distinctId ?? undefined },
         next
       );
       await posthog.shutdown().catch(() => {});
       return response;
     };
     ```

     Then, you'll need to register the middleware in your app in the `app/root.tsx` file by exporting it in the `Route.MiddlewareFunction[]` array.

     app/root.tsx

     PostHog AI

     ```jsx
     import { posthogMiddleware } from './lib/posthog-middleware';
     export const middleware: Route.MiddlewareFunction[] = [
       posthogMiddleware,
       // other middlewares...
     ];
     ```

11.  ## Verify server-side events are captured

     Checkpoint

     *Confirm that you can capture server-side events and see them in your PostHog project*

     At this point, you should be able to capture server-side events and see them in your PostHog project.

     In a route, you can access the PostHog client from the context and capture an event. The middleware assigns the session ID and the distinct ID. This ensures that the system associates events with the correct user and session.

     app/routes/api.checkout.ts

     PostHog AI

     ```jsx
     import type { PostHogContext } from "../lib/posthog-middleware";
     export async function action({ request, context }: Route.ActionArgs) {
       const body = await request.json();
       // ... existing code ...
       // Access the PostHog client from the context and capture an event
       const posthog = (context as PostHogContext).posthog;
       posthog?.capture({ event: 'checkout_completed' });
       return Response.json({
         success: true,
         // ... existing code ...
       });
     }
     ```

12.  10

     ## Next steps

     Recommended

     Now that you've set up PostHog for React Router, you can start capturing events and exceptions in your app.

     To get the most out of PostHog, you should familiarize yourself with the following:

     -   [PostHog Web SDK docs](/docs/libraries/js.md): Learn more about the PostHog Web SDK and how to use it on the client-side.
     -   [PostHog Node SDK docs](/docs/libraries/node.md): Learn more about the PostHog Node SDK and how to use it on the server-side.
     -   [Identify users](/docs/product-analytics/identify.md): Learn more about how to identify users in your app.
     -   [Group analytics](/docs/product-analytics/group-analytics.md): Learn more about how to use group analytics in your app.
     -   [PostHog AI](/docs/posthog-ai.md): After capturing events, use PostHog AI to help you understand your data and build insights.
     -   [Feature flags and experiments](/docs/libraries/react.md#feature-flags): Feature flag and experiment setup is the same as React. You can find more details in the React integration guide.

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better