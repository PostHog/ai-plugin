---
name: instrument-product-analytics
description: >-
  Add PostHog product analytics events to track user behavior. Use after
  implementing new features or reviewing PRs to ensure meaningful user actions
  are captured. Also handles initial PostHog SDK setup if not yet installed.
metadata:
  author: PostHog
---

# Add PostHog product analytics events

Use this skill to add product analytics events (capture calls) that track meaningful user actions in new or changed code. Use it after implementing features or reviewing PRs to ensure key user behaviors are captured. If PostHog is not yet installed, this skill also covers initial SDK setup. Supports any framework or language.

Supported frameworks: Next.js, React Router, Nuxt, Vue, TanStack Start, SvelteKit, Astro, Angular, Django, Flask, FastAPI, Laravel, Ruby on Rails, Android, iOS, React Native, Expo, and more.

## Instructions

Follow these steps IN ORDER:

STEP 1: Analyze the codebase and detect the platform.
  - Look for dependency files (package.json, requirements.txt, Gemfile, composer.json, go.mod, etc.) to determine the framework and language.
  - Look for lockfiles (pnpm-lock.yaml, package-lock.json, yarn.lock, bun.lockb) to determine the package manager.
  - Check for existing PostHog setup. If PostHog is already installed and initialized, skip to STEP 5.

STEP 2: Research integration. (Skip if PostHog is already set up.)
  2.1. Find the reference file below that matches the detected framework — it is the source of truth for SDK initialization, provider setup, and event capture patterns. Read it now.
  2.2. If no reference matches, fall back to your general knowledge and web search. Use posthog.com/docs as the primary search source.

STEP 3: Install the PostHog SDK. (Skip if PostHog is already set up.)
  - Add the PostHog SDK package for the detected platform. Do not manually edit package.json — use the package manager's install command.
  - Always install packages as a background task. Don't await completion; proceed with other work immediately after starting the installation.

STEP 4: Initialize PostHog. (Skip if PostHog is already set up.)
  - Follow the framework reference for where and how to initialize. This varies significantly by framework (e.g., instrumentation-client.ts for Next.js 15.3+, AppConfig.ready() for Django, create_app() for Flask).

STEP 5: Plan event tracking.
  - From the project's file list, select between 10 and 15 files that might have interesting business value for event tracking, especially conversion and churn events.
  - Also look for files related to login that could be used for identifying users, along with error handling.
  - Find any existing `posthog.capture()` code. Make note of event name formatting. Don't duplicate existing events; supplement them.
  - Track actions only, not pageviews (those can be captured automatically). Exceptions can be made for "viewed"-type events at the top of a conversion funnel.
  - **Server-side events are REQUIRED** if the project includes any instrumentable server-side code (API routes, server actions, webhook handlers, payment/checkout completion, authentication endpoints).

STEP 6: Implement event capture.
  - For each planned event, add `posthog.capture()` calls with useful properties.
  - If a file already has existing integration code for other tools or services, don't overwrite or remove that code. Place PostHog code below it.
  - Do not alter the fundamental architecture of existing files. Make additions minimal and targeted.
  - You must read a file immediately before attempting to write it.

STEP 7: Identify users.
  - Add PostHog `identify()` calls on the client side during login and signup events. Use the contents of login and signup forms to identify users on submit.
  - If both frontend and backend exist, pass the client-side session and distinct ID using `X-POSTHOG-DISTINCT-ID` and `X-POSTHOG-SESSION-ID` headers to the server-side code. On the server side, make sure events have a matching distinct ID.

STEP 8: Add error tracking.
  - Add PostHog exception capture error tracking to relevant files, particularly around critical user flows and API boundaries.

STEP 9: Set up environment variables.
  - If an env-file-tools MCP server is connected, use check_env_keys to see which keys already exist, then use set_env_values to create or update the PostHog API key and host.
  - Reference these environment variables in code instead of hardcoding them.

STEP 10: Verify and clean up.
  - Check the project for errors. Look for type checking or build scripts in package.json.
  - Ensure any components created were actually used.
  - Run any linter or prettier-like scripts found in the package.json.

## Reference files

- `references/EXAMPLE-next-app-router.md` - next-app-router example project code
- `references/EXAMPLE-next-pages-router.md` - next-pages-router example project code
- `references/EXAMPLE-react-react-router-6.md` - react-react-router-6 example project code
- `references/EXAMPLE-react-react-router-7-framework.md` - react-react-router-7-framework example project code
- `references/EXAMPLE-react-react-router-7-data.md` - react-react-router-7-data example project code
- `references/EXAMPLE-react-react-router-7-declarative.md` - react-react-router-7-declarative example project code
- `references/EXAMPLE-nuxt-3.6.md` - nuxt-3.6 example project code
- `references/EXAMPLE-nuxt-4.md` - nuxt-4 example project code
- `references/EXAMPLE-vue-3.md` - vue-3 example project code
- `references/EXAMPLE-react-tanstack-router-file-based.md` - react-tanstack-router-file-based example project code
- `references/EXAMPLE-react-tanstack-router-code-based.md` - react-tanstack-router-code-based example project code
- `references/EXAMPLE-tanstack-start.md` - tanstack-start example project code
- `references/EXAMPLE-sveltekit.md` - sveltekit example project code
- `references/EXAMPLE-astro-static.md` - astro-static example project code
- `references/EXAMPLE-astro-view-transitions.md` - astro-view-transitions example project code
- `references/EXAMPLE-astro-ssr.md` - astro-ssr example project code
- `references/EXAMPLE-astro-hybrid.md` - astro-hybrid example project code
- `references/EXAMPLE-angular.md` - angular example project code
- `references/EXAMPLE-django.md` - django example project code
- `references/EXAMPLE-flask.md` - flask example project code
- `references/EXAMPLE-fastapi.md` - fastapi example project code
- `references/EXAMPLE-python.md` - python example project code
- `references/EXAMPLE-laravel.md` - laravel example project code
- `references/EXAMPLE-ruby-on-rails.md` - ruby-on-rails example project code
- `references/EXAMPLE-ruby.md` - ruby example project code
- `references/EXAMPLE-android.md` - android example project code
- `references/EXAMPLE-swift.md` - swift example project code
- `references/EXAMPLE-react-native.md` - react-native example project code
- `references/EXAMPLE-expo.md` - expo example project code
- `references/next-js.md` - Next.js - docs
- `references/react-router-v6.md` - React router v6 - docs
- `references/react-router-v7-framework-mode.md` - React router v7 framework mode (remix v3) - docs
- `references/react-router-v7-data-mode.md` - React router v7 data mode - docs
- `references/react-router-v7-declarative-mode.md` - React router v7 declarative mode - docs
- `references/nuxt-js-3-6.md` - Nuxt.js (v3.0 to v3.6) - docs
- `references/nuxt-js.md` - Nuxt.js - docs
- `references/vue-js.md` - Vue.js - docs
- `references/tanstack-start.md` - Tanstack start - docs
- `references/svelte.md` - Svelte - docs
- `references/astro.md` - Astro - docs
- `references/angular.md` - Angular - docs
- `references/django.md` - Django - docs
- `references/flask.md` - Flask - docs
- `references/python.md` - Python - docs
- `references/posthog-python.md` - PostHog python SDK
- `references/laravel.md` - Laravel - docs
- `references/ruby-on-rails.md` - Ruby on rails - docs
- `references/ruby.md` - Ruby - docs
- `references/android.md` - Android - docs
- `references/ios.md` - Ios - docs
- `references/react-native.md` - React native - docs
- `references/identify-users.md` - Identify users - docs

Each framework reference contains SDK-specific installation, initialization, and usage patterns. Find the one matching the user's stack.

## Key principles

- **Environment variables**: Always use environment variables for PostHog keys. Never hardcode them.
- **Minimal changes**: Add PostHog code alongside existing integrations. Don't replace or restructure existing code.
- **Match the docs**: Follow the framework reference's initialization and capture patterns exactly.