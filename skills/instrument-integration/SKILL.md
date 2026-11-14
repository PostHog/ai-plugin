---
name: instrument-integration
description: >-
  Add PostHog SDK integration to your application. Use when setting up PostHog
  for the first time or reviewing PRs that need PostHog initialization. Covers
  SDK installation, provider setup, and basic configuration for any framework.
metadata:
  author: PostHog
---

# Add PostHog SDK integration

Use this skill to add the PostHog SDK to an application. Use it when setting up PostHog for the first time, or reviewing PRs that need PostHog initialization. Covers SDK installation, provider setup, and basic configuration. Supports any framework or language.

Supported frameworks and languages: Next.js, React, React Router, Remix, Vue, Nuxt, TanStack Start, SvelteKit, Astro, Angular, Gatsby, Docusaurus, Django, Flask, FastAPI, Laravel, PHP, WordPress, Ruby on Rails, Elixir (Phoenix), Go, Java (Spring Boot), Rust, .NET, Android, iOS, Swift, Flutter, Kotlin Multiplatform, React Native, Expo, Capacitor, Node.js, NestJS, Fastify, Hono, Cloudflare Workers, Convex, Unity, Godot, Roblox, and vanilla JavaScript.

## Instructions

Before you edit anything, read `references/COMMANDMENTS.md`. It lists the rules every PostHog install follows: how to install the SDK, where to create the client, how to identify users, Content Security Policy and multi-platform apps, plus the rules for this framework.

Follow these steps IN ORDER:

STEP 1: Analyze the codebase and detect the platform.
  -
 Look for dependency files (package.json, pubspec.yaml, Podfile, Package.swift, requirements.txt, Gemfile, composer.json, go.mod, mix.exs, etc.) to determine the framework and language.
  -
 Look for lockfiles (pnpm-lock.yaml, package-lock.json, yarn.lock, bun.lockb, go.sum, pubspec.lock, Podfile.lock, Package.resolved, mix.lock) to determine the package manager.
  - Check for existing PostHog setup. If PostHog is already installed and initialized, do not modify its code. Inform the user and skip to verification.

STEP 2: Research integration.
  2.1. Find the reference file below that matches the detected framework — it is the source of truth for SDK initialization, provider setup, and configuration patterns. Read it now.
  2.2. If no reference matches, fall back to your general knowledge and web search. Use posthog.com/docs as the primary search source.

STEP 3: Install the PostHog SDK.
  - Add the PostHog SDK package for the detected platform. Do not manually edit package.json — use the package manager's install command.
  - If the project keeps more than one lockfile for the same manifest, such as a second Gemfile lock for another bundle, update each one.

STEP 4: Initialize PostHog.
  - Follow the framework reference for where and how to initialize. This varies significantly by framework (e.g., instrumentation-client.ts for Next.js 15.3+, AppConfig.ready() for Django, create_app() for Flask).
  - Set up the PostHog provider/wrapper component if the framework requires one.
  - For posthog-js, set `defaults` to the preset the framework docs reference shows. The example projects can show an older preset.
  - For posthog-js, if the framework reference documents a reverse proxy for this framework, set it up as part of this change. Otherwise, suggest one in your final message: a reverse proxy keeps ad blockers from dropping events, and the `instrument-reverse-proxy` skill sets one up (https://posthog.com/docs/advanced/proxy.md).

STEP 5: Identify users.
  - Add PostHog `identify()` calls on the client side during login and signup events.
  - If both frontend and backend exist, pass the client-side session and distinct ID using `X-POSTHOG-DISTINCT-ID` and `X-POSTHOG-SESSION-ID` headers to the server-side code.

STEP 6: Set up environment variables.
  - Check if the project already has PostHog environment variables configured (e.g. in `.env`, `.env.local`, or framework-specific env files). If valid values already exist, skip this step.
  - If the PostHog project token is missing, use the project token that the tool or CLI which started this setup already gave you (for example in its output or instructions).
  - If it gave you none, use the PostHog MCP server's `projects-get` tool to retrieve the project's `api_token`. If multiple projects are returned, ask the user which project to use. If the MCP server is not connected or not authenticated, ask the user for their PostHog project token instead.
  - For the PostHog host URL: use the host that the tool or CLI which started this setup already gave you. If it gave you none, check the `projects-get` MCP response for a `region` field — `US` maps to `https://us.i.posthog.com`, `EU` maps to `https://eu.i.posthog.com`. If you still have no host from the calling tool, the MCP response, or existing project configuration, ask the user: "Are you on PostHog US Cloud or EU Cloud?" Do not assume US Cloud.
  - Write these values to the appropriate env file (e.g. `.env.local` for Next.js, `.env` for others) using the framework's naming convention.
  - Reference these environment variables in code instead of hardcoding them.
  - List the key names in `.env.example`, or the env template the project already uses, with placeholder values, so the next developer knows what to set. Create `.env.example` if the project has none. Never put real values in it.
  - Read the keys as optional: a missing key must never break the build or boot. Follow the missing-configuration rule in `references/COMMANDMENTS.md`.

STEP 7: Verify and clean up.
  - Check the project for errors. Look for type checking or build scripts in package.json.
  - Ensure any components created were actually used.
  - Run any linter or prettier-like scripts found in the package.json, but ONLY on the files you have edited or created during this session. Never run formatting or linting across the entire project's codebase.

## Reference files

- `references/EXAMPLE-next-app-router.md` - next-app-router example project code
- `references/EXAMPLE-next-pages-router.md` - next-pages-router example project code
- `references/EXAMPLE-react-react-router-6.md` - react-react-router-6 example project code
- `references/EXAMPLE-react-react-router-7-framework.md` - react-react-router-7-framework example project code
- `references/EXAMPLE-react-react-router-7-data.md` - react-react-router-7-data example project code
- `references/EXAMPLE-react-react-router-7-declarative.md` - react-react-router-7-declarative example project code
- `references/EXAMPLE-react-vite.md` - react-vite example project code
- `references/EXAMPLE-nuxt-3-6.md` - nuxt-3-6 example project code
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
- `references/EXAMPLE-gatsby.md` - gatsby example project code
- `references/EXAMPLE-docusaurus.md` - docusaurus example project code
- `references/EXAMPLE-remix.md` - remix example project code
- `references/EXAMPLE-javascript-node.md` - javascript-node example project code
- `references/EXAMPLE-nestjs.md` - nestjs example project code
- `references/EXAMPLE-fastify.md` - fastify example project code
- `references/EXAMPLE-hono.md` - hono example project code
- `references/EXAMPLE-cloudflare-workers.md` - cloudflare-workers example project code
- `references/EXAMPLE-convex.md` - convex example project code
- `references/EXAMPLE-javascript-web.md` - javascript-web example project code
- `references/EXAMPLE-django.md` - django example project code
- `references/EXAMPLE-flask.md` - flask example project code
- `references/EXAMPLE-fastapi.md` - fastapi example project code
- `references/EXAMPLE-python.md` - python example project code
- `references/EXAMPLE-laravel.md` - laravel example project code
- `references/EXAMPLE-php.md` - php example project code
- `references/EXAMPLE-wordpress.md` - wordpress example project code
- `references/EXAMPLE-ruby-on-rails.md` - ruby-on-rails example project code
- `references/EXAMPLE-ruby.md` - ruby example project code
- `references/EXAMPLE-elixir.md` - elixir example project code
- `references/EXAMPLE-go.md` - go example project code
- `references/EXAMPLE-java-spring-boot.md` - java-spring-boot example project code
- `references/EXAMPLE-rust.md` - rust example project code
- `references/EXAMPLE-dotnet.md` - dotnet example project code
- `references/EXAMPLE-android.md` - android example project code
- `references/EXAMPLE-swift.md` - swift example project code
- `references/EXAMPLE-swift-xcodegen.md` - swift-xcodegen example project code
- `references/EXAMPLE-flutter.md` - flutter example project code
- `references/EXAMPLE-react-native.md` - react-native example project code
- `references/EXAMPLE-expo.md` - expo example project code
- `references/next-js.md` - Next.js
- `references/react.md` - React
- `references/react-router-v6.md` - React router v6
- `references/react-router-v7-framework-mode.md` - React router v7 framework mode (remix v3)
- `references/react-router-v7-data-mode.md` - React router v7 data mode
- `references/react-router-v7-declarative-mode.md` - React router v7 declarative mode
- `references/nuxt-js-3-6.md` - Nuxt.js (v3.0 to v3.6)
- `references/nuxt-js.md` - Nuxt.js
- `references/nuxt-js-2.md` - Nuxt.js (v2.16 and below)
- `references/gatsby.md` - Gatsby
- `references/docusaurus.md` - Docusaurus
- `references/vue-js.md` - Vue.js
- `references/tanstack-start.md` - Tanstack start
- `references/svelte.md` - Svelte
- `references/astro.md` - Astro
- `references/angular.md` - Angular
- `references/js.md` - JavaScript web
- `references/posthog-js.md` - PostHog JavaScript web SDK
- `references/node.md` - Node.js
- `references/nestjs.md` - Nestjs
- `references/fastify.md` - Fastify
- `references/hono.md` - Hono
- `references/remix.md` - Remix
- `references/cloudflare-workers.md` - Cloudflare workers
- `references/convex.md` - Convex
- `references/posthog-node.md` - PostHog Node.js SDK
- `references/django.md` - Django
- `references/flask.md` - Flask
- `references/python.md` - Python
- `references/posthog-python.md` - PostHog python SDK
- `references/dotnet.md` - .net
- `references/elixir.md` - Elixir
- `references/phoenix.md` - Phoenix
- `references/go.md` - Go
- `references/java.md` - Java
- `references/rust.md` - Rust
- `references/laravel.md` - Laravel
- `references/php.md` - Php
- `references/wordpress.md` - How to set up wordpress analytics with PostHog
- `references/ruby-on-rails.md` - Ruby on rails
- `references/ruby.md` - Ruby
- `references/android.md` - Android
- `references/ios.md` - Ios
- `references/usage.md` - Ios SDK usage
- `references/configuration.md` - Ios SDK configuration
- `references/flutter.md` - Flutter
- `references/kmp.md` - Kotlin multiplatform
- `references/react-native.md` - React native
- `references/capacitor.md` - Capacitor
- `references/unity.md` - Unity
- `references/godot.md` - Godot
- `references/roblox.md` - Roblox
- `references/identify-users.md` - Identify users
- `references/COMMANDMENTS.md` - Framework-specific rules the integration must follow

Each framework reference contains SDK-specific installation, initialization, and usage patterns. Find the one matching the user's stack.

## Key principles

- **Environment variables**: Always use environment variables for PostHog keys. Never hardcode them.
- **Minimal changes**: Add PostHog code alongside existing integrations. Don't replace or restructure existing code.
- **Match the example**: Follow the example project's patterns for installing, initializing and identifying as closely as possible. The examples also show features beyond the install, such as exception capture and custom events. Adding them is fine when they fit the app. List what you added beyond the install in your final message, so the user knows what was set up.
- **Analytics contract**: Treat event names, property names, and feature flag keys as part of an analytics contract. Reuse existing names and patterns found in the project. When introducing new ones, make them clear, descriptive, and consistent with existing conventions.
