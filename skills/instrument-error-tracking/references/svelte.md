# SvelteKit error tracking installation - Docs

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

    If you haven't created a root layout already, create a new file called `+layout.js` in your `src/routes` folder. Check the environment is the browser, and initialize PostHog if so:

    src/routes/+layout.js

    PostHog AI

    ```javascript
    import posthog from 'posthog-js'
    import { browser } from '$app/environment';
    import { onMount } from 'svelte';
    export const load = async () => {
      if (browser) {
        posthog.init(
          '<ph_project_token>',
          {
            api_host: 'https://us.i.posthog.com',
            defaults: '2026-05-30'
          }
        )
      }
      return
    };
    ```

    **SvelteKit layout**

    Learn more about [SvelteKit layouts](https://kit.svelte.dev/docs/routing#layout) in the official documentation.

3.  3

    ## Server-side setup

    Optional

    Install `posthog-node` using your package manager:

    PostHog AI

    ### npm

    ```bash
    npm install posthog-node --save
    ```

    ### yarn

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

    Then, initialize the PostHog Node client where you'd like to use it on the server side. For example, in a load function:

    routes/+page.server.js

    PostHog AI

    ```javascript
    import { PostHog } from 'posthog-node';
    export async function load() {
      const posthog = new PostHog('<ph_project_token>', { host: 'https://us.i.posthog.com' });
      posthog.capture({
        distinctId: 'distinct_id_of_the_user',
        event: 'event_name',
      })
      await posthog.shutdown()
    }
    ```

    **Note**

    Make sure to always call `posthog.shutdown()` after capturing events from the server-side. PostHog queues events into larger batches, and this call forces all batched events to be flushed immediately.

4.  4

    ## Send events

    Click around and view a couple pages to generate some events. PostHog automatically captures pageviews, clicks, and other interactions for you.

    If you'd like, you can also manually capture custom events:

    JavaScript

    PostHog AI

    ```javascript
    posthog.capture('my_custom_event', { property: 'value' })
    ```

5.  5

    ## Set up client-side exception capture

    Required

    [SvelteKit Hooks](https://svelte.dev/docs/kit/hooks) can be used to capture exceptions in the client and server-side.

    Capture exceptions in the `handleError` callback in your client-side hooks file:

    src/hooks.client.js

    PostHog AI

    ```javascript
    import posthog from 'posthog-js';
    import type { HandleClientError } from '@sveltejs/kit';
    export const handleError = ({ error, status }: HandleClientError) => {
      // SvelteKit 2.0 offers a reliable way to check for a 404 error:
      if (status !== 404) {
          posthog.captureException(error);
      }
    };
    ```

6.  6

    ## Set up server-side exception capture

    Required

    To capture exceptions on the server-side, you will also need to implement the `handleError` callback:

    src/hooks.server.ts

    PostHog AI

    ```javascript
    import type { HandleServerError } from '@sveltejs/kit';
    import { PostHog } from 'posthog-node';
    const client = new PostHog(
      '<ph_project_token>',
      { host: 'https://us.i.posthog.com' }
    )
    export const handleError = async ({ error, status }: HandleServerError) => {
      if (status !== 404) {
          client.captureException(error);
          await client.shutdown();
      }
    };
    ```

7.  ## Verify error tracking

    Recommended

    *Confirm events are being sent to PostHog*

    Before proceeding, let's make sure exception events are being captured and sent to PostHog. You should see events appear in the activity feed.

    ![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_ouxl_f788dd8cd2.png)![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_owae_7c3490822c.png)

    [Check for exceptions in PostHog](https://app.posthog.com/activity/explore)

8.  7

    ## Upload source maps

    Required

    Great, you're capturing exceptions! If you serve minified bundles, the next step is to upload source maps to generate accurate stack traces.

    Let's continue to the next section.

    [Upload source maps](/docs/error-tracking/upload-source-maps/web.md)

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better