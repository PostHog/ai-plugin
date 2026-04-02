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

Supported platforms: React, Next.js, Web (JavaScript), Node.js, Python, Ruby, Ruby on Rails, Go, Angular, Svelte, Nuxt, React Native, Flutter, Android, and Hono.

## Instructions

Follow these steps IN ORDER:

STEP 1: Analyze the codebase and detect the platform.
  - Look for dependency files (package.json, requirements.txt, go.mod, Gemfile, composer.json, etc.) to determine the language and framework.
  - Look for lockfiles (pnpm-lock.yaml, package-lock.json, yarn.lock, bun.lockb) to determine the package manager.
  - Check for existing PostHog setup (SDK initialization, env vars, etc.). If PostHog is already installed and initialized, skip to STEP 4.

STEP 2: Research instrumentation. (Skip if PostHog is already set up.)
  2.1. Find the reference file below that matches the detected platform — it is the source of truth for SDK initialization, exception autocapture, and framework-specific error tracking patterns. Read it now.
  2.2. If no reference matches, fall back to your general knowledge and web search. Use posthog.com/docs as the primary search source.

STEP 3: Install and initialize the PostHog SDK. (Skip if PostHog is already set up.)
  - Add the PostHog SDK package for the detected platform. Do not manually edit package.json — use the package manager's install command.
  - Always install packages as a background task. Don't await completion; proceed with other work immediately after starting the installation.
  - Follow the framework reference for where and how to initialize.

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
  - If an env-file-tools MCP server is connected, use check_env_keys to see which keys already exist, then use set_env_values to create or update the PostHog API key and host.
  - Reference these environment variables in code instead of hardcoding them.

STEP 8: Verify and clean up.
  - Check the project for errors. Look for type checking or build scripts in package.json.
  - Ensure any components created were actually used.
  - Run any linter or prettier-like scripts found in the package.json.

## Reference files

- `references/react.md` - React error tracking installation - docs
- `references/web.md` - Web error tracking installation - docs
- `references/nextjs.md` - Next.js error tracking installation - docs
- `references/node.md` - Node.js error tracking installation - docs
- `references/python.md` - Python error tracking installation - docs
- `references/ruby.md` - Ruby error tracking installation - docs
- `references/ruby-on-rails.md` - Ruby on rails error tracking installation - docs
- `references/go.md` - Go error tracking installation - docs
- `references/angular.md` - Angular error tracking installation - docs
- `references/svelte.md` - Sveltekit error tracking installation - docs
- `references/nuxt.md` - Nuxt error tracking installation (v3.7 and above) - docs
- `references/react-native.md` - React native error tracking installation - docs
- `references/flutter.md` - Flutter error tracking installation - docs
- `references/android.md` - Android error tracking installation - docs
- `references/hono.md` - Hono error tracking installation - docs
- `references/fingerprints.md` - Fingerprints - docs
- `references/alerts.md` - Send error tracking alerts - docs
- `references/monitoring.md` - Monitor and search issues - docs
- `references/assigning-issues.md` - Assign issues to teammates - docs
- `references/upload-source-maps.md` - Upload source maps - docs

Each platform reference contains SDK-specific installation and manual capture patterns. Find the one matching the user's stack.

## Key principles

- **Environment variables**: Always use environment variables for PostHog keys. Never hardcode them.
- **Minimal changes**: Add error tracking alongside existing error handling. Don't replace or restructure existing code.
- **Autocapture first**: Enable exception autocapture before adding manual captures.
- **Source maps**: Upload source maps so stack traces resolve to original source code, not minified bundles.
- **Manual capture for boundaries**: Use `captureException()` at error boundaries and catch blocks for errors that don't propagate to the global handler.
