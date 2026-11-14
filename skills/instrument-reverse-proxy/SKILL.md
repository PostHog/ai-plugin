---
name: instrument-reverse-proxy
description: >-
  Route PostHog's browser traffic through the app's own domain, so ad blockers
  don't drop events, session replays, and feature flag calls. Use when the user
  asks for a reverse proxy or agrees to one you suggested, for example after
  adding posthog-js or when events or recordings seem to be missing. Don't set
  one up unprompted. Prefers a self-hosted proxy where the app's platform makes
  it a small change, such as Next.js or Cloudflare, and PostHog's managed
  reverse proxy elsewhere.
metadata:
  author: PostHog
---

# Set up a PostHog reverse proxy

Use this skill to route the PostHog browser SDK's traffic through a domain the app owns. Ad blockers keep lists of analytics domains and block requests to them. Through a proxy, events, session replay data, feature flag calls, surveys, and the SDK's own scripts load from the app's domain, so ad blockers don't drop them.

A proxy is optional, and setting one up can take several steps the user has to do themselves, such as a DNS record. Set one up only when the user asked for it or agreed to your suggestion.

This skill covers the browser SDK: posthog-js and the snippet. Server-side SDKs don't need a proxy, so don't add one for them.

There are two ways to do it:

- **A self-hosted proxy.** A rewrite, edge function, or server route in the app's own hosting forwards a path, such as `/e`, to PostHog. On platforms with built-in rewrites or edge functions, it's a few lines of configuration.
- **PostHog's managed reverse proxy.** The user adds one DNS record for a subdomain, such as `e.example.com`, and PostHog runs the proxy, its TLS certificate, and its routing. It's free on PostHog Cloud, and no proxy code goes into the app.

### Trade-offs

| | Self-hosted proxy | Managed proxy |
| --- | --- | --- |
| Setup | Code or config in the app, deployed with it. No DNS change. | One CNAME record. Needs DNS access and an organization admin. |
| Blocking | A path on the app's own domain has no CNAME, so DNS-level blockers (NextDNS, Pi-hole) can't trace it back to PostHog. | DNS-level blockers that uncloak CNAMEs can see the record points at PostHog. Browser extensions can't. |
| Cost | Requests count against the platform's bandwidth and invocation quotas. Vercel, Netlify, CloudFront, and Railway bill for them, which adds up on high-traffic sites. | Free. Doesn't touch the app's hosting quotas. |
| Maintenance | The app owns it: routing, headers, body size limits. PostHog support can't troubleshoot it. | PostHog maintains it and offers a `proxy-diagnose` check. |
| Compliance | Runs wherever the app runs. Works for HIPAA and EU-only edge requirements. | Runs on Cloudflare, a PostHog subprocessor. Not HIPAA-compliant, and EU edge termination isn't guaranteed. |
| Availability | Any PostHog, including self-hosted. | PostHog Cloud only. An organization gets a limited number of proxies (`proxy-list` returns the limit). |

## Reference files

- `references/proxy-reference.md` - Self-hosted proxy reference
- `references/cloudflare.md` - Cloudflare reverse proxy
- `references/vercel.md` - Vercel reverse proxy
- `references/nextjs.md` - Next.js rewrites reverse proxy
- `references/nextjs-middleware.md` - Next.js proxy file reverse proxy
- `references/netlify.md` - Netlify reverse proxy
- `references/nuxt.md` - Nuxt reverse proxy
- `references/sveltekit.md` - Sveltekit reverse proxy
- `references/remix.md` - Remix reverse proxy
- `references/node.md` - Node reverse proxy
- `references/railway.md` - Railway reverse proxy
- `references/nginx.md` - Nginx reverse proxy
- `references/caddy.md` - Caddy reverse proxy
- `references/cloudfront.md` - Aws cloudfront reverse proxy
- `references/kubernetes-ingress-controller.md` - Kubernetes reverse proxy
- `references/pomerium.md` - Pomerium reverse proxy
- `references/proxy.md` - Deploy a reverse proxy
- `references/COMMANDMENTS.md` - Framework-specific rules the integration must follow

The overview reference covers the managed proxy: its steps, troubleshooting, and FAQ. Each platform reference shows a self-hosted proxy for one platform. When this page and a reference disagree on a platform's configuration, follow the reference.

## API tools

The managed proxy steps use PostHog API tools. The same tool names work through the PostHog MCP server (its `exec` tool) and through the hog CLI (`hog api call <tool> '<json input>'`).

- `proxy-list`: the organization's proxies, with their status, and the most the plan allows.
- `proxy-create`: creates a proxy for a domain. Returns its `id` and the `target_cname` for the DNS record.
- `proxy-get`: one proxy's status and message.
- `proxy-diagnose`: checks DNS, CAA records, the certificate, and a live event, and says how to fix each failure.
- `proxy-retry`: starts provisioning again after the user fixed the problem.

Proxies belong to the organization, not the project, and only organization admins can create, retry, diagnose, or delete them. The token needs the `organization:write` scope. With the hog CLI, run `hog auth add organization:write` and ask the user to approve it in the browser. If PostHog rejects the call because the user isn't an admin, give the steps to an admin, or use a self-hosted proxy instead.

## Instructions

Follow these steps IN ORDER:

STEP 1: Check what the app already has.
  - Find where the app initializes posthog-js and read its `api_host` and `ui_host`. Check the env files and the hosting configuration that set them too.
  - If `api_host` already points at a domain or a path of the app, a proxy exists. Check that it routes as the guidelines below require, fix it if it doesn't, and stop there.
  - Find the PostHog Cloud region. Use the host that the tool or CLI which started this work gave you, then the `host` in `posthog.json`, then the current `api_host` (`us.i.posthog.com` is US, `eu.i.posthog.com` is EU). If none of them names it, ask the user: "Are you on PostHog US Cloud or EU Cloud?" Do not assume US Cloud. A proxy that forwards to the wrong region loses every event it receives.
  - Self-hosted PostHog has no managed proxy. Go to STEP 3B.
  - Run `proxy-list`. If a proxy with status `valid` already exists for a subdomain of this app's domain, use it: go to STEP 4.

STEP 2: Choose the self-hosted or the managed proxy.
  - Prefer a self-hosted proxy when the app's hosting makes it a small change:
    - Next.js (rewrites in `next.config.*`, or middleware), Nuxt, SvelteKit, or Remix, which have proxy references above.
    - An app deployed on Cloudflare (Workers or Pages), Vercel, or Netlify, whose configuration is in the repo.
    - A reverse proxy configuration the repo already contains: nginx, Caddy, or a Kubernetes ingress.
  - Also use a self-hosted proxy, whatever the platform, when the managed proxy can't serve the app:
    - Self-hosted PostHog.
    - The app processes protected health information under HIPAA, or needs EU-only edge termination.
    - The domain is a Cloudflare Enterprise zone with zone hold enabled.
    - The user isn't an organization admin, can't add DNS records, or the organization has as many proxies as its plan allows (`proxy-list`) and none fits this app.
  - Prefer the managed proxy for everything else, where a self-hosted proxy means adding a server, a function, or hosting the app doesn't have yet. For example, static hosting without rewrites to other origins, or a framework with no proxy reference above.
  - On Vercel, Netlify, CloudFront, or Railway, mention the cost trade-off for a high-traffic site, and offer the managed proxy as the alternative.
  - Tell the user which one you chose and why, in one or two sentences from the trade-offs table. Ask before going ahead only when the choice isn't clear from the rules above.

STEP 3A: Set up the managed proxy.
  - Pick a subdomain of the domain the app is served from, and confirm it with the user before you create anything. The user must control its DNS, and it should be neutral: no `analytics`, `tracking`, `telemetry`, `posthog`, or `ph` in the name, because ad blockers match those words.
  - Run `proxy-create` with `{"domain": "<subdomain>"}`. Keep the `id` and the `target_cname` it returns.
  - You can't create DNS records. Give the user the exact record: type `CNAME`, name the subdomain, target the `target_cname`. If their DNS is on Cloudflare, the record must be DNS only (gray cloud), not proxied.
  - The status goes from `waiting` to `issuing` to `valid`. That usually takes 2 to 5 minutes after the record exists, and up to 30 minutes when DNS is slow. Check it with `proxy-get`. Don't wait for it in a loop.
  - If the status is `erroring` or `timed_out`, or it stays `issuing` for more than 30 minutes, run `proxy-diagnose` and give the user the remediation it returns. After they fix it, run `proxy-retry`.
  - Point the SDK at the proxy only once its status is `valid`. Until then, every request to the subdomain fails, and the app would send nothing. If it isn't `valid` yet, make the proxy URL configurable without switching to it: read `api_host` from an environment variable whose default stays PostHog's ingestion host, and tell the user to set the variable once the proxy is live.
  - Set `api_host` to `https://<subdomain>` and `ui_host` to the PostHog app host: `https://us.posthog.com` or `https://eu.posthog.com`.

STEP 3B: Set up a self-hosted proxy.
  - Find the reference for the platform that serves the app, not the framework it is built with. A Vite app deployed on Cloudflare Workers uses the Cloudflare reference, and a Next.js app on Vercel uses the Next.js rewrites reference. If no reference matches, follow the proxy reference's routing rules on whatever the app runs.
  - Use the path the reference gives, or a neutral one such as `/e` or `/ingest`. Avoid the words ad blockers match: `analytics`, `tracking`, `telemetry`, `posthog`, `ph`.
  - Forward to the region's hosts: `/static/*` and `/array/*` to the assets host, everything else to the ingestion host. The proxy reference lists the headers, methods, and body size a self-hosted proxy must handle. Check the platform's code against it.
  - Do not alter the fundamental architecture of existing files. Add the proxy route next to the app's other routes, rewrites, or worker code.
  - Make the local dev server proxy the same path, or keep local development pointed at PostHog directly. Don't leave a path that only works in production.
  - Set `api_host` to the proxy path or domain and `ui_host` to the PostHog app host: `https://us.posthog.com` or `https://eu.posthog.com`.

STEP 4: Update the app.
  - Read `api_host` and `ui_host` the way the app already reads its PostHog settings, usually environment variables. Never hardcode a key.
  - If the app sends a Content-Security-Policy, allow the proxy in `script-src` and `connect-src`.
  - List any new environment variable in `.env.example`, or the env template the project already uses, with a placeholder value.

STEP 5: Verify the proxy.
  - Check routing without writing data. A `GET` of `<proxy>/array/<project token>/config.js` should return JavaScript, and a `POST` of `{"api_key": "<project token>", "distinct_id": "proxy-check"}` to `<proxy>/flags/?v=2` should return JSON with a `flags` key. Neither creates events.
  - Avoid sending test events to the user's project. If you must, give them an obvious name and tell the user which events you sent.
  - posthog-js's bot filter drops every capture from an automated browser, while flag calls and asset loads still succeed. A Playwright or Puppeteer test that shows no events in PostHog doesn't mean the proxy is broken. Check the proxy's responses instead.
  - For the managed proxy, `proxy-get` returning `valid` and the two checks above passing is enough.

STEP 6: Hand off.
  - List the files you changed and the approach you chose, with the reason.
  - List what the user still has to do, with exact values: the DNS record, environment variables in the hosting platform, and the wait for the managed proxy to become `valid`.
  - Tell the user how to check it after the next deploy: in the browser's Network tab, PostHog requests go to the proxy and return `200`.

## Guidelines

Read `references/COMMANDMENTS.md` before STEP 3A or STEP 3B, and follow every rule in it.
