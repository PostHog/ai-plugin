# Nuxt error tracking installation (v3.6 and below) - Docs

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

    **Nuxt version**

    This guide is for Nuxt v3.0 and above. For Nuxt v2.16 and below, see our [Nuxt docs](/docs/libraries/nuxt-js.md#nuxt-v216-and-below).

2.  2

    ## Add environment variables

    Required

    Add your PostHog project token and host to your `nuxt.config.js` file:

    nuxt.config.js

    PostHog AI

    ```javascript
    export default defineNuxtConfig({
      runtimeConfig: {
        public: {
          posthogPublicKey: '<ph_project_token>',
          posthogHost: 'https://us.i.posthog.com',
          posthogDefaults: '2026-05-30'
        }
      }
    })
    ```

3.  3

    ## Create a plugin

    Required

    Create a new plugin by creating a new file `posthog.client.js` in your plugins directory:

    plugins/posthog.client.js

    PostHog AI

    ```javascript
    import { defineNuxtPlugin } from '#app'
    import posthog from 'posthog-js'
    export default defineNuxtPlugin(nuxtApp => {
      const runtimeConfig = useRuntimeConfig();
      const posthogClient = posthog.init(runtimeConfig.public.posthogPublicKey, {
        api_host: runtimeConfig.public.posthogHost,
        defaults: runtimeConfig.public.posthogDefaults,
        loaded: (posthog) => {
          if (import.meta.env.MODE === 'development') posthog.debug();
        }
      })
      return {
        provide: {
          posthog: () => posthogClient
        }
      }
    })
    ```

4.  4

    ## Server-side setup

    Optional

    To capture events from server routes, install `posthog-node` and instantiate it directly. You can also use it to evaluate feature flags on the server:

    PostHog AI

    ### npm

    ```bash
    npm install posthog-node
    ```

    ### yarn

    ```bash
    yarn add posthog-node
    ```

    ### pnpm

    ```bash
    pnpm add posthog-node
    ```

    server/api/example.js

    PostHog AI

    ```javascript
    import { PostHog } from 'posthog-node'
    export default defineEventHandler(async (event) => {
        const runtimeConfig = useRuntimeConfig()
        const posthog = new PostHog(
            runtimeConfig.public.posthogPublicKey,
            { host: runtimeConfig.public.posthogHost }
        )
        posthog.capture({
            distinctId: 'distinct_id_of_the_user',
            event: 'event_name'
        })
        await posthog.shutdown()
    })
    ```

5.  5

    ## Send events

    Click around and view a couple pages to generate some events. PostHog automatically captures pageviews, clicks, and other interactions for you.

    If you'd like, you can also manually capture custom events:

    JavaScript

    PostHog AI

    ```javascript
    posthog.capture('my_custom_event', { property: 'value' })
    ```

6.  6

    ## Manually capturing exceptions

    Optional

    To send errors directly using the PostHog client, import it and use the `captureException` method like this:

    Vue

    PostHog AI

    ```html
    <script>
      const { $posthog } = useNuxtApp()
      if ($posthog) {
        const posthog = $posthog()
        posthog.captureException(new Error("Important error message"))
      }
    </script>
    ```

    On the server side, you can use the `posthog` object directly.

    server/api/example.js

    PostHog AI

    ```javascript
    const runtimeConfig = useRuntimeConfig()
    const posthog = new PostHog(
      runtimeConfig.public.posthogPublicKey,
      {
        host: runtimeConfig.public.posthogHost,
      }
    );
    try {
      const results = await DB.query.users.findMany()
      return results
    } catch (error) {
      posthog.captureException(error)
    }
    ```

7.  7

    ## Configuring exception autocapture

    Recommended

    Update your `posthog.client.js` to add an error hook.

    JavaScript

    PostHog AI

    ```javascript
    export default defineNuxtPlugin((nuxtApp) => {
        ...
        nuxtApp.hook('vue:error', (error) => {
            posthogClient.captureException(error)
        })
        ...
    })
    ```

8.  ## Verify error tracking

    Recommended

    *Confirm events are being sent to PostHog*

    Before proceeding, let's make sure exception events are being captured and sent to PostHog. You should see events appear in the activity feed.

    ![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_ouxl_f788dd8cd2.png)![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_owae_7c3490822c.png)

    [Check for exceptions in PostHog](https://app.posthog.com/activity/explore)

9.  8

    ## Upload source maps

    Required

    Great, you're capturing exceptions! If you serve minified bundles, the next step is to upload source maps to generate accurate stack traces.

    Let's continue to the next section.

    [Upload source maps](/docs/error-tracking/upload-source-maps/nuxt.md)

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better