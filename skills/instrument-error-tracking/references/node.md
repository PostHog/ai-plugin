> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Node.js Error Tracking installation - Docs

Copy page

# Node.js Error Tracking installation - Docs

1.  1

    ## Install the package

    Required

    Install the PostHog Node.js library using your package manager:

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

2.  2

    ## Initialize PostHog

    Required

    Initialize the PostHog client with your project token:

    Node.js

    PostHog AI

    ```javascript
    import { PostHog } from 'posthog-node'
    const client = new PostHog(
        '<ph_project_token>',
        {
            host: 'https://us.i.posthog.com'
        }
    )
    ```

3.  3

    ## Send an event

    Recommended

    Once installed, you can manually send events to test your integration:

    Node.js

    PostHog AI

    ```javascript
    client.capture({
        distinctId: 'distinct_id_of_the_user',
        event: 'event_name',
        properties: {
            property1: 'value',
            property2: 'value',
        },
    })
    ```

4.  4

    ## Configure exception autocapture

    Recommended

    You can enable exception autocapture when initializing the PostHog client to automatically capture uncaught exceptions and unhandled rejections in your Node app.

    Node.js

    PostHog AI

    ```javascript
    import { PostHog } from 'posthog-node'
    const client = new PostHog(
        '<ph_project_token>',
        { host: 'https://us.i.posthog.com', enableExceptionAutocapture: true }
    )
    ```

    If you are using the Express framework, you will need to import and call `setupExpressErrorHandler` with your PostHog client and Express app. This is because Express handles uncaught exceptions internally meaning exception autocapture will not work by default.

    server.ts

    PostHog AI

    ```javascript
    import express from 'express'
    import { PostHog, setupExpressErrorHandler } from 'posthog-node'
    const app = express()
    const posthog = new PostHog(POSTHOG_PROJECT_TOKEN)
    setupExpressErrorHandler(posthog, app)
    ```

    > **Note:** Error tracking requires access the file system to process stack traces. Some providers, like Cloudflare Workers, do not support Node.js runtime APIs by default and need to be [included as per their documentation](https://developers.cloudflare.com/workers/runtime-apis/nodejs/#nodejs-compatibility).

5.  5

    ## Manually capture exceptions

    Optional

    If you need to manually capture exceptions, you can do so by calling the `captureException` method:

    Node.js

    PostHog AI

    ```javascript
    posthog.captureException(e, 'user_distinct_id', additionalProperties)
    ```

    This is helpful if you've built your own error handling logic or want to capture exceptions normally handled by the framework.

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

    [Upload source maps](/docs/error-tracking/upload-source-maps/node.md)

### Still have questions?

Ask PostHog AI

### Was this page useful?

HelpfulCould be better