> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Pomerium reverse proxy

Canonical URL: https://posthog.com/docs/advanced/proxy/pomerium

## On this page

- [How it works](#how-it-works)
- [Prerequisites](#prerequisites)
- [Choose your setup option](#choose-your-setup-option)
- [Option 1: Pomerium Zero](#option-1-pomerium-zero)
- [Create a public access policy](#create-a-public-access-policy)
- [Create the PostHog routes](#create-the-posthog-routes)
- [Update your PostHog SDK](#update-your-posthog-sdk)
- [Verify your setup](#verify-your-setup)
- [Option 2: Pomerium Core](#option-2-pomerium-core)
- [Add routes to your config](#add-routes-to-your-config)
- [Reload Pomerium](#reload-pomerium)
- [Update your PostHog SDK](#update-your-posthog-sdk-1)
- [Verify your setup](#verify-your-setup-1)
- [Troubleshooting](#troubleshooting)

**Before you start**

-   If you use a self-hosted proxy, PostHog can't help troubleshoot. Use [our managed reverse proxy](https://posthog.com/docs/advanced/proxy/managed-reverse-proxy.md) if you want support.
-   Use domains matching your PostHog region: `us.i.posthog.com` for US, `eu.i.posthog.com` for EU.
-   Don't use obvious path names like `/analytics`, `/tracking`, `/telemetry`, or `/posthog`. Blockers will catch them. Use something unique to your app instead.

This guide shows you how to use [Pomerium](https://www.pomerium.com/) as a reverse proxy for PostHog.

## How it works

Pomerium is an identity-aware proxy that sits between your users and backend services. For PostHog, you configure Pomerium to route requests from your domain to PostHog's servers with public access enabled (no authentication required).

Here's the request flow:

1.  User triggers an event in your app
2.  Request goes to your Pomerium proxy (e.g., `e.yourdomain.com`)
3.  Pomerium matches the request to a route and checks the policy
4.  With public access enabled, Pomerium forwards the request to PostHog
5.  PostHog's response is returned to the user under your domain

**Why public access?** Unlike typical Pomerium use cases where you want to authenticate users, PostHog analytics should work for all visitors including anonymous users. You'll create a policy that allows unauthenticated access.

## Prerequisites

-   A domain with DNS pointing to your Pomerium instance
-   Either a [Pomerium Zero](https://www.pomerium.com/zero) account or [Pomerium Core](https://www.pomerium.com/docs/deploy/core) installed

## Choose your setup option

Both options accomplish the same goal. Choose based on your Pomerium deployment:

-   [**Pomerium Zero:**](#option-1-pomerium-zero) The managed service with a web-based UI. Use this if you want the simplest setup without managing infrastructure.
-   [**Pomerium Core:**](#option-2-pomerium-core) The self-hosted version configured with YAML files. Use this if you're already running Pomerium Core or prefer configuration as code.

## Option 1: Pomerium Zero

Pomerium Zero uses a web-based console for configuration. You'll create a policy and two routes.

1.  1

    ## Create a public access policy

    In the Pomerium Zero console, create a new policy with public access enabled. This allows unauthenticated requests to pass through, which is required for PostHog analytics to work for all visitors.

    Configure these settings:

    | Setting | Value |
    | --- | --- |
    | Name | `allow-all` or similar |
    | Policy Enforcement | Optional |
    | Public Access | Enabled in overrides section |

    See [Pomerium's policy documentation](https://www.pomerium.com/docs/capabilities/authorization) for detailed instructions.

2.  2

    ## Create the PostHog routes

    Create two routes in the Pomerium Zero console, both using the public access policy you created:

    | Route | From | To | Path prefix |
    | --- | --- | --- | --- |
    | PostHog | `https://e.yourdomain.com` | `https://us.i.posthog.com` | none |
    | PostHog Assets (static) | `https://e.yourdomain.com` | `https://us-assets.i.posthog.com` | `/static` |
    | PostHog Assets (array) | `https://e.yourdomain.com` | `https://us-assets.i.posthog.com` | `/array` |

    Replace `e.yourdomain.com` with your subdomain. Replace `us` with `eu` for EU region.

    The assets routes need the `/static` and `/array` prefixes so they only match requests for PostHog's JavaScript SDK, remote config, and other static files. All other requests go to the main route.

    See [Pomerium's routing documentation](https://www.pomerium.com/docs/capabilities/routing) for detailed instructions.

3.  3

    ## Update your PostHog SDK

    In your application code, update your PostHog initialization:

    ### US

    ```javascript
    posthog.init('<ph_project_token>', {
      api_host: 'https://e.yourdomain.com',
      ui_host: 'https://us.posthog.com'
    })
    ```

    ### EU

    ```javascript
    posthog.init('<ph_project_token>', {
      api_host: 'https://e.yourdomain.com',
      ui_host: 'https://eu.posthog.com'
    })
    ```

    Replace `e.yourdomain.com` with your actual subdomain.

4.  ## Verify your setup

    Checkpoint

    Confirm events are flowing through your proxy:

    1.  Open your browser's developer tools and go to the **Network** tab
    2.  Trigger an event in your app
    3.  Look for requests to your subdomain (e.g., `e.yourdomain.com`)
    4.  Verify the response status is `200 OK` and you're not prompted to authenticate
    5.  Check the [PostHog app](https://app.posthog.com) to confirm events appear

    If you see errors, check [troubleshooting](#troubleshooting) below.

## Option 2: Pomerium Core

1.  1

    ## Add routes to your config

    Add these routes to your Pomerium `config.yaml`:

    ### US

    ```yaml
    routes:
      - from: https://e.yourdomain.com
        to: https://us.i.posthog.com
        policy:
          - allow:
              or:
                - public: true
        name: "PostHog"
    
      - from: https://e.yourdomain.com
        to: https://us-assets.i.posthog.com
        prefix: "/static"
        policy:
          - allow:
              or:
                - public: true
        name: "PostHog Assets (static)"
    
      - from: https://e.yourdomain.com
        to: https://us-assets.i.posthog.com
        prefix: "/array"
        policy:
          - allow:
              or:
                - public: true
        name: "PostHog Assets (array)"
    ```

    ### EU

    ```yaml
    routes:
      - from: https://e.yourdomain.com
        to: https://eu.i.posthog.com
        policy:
          - allow:
              or:
                - public: true
        name: "PostHog"
    
      - from: https://e.yourdomain.com
        to: https://eu-assets.i.posthog.com
        prefix: "/static"
        policy:
          - allow:
              or:
                - public: true
        name: "PostHog Assets (static)"
    
      - from: https://e.yourdomain.com
        to: https://eu-assets.i.posthog.com
        prefix: "/array"
        policy:
          - allow:
              or:
                - public: true
        name: "PostHog Assets (array)"
    ```

    Replace `e.yourdomain.com` with your subdomain.

    The `public: true` policy allows unauthenticated access. The `prefix` values ensure the assets routes only match static file and remote config requests.

    See [Pomerium's routes documentation](https://www.pomerium.com/docs/reference/routes) for more configuration options.

2.  2

    ## Reload Pomerium

    Apply the configuration changes:

    ```bash
    pomerium-cli config check  # Validate your config
    systemctl reload pomerium  # Or your preferred restart method
    ```

3.  3

    ## Update your PostHog SDK

    In your application code, update your PostHog initialization:

    ### US

    ```javascript
    posthog.init('<ph_project_token>', {
      api_host: 'https://e.yourdomain.com',
      ui_host: 'https://us.posthog.com'
    })
    ```

    ### EU

    ```javascript
    posthog.init('<ph_project_token>', {
      api_host: 'https://e.yourdomain.com',
      ui_host: 'https://eu.posthog.com'
    })
    ```

    Replace `e.yourdomain.com` with your actual subdomain.

4.  ## Verify your setup

    Checkpoint

    Confirm events are flowing through your proxy:

    1.  Test the proxy directly:

        ```bash
        curl -I https://e.yourdomain.com/flags?v=2
        ```

        You should see a `200 OK` response without authentication prompts.

    2.  Open your browser's developer tools and go to the **Network** tab

    3.  Trigger an event in your app

    4.  Look for requests to your subdomain

    5.  Check the [PostHog app](https://app.posthog.com) to confirm events appear

    If you see errors, check [troubleshooting](#troubleshooting) below.

## Troubleshooting

### Authentication prompts appearing

If users are prompted to log in when accessing your proxy, verify your policy has public access enabled and is applied to both routes. See [Pomerium's authorization documentation](https://www.pomerium.com/docs/capabilities/authorization) for policy configuration details.

### 404 errors on static assets

If the PostHog SDK fails to load, verify the assets routes have the `/static` and `/array` prefixes configured and point to the correct domain (`us-assets.i.posthog.com` or `eu-assets.i.posthog.com`).

### DNS not resolving

If your subdomain doesn't resolve, verify your DNS records point to your Pomerium instance. For Pomerium Zero, check [Pomerium's networking documentation](https://www.pomerium.com/docs/capabilities/routing) to ensure the subdomain is configured correctly.
