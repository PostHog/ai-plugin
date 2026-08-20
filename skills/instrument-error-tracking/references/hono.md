> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Hono Error Tracking installation - Docs

Copy page

# Hono Error Tracking installation - Docs

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

    ## Exception handling example

    Required

    Hono uses [`app.onError`](https://hono.dev/docs/api/exception#handling-httpexception) to handle uncaught exceptions. You can take advantage of this for error tracking.

    Remember to **export** your [project token](https://app.posthog.com/settings/project#variables) as an environment variable.

    index.ts

    PostHog AI

    ```typescript
    import { PostHog } from 'posthog-node'
    const posthog = new PostHog(process.env.POSTHOG_TOKEN, { host: 'https://us.i.posthog.com' })
    app.onError(async (err, c) => {
      posthog.captureException(err, 'user_distinct_id_with_err_rethrow', {
        path: c.req.path,
        method: c.req.method,
        url: c.req.url,
        headers: c.req.header(),
        // ... other properties
      })
      await posthog.flush()
      // other error handling logic
      return c.text('Internal Server Error', 500)
    })
    ```

5.  ## Verify error tracking

    Recommended

    *Confirm events are being sent to PostHog*

    Before proceeding, let's make sure exception events are being captured and sent to PostHog. You should see events appear in the activity feed.

    ![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_ouxl_f788dd8cd2.png)![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_owae_7c3490822c.png)

    [Check for exceptions in PostHog](https://app.posthog.com/activity/explore)

6.  5

    ## Upload source maps

    Required

    Great, you're capturing exceptions! If you serve minified bundles, the next step is to upload source maps to generate accurate stack traces.

    Let's continue to the next section.

    [Upload source maps](/docs/error-tracking/upload-source-maps.md)

### Still have questions?

Ask PostHog AI

### Was this page useful?

HelpfulCould be better