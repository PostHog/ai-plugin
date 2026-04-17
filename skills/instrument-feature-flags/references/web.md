# Web Feature Flags installation - Docs

1.  1

    ## Choose an installation method

    Required

    You can either add the JavaScript snippet directly to your HTML or install the JavaScript SDK via your package manager.

    ## HTML snippet

    Add this snippet to your website within the `<head>` tag. This can also be used in services like Google Tag Manager:

    HTML

    PostHog AI

    ```html
    <script>
        !function(t,e){var o,n,p,r;e.__SV||(window.posthog && window.posthog.__loaded)||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="init os ds Ie us vs ss ls capture calculateEventProperties register register_once register_for_session unregister unregister_for_session ws getFeatureFlag getFeatureFlagPayload getFeatureFlagResult isFeatureEnabled reloadFeatureFlags updateFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSurveysLoaded onSessionId getSurveys getActiveMatchingSurveys renderSurvey displaySurvey cancelPendingSurvey canRenderSurvey canRenderSurveyAsync identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset get_distinct_id getGroups get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording sessionRecordingStarted captureException startExceptionAutocapture stopExceptionAutocapture loadToolbar get_property getSessionProperty bs ps createPersonProfile setInternalOrTestUser ys es $s opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing get_explicit_consent_status is_capturing clear_opt_in_out_capturing cs debug M gs getPageViewId captureTraceFeedback captureTraceMetric Qr".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
        posthog.init('<ph_project_token>', {
            api_host: 'https://us.i.posthog.com',
            defaults: '2026-01-30',
        })
    </script>
    ```

    ## JavaScript SDK

    Install the PostHog JavaScript library using your package manager. Then, import and initialize the PostHog library with your project token and host:

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

    JavaScript

    PostHog AI

    ```javascript
    import posthog from 'posthog-js'
    posthog.init('<ph_project_token>', {
        api_host: 'https://us.i.posthog.com',
        defaults: '2026-01-30'
    })
    ```

2.  2

    ## Send events

    Recommended

    Once installed, PostHog will automatically start capturing events. You can also manually send events to test your integration:

    Click around and view a couple pages to generate some events. PostHog automatically captures pageviews, clicks, and other interactions for you.

    If you'd like, you can also manually capture custom events:

    JavaScript

    PostHog AI

    ```javascript
    posthog.capture('my_custom_event', { property: 'value' })
    ```

3.  3

    ## Use boolean feature flags

    Required

    Check if a feature flag is enabled:

    ```javascript
    if (posthog.isFeatureEnabled('flag-key')) {
        // Do something differently for this user
        // Optional: fetch the payload
        const matchedFlagPayload = posthog.getFeatureFlagPayload('flag-key')
    }
    ```

4.  4

    ## Use multivariate feature flags

    Optional

    For multivariate flags, check which variant the user has been assigned:

    ```javascript
    if (posthog.getFeatureFlag('flag-key') == 'variant-key') { // replace 'variant-key' with the key of your variant
        // Do something differently for this user
        // Optional: fetch the payload
        const matchedFlagPayload = posthog.getFeatureFlagPayload('flag-key')
    }
    ```

5.  5

    ## Use feature flag payloads

    Optional

    Feature flags can include payloads with additional data. Fetch the payload like this:

    ```javascript
    const matchedFlagPayload = posthog.getFeatureFlagPayload('flag-key')
    ```

6.  6

    ## Ensure flags are loaded

    Optional

    Every time a user loads a page, we send a request in the background to fetch the feature flags that apply to that user. We store those flags in your chosen persistence option (local storage by default).

    This means that for most pages, the feature flags are available immediately — **except for the first time a user visits**.

    To handle this, you can use the `onFeatureFlags` callback to wait for the feature flag request to finish:

    ```javascript
    posthog.onFeatureFlags(function (flags, flagVariants, { errorsLoading }) {
        // feature flags are guaranteed to be available at this point
        if (posthog.isFeatureEnabled('flag-key')) {
            // do something
        }
    })
    ```

7.  7

    ## Reload feature flags

    Optional

    Feature flag values are cached. If something has changed with your user and you'd like to refetch their flag values:

    ```javascript
    posthog.reloadFeatureFlags()
    ```

8.  8

    ## Running experiments

    Optional

    Experiments run on top of our feature flags. Once you've implemented the flag in your code, you run an experiment by creating a new experiment in the PostHog dashboard.

9.  9

    ## Next steps

    Recommended

    Now that you're evaluating flags, continue with the resources below to learn what else Feature Flags enables within the PostHog platform.

    | Resource | Description |
    | --- | --- |
    | [Creating a feature flag](/docs/feature-flags/creating-feature-flags.md) | How to create a feature flag in PostHog |
    | [Adding feature flag code](/docs/feature-flags/adding-feature-flag-code.md) | How to check flags in your code for all platforms |
    | [Framework-specific guides](/docs/feature-flags/tutorials.md#framework-guides) | Setup guides for React Native, Next.js, Flutter, and other frameworks |
    | [How to do a phased rollout](/tutorials/phased-rollout.md) | Gradually roll out features to minimize risk |
    | [More tutorials](/docs/feature-flags/tutorials.md) | Other real-world examples and use cases |

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better