---
name: instrument-error-tracking
description: >-
  Add PostHog error tracking to capture and monitor exceptions. Use after
  implementing features or reviewing PRs to ensure errors are tracked with stack
  traces and source maps. Also handles initial PostHog SDK setup if not yet
  installed.
metadata:
  author: PostHog
---

# Add PostHog error tracking

Use this skill to add PostHog error tracking that captures and monitors exceptions in your application. Use it after implementing features or reviewing PRs to ensure errors are tracked with full stack traces and source maps. If PostHog is not yet installed, this skill also covers initial SDK setup. Supports any platform or language.

Supported platforms: React, Next.js, Web (JavaScript), Node.js, Python, PHP, Ruby, Ruby on Rails, Go, Elixir, Angular, Svelte, Nuxt, React Native, Flutter, iOS, Android, and Hono.

## Instructions

Before you edit anything, read `references/COMMANDMENTS.md`. It lists the rules every PostHog install follows: how to install the SDK, where to create the client, how to identify users, Content Security Policy and multi-platform apps, plus the rules for this framework.

Follow these steps IN ORDER:

STEP 1: Analyze the codebase and detect the platform.
  -
 Look for dependency files (package.json, pubspec.yaml, Podfile, Package.swift, requirements.txt, go.mod, Gemfile, composer.json, mix.exs, etc.) to determine the language and framework.
  -
 Look for lockfiles (pnpm-lock.yaml, package-lock.json, yarn.lock, bun.lockb, go.sum, pubspec.lock, Podfile.lock, Package.resolved, mix.lock) to determine the package manager.
  - Check for existing PostHog setup (SDK initialization, env vars, etc.). If PostHog is already installed and initialized, skip to STEP 4.

STEP 2: Research instrumentation. (Skip if PostHog is already set up.)
  2.1. Find the reference file below that matches the detected platform — it is the source of truth for SDK initialization, exception autocapture, and framework-specific error tracking patterns. Read it now.
  2.2. If no reference matches, fall back to your general knowledge and web search. Use posthog.com/docs as the primary search source.

STEP 3: Install and initialize the PostHog SDK. (Skip if PostHog is already set up.)
  - Add the PostHog SDK package for the detected platform. Do not manually edit package.json — use the package manager's install command.
  - If the project keeps more than one lockfile for the same manifest, such as a second Gemfile lock for another bundle, update each one.
  - Follow the framework reference for where and how to initialize.
  - For posthog-js, set `defaults` to the preset the framework docs reference shows. The example projects can show an older preset.
  - For posthog-js, if the framework reference documents a reverse proxy for this framework, set it up as part of this change. Otherwise, suggest one in your final message: a reverse proxy keeps ad blockers from dropping events (https://posthog.com/docs/advanced/proxy.md).

STEP 4: Enable exception autocapture.
  - Follow the platform reference to enable exception autocapture. This automatically captures unhandled exceptions without additional code.

STEP 5: Add manual error captures.
  - Identify error boundaries, catch blocks, and critical user flows where errors should be explicitly captured.
  - Add `posthog.captureException()` or the platform-equivalent at these locations.
  - Do not alter the fundamental architecture of existing error handling. Make additions minimal and targeted.
  - You must read a file immediately before attempting to write it.

STEP 6: Upload source maps (frontend/mobile only).
  - Configure source map uploads so stack traces resolve to original source code, not minified bundles.
  - Follow the platform-specific reference for upload configuration (build plugins, CI scripts, etc.).

STEP 7: Set up environment variables.
  - Check if the project already has PostHog environment variables configured (e.g. in `.env`, `.env.local`, or framework-specific env files). If valid values already exist, skip this step.
  - If the PostHog project token is missing, use the project token that the tool or CLI which started this setup already gave you (for example in its output or instructions).
  - If it gave you none, use the PostHog MCP server's `projects-get` tool to retrieve the project's `api_token`. If multiple projects are returned, ask the user which project to use. If the MCP server is not connected or not authenticated, ask the user for their PostHog project token instead.
  - For the PostHog host URL: use the host that the tool or CLI which started this setup already gave you. If it gave you none, check the `projects-get` MCP response for a `region` field — `US` maps to `https://us.i.posthog.com`, `EU` maps to `https://eu.i.posthog.com`. If you still have no host from the calling tool, the MCP response, or existing project configuration, ask the user: "Are you on PostHog US Cloud or EU Cloud?" Do not assume US Cloud.
  - Write these values to the appropriate env file using the framework's naming convention.
  - Reference these environment variables in code instead of hardcoding them.
  - List the key names in `.env.example`, or the env template the project already uses, with placeholder values, so the next developer knows what to set. Create `.env.example` if the project has none. Never put real values in it.
  - Read the keys as optional: a missing key must never break the build or boot. Follow the missing-configuration rule in `references/COMMANDMENTS.md`.

STEP 8: Verify and clean up.
  - Check the project for errors. Look for type checking or build scripts in package.json.
  - Ensure any components created were actually used.
  - Run any linter or prettier-like scripts found in the package.json, but ONLY on the files you have edited or created during this session. Never run formatting or linting across the entire project's codebase.

## Reference files

- `references/react.md` - React error tracking installation
- `references/web.md` - Web error tracking installation
- `references/nextjs.md` - Next.js error tracking installation
- `references/node.md` - Node.js error tracking installation
- `references/python.md` - Python error tracking installation
- `references/django.md` - Django
- `references/flask.md` - Flask
- `references/php.md` - Php error tracking installation
- `references/laravel.md` - Laravel
- `references/ruby.md` - Ruby error tracking installation
- `references/ruby-on-rails.md` - Ruby on rails error tracking installation
- `references/ruby-on-rails.md` - Ruby on rails
- `references/go.md` - Go error tracking installation
- `references/dotnet.md` - .net error tracking installation
- `references/dotnet.md` - .net
- `references/elixir.md` - Elixir error tracking installation
- `references/angular.md` - Angular error tracking installation
- `references/svelte.md` - Sveltekit error tracking installation
- `references/nuxt-3-7.md` - Nuxt error tracking installation (v3.7 and above)
- `references/nuxt-3-6.md` - Nuxt error tracking installation (v3.6 and below)
- `references/react-native.md` - React native error tracking installation
- `references/flutter.md` - Flutter error tracking installation
- `references/ios.md` - Ios error tracking installation
- `references/android.md` - Android error tracking installation
- `references/hono.md` - Hono error tracking installation
- `references/fingerprints.md` - Fingerprints
- `references/alerts.md` - Send error tracking alerts
- `references/monitoring.md` - Monitor and search issues
- `references/assigning-issues.md` - Assign issues to teammates
- `references/upload-source-maps.md` - Upload source maps
- `references/COMMANDMENTS.md` - Framework-specific rules the integration must follow

Each platform reference contains SDK-specific installation and manual capture patterns. Find the one matching the user's stack.

## Key principles

- **Environment variables**: Always use environment variables for PostHog keys. Never hardcode them.
- **Minimal changes**: Add error tracking alongside existing error handling. Don't replace or restructure existing code.
- **Autocapture first**: Enable exception autocapture before adding manual captures.
- **Source maps**: Upload source maps so stack traces resolve to original source code, not minified bundles.
- **Manual capture for boundaries**: Use `captureException()` at error boundaries and catch blocks for errors that don't propagate to the global handler.
