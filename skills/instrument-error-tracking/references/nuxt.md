# Nuxt error tracking installation (v3.7 and above) - Docs

1.  1

    ## Install the PostHog Nuxt module

    Required

    Install the PostHog Nuxt module using your package manager:

    PostHog AI

    ### npm

    ```bash
    npm install @posthog/nuxt
    ```

    ### yarn

    ```bash
    yarn add @posthog/nuxt
    ```

    ### pnpm

    ```bash
    pnpm add @posthog/nuxt
    ```

    ### bun

    ```bash
    bun add @posthog/nuxt
    ```

    Add the module to your `nuxt.config.ts` file:

    nuxt.config.ts

    PostHog AI

    ```typescript
    export default defineNuxtConfig({
      modules: ['@posthog/nuxt'],
      // Enable source maps generation in both vue and nitro
      sourcemap: {
        client: 'hidden'
      },
      nitro: {
        rollupConfig: {
          output: {
            sourcemapExcludeSources: false,
          },
        },
      },
      posthogConfig: {
        publicKey: '<ph_project_token>', // Find it in project settings https://app.posthog.com/settings/project
        host: 'https://us.i.posthog.com', // Optional: defaults to https://us.i.posthog.com. Use https://eu.i.posthog.com for EU region
        clientConfig: {
          capture_exceptions: true, // Enables automatic exception capture on the client side (Vue)
        },
        serverConfig: {
          enableExceptionAutocapture: true, // Enables automatic exception capture on the server side (Nitro)
        },
        sourcemaps: {
          enabled: true,
          project: '<ph_project_id>', // Your project ID from PostHog settings https://app.posthog.com/settings/environment#variables
          personalApiKey: '<ph_personal_api_key>', // Your personal API key from PostHog settings https://app.posthog.com/settings/user-api-keys (requires organization:read and error_tracking:write scopes)
          releaseName: 'my-application', // Optional: defaults to git repository name
          releaseVersion: '1.0.0', // Optional: defaults to current git commit
        },
      },
    })
    ```

    **Personal API key**

    Your personal API key will require `organization:read` and `error_tracking:write` scopes.

    The module will automatically:

    -   Initialize PostHog on both Vue (client side) and Nitro (server side)
    -   Capture exceptions on both client and server
    -   Generate and upload source maps during build

2.  2

    ## Manually capturing exceptions

    Optional

    Our module if set up as shown above already captures both client and server side exceptions automatically.

    To send errors manually on the client side, import it and use the `captureException` method like this:

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

    On the server side instantiate PostHog using:

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

3.  3

    ## Build your project for production

    Required

    Build your project for production by running the following command:

    Terminal

    PostHog AI

    ```bash
    nuxt build
    ```

    The PostHog module will automatically **generate and upload source maps** to PostHog during the build process.

4.  ## Verify error tracking

    Recommended

    *Confirm events are being sent to PostHog*

    Before proceeding, let's make sure exception events are being captured and sent to PostHog. You should see events appear in the activity feed.

    ![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_ouxl_f788dd8cd2.png)![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_owae_7c3490822c.png)

    [Check for exceptions in PostHog](https://app.posthog.com/activity/explore)

5.  4

    ## Upload source maps

    Required

    Great, you're capturing exceptions! If you serve minified bundles, the next step is to upload source maps to generate accurate stack traces.

    Let's continue to the next section.

    [Upload source maps](/docs/error-tracking/upload-source-maps/nuxt.md)

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better