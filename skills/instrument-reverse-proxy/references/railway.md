> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Railway reverse proxy

Canonical URL: https://posthog.com/docs/advanced/proxy/railway

## On this page

- [How it works](#how-it-works)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Deploy the template](#deploy-the-template)
- [Configure your region](#configure-your-region)
- [Wait for deployment](#wait-for-deployment)
- [Update your PostHog SDK](#update-your-posthog-sdk)
- [Add a custom domain](#add-a-custom-domain)
- [Verify your setup](#verify-your-setup)
- [Troubleshooting](#troubleshooting)

**Before you start**

-   If you use a self-hosted proxy, PostHog can't help troubleshoot. Use [our managed reverse proxy](https://posthog.com/docs/advanced/proxy/managed-reverse-proxy.md) if you want support.
-   Use domains matching your PostHog region: `us.i.posthog.com` for US, `eu.i.posthog.com` for EU.
-   Don't use obvious path names like `/analytics`, `/tracking`, `/telemetry`, or `/posthog`. Blockers will catch them. Use something unique to your app instead.

**Data transfer costs**

Proxying routes all PostHog traffic – events, session recordings, feature flag polls, and SDK assets – through your Railway service, which bills [egress per-GB](https://railway.app/pricing) on usage-based plans. Session recordings are the biggest driver (often 1–5 MB per session) and can make Railway costs noticeable on high-traffic sites.

To avoid these costs, use the [managed reverse proxy](https://posthog.com/docs/advanced/proxy/managed-reverse-proxy.md) (free for PostHog Cloud users) or a provider without egress fees like [Cloudflare Workers](https://posthog.com/docs/advanced/proxy/cloudflare.md).

This guide shows you how to deploy a PostHog reverse proxy on [Railway](https://railway.app/).

## How it works

Railway provides a one-click deployment template that runs an nginx-based reverse proxy. When deployed, Railway gives you a domain that routes all requests to PostHog's servers.

Here's the request flow:

1.  User triggers an event in your app
2.  Request goes to your Railway domain (e.g., `your-project.up.railway.app`)
3.  The nginx proxy running on Railway forwards the request to PostHog
4.  PostHog processes the request and returns a response
5.  The proxy returns PostHog's response to the user

This works because ad blockers see requests going to Railway's domain (or your custom domain), not PostHog's.

## Prerequisites

This guide requires a [Railway account](https://railway.app/) (free tier works).

## Setup

1.  1

    ## Deploy the template

    Click the button below to deploy a pre-configured PostHog reverse proxy on Railway:

    [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/posthog-proxy?referralCode=FQRCYT)

    This template deploys an nginx container configured to proxy requests to PostHog.

2.  2

    ## Configure your region

    During deployment, Railway prompts you to set the `POSTHOG_CLOUD_REGION` environment variable:

    -   Set to `us` for US region
    -   Set to `eu` for EU region

    This tells the proxy which PostHog servers to forward requests to. Make sure this matches your PostHog project's region.

3.  3

    ## Wait for deployment

    Railway automatically builds and deploys your proxy. This usually takes 1-2 minutes.

    Once deployed, Railway provides you with a domain like `your-project-name.up.railway.app`. You can find this in your project's **Settings** → **Networking** section.

4.  4

    ## Update your PostHog SDK

    In your application code, update your PostHog initialization to use your Railway domain:

    ### US

    ```javascript
    posthog.init('<ph_project_token>', {
      api_host: 'https://your-project-name.up.railway.app',
      ui_host: 'https://us.posthog.com'
    })
    ```

    ### EU

    ```javascript
    posthog.init('<ph_project_token>', {
      api_host: 'https://your-project-name.up.railway.app',
      ui_host: 'https://eu.posthog.com'
    })
    ```

    Replace `your-project-name.up.railway.app` with your actual Railway domain.

5.  5

    ## Add a custom domain

    Optional

    For better blocking resistance, use your own domain instead of Railway's default:

    1.  Go to your Railway project's **Settings** → **Networking**
    2.  Click **Add Domain**
    3.  Follow [Railway's custom domains guide](https://docs.railway.app/guides/public-networking#custom-domains) to configure DNS

    Then update your SDK to use your custom domain:

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

6.  ## Verify your setup

    Checkpoint

    Confirm events are flowing through your proxy:

    1.  Test the proxy directly:

        ```bash
        curl -I https://your-project-name.up.railway.app/flags?v=2
        ```

        You should see a `200 OK` response.

    2.  Open your browser's developer tools and go to the **Network** tab

    3.  Trigger an event in your app

    4.  Look for requests to your Railway domain

    5.  Verify the response status is `200 OK`

    6.  Check the [PostHog app](https://app.posthog.com) to confirm events appear

    If you see errors, check [troubleshooting](#troubleshooting) below.

## Troubleshooting

### Proxy stops working periodically

If your proxy stops responding intermittently:

1.  **Check sleep settings:** Free tier services may sleep after inactivity. Go to **Settings** → **Service** and check if sleep mode is enabled.
2.  **Monitor resource usage:** Check the **Metrics** tab for memory or CPU spikes that might cause restarts.
3.  **View logs:** Look for error messages in the **Deployments** tab.
4.  **Consider upgrading:** Paid plans include better uptime guarantees and disable sleep mode.

If issues persist, check [Railway's status page](https://status.railway.app/).

### Deployment failed

If the initial deployment fails:

1.  Check the build logs for error messages
2.  Verify you set the `POSTHOG_CLOUD_REGION` variable correctly (must be `us` or `eu`)
3.  Try redeploying from the Railway dashboard

### 502 Bad Gateway errors

If the proxy returns 502 errors:

1.  Verify the `POSTHOG_CLOUD_REGION` variable matches your PostHog project's region
2.  Check that the Railway service is running in the dashboard
3.  View the service logs for connection errors
