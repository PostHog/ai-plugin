---
name: instrument-feature-flags
description: >-
  Add PostHog feature flags to gate new functionality. Use after implementing
  features or reviewing PRs to ensure safe rollouts with feature flag controls.
  Also handles initial PostHog SDK setup if not yet installed.
metadata:
  author: PostHog
---

# Add PostHog feature flags

Use this skill to add PostHog feature flags that gate new or changed functionality. Use it after implementing features or reviewing PRs to ensure safe rollouts with feature flag controls. If PostHog is not yet installed, this skill also covers initial SDK setup. Supports any platform or language.

Supported platforms: React, Next.js, React Native, Web (JavaScript), Node.js, Python, PHP, Ruby, Go, Java, Rust, .NET, Elixir, Android, iOS, Flutter, and the REST API.

## Instructions

Follow these steps IN ORDER:

STEP 1: Analyze the codebase and detect the platform.
  - Look for dependency files (package.json, requirements.txt, go.mod, Gemfile, composer.json, etc.) to determine the language and framework.
  - Look for lockfiles (pnpm-lock.yaml, package-lock.json, yarn.lock, bun.lockb) to determine the package manager.
  - Check for existing PostHog setup (SDK initialization, env vars, etc.). If PostHog is already installed and initialized, skip to STEP 3.

STEP 2: Research instrumentation. (Skip if PostHog is already set up.)
  2.1. Find the reference file below that matches the detected platform — it is the source of truth for SDK initialization, flag evaluation methods, and framework-specific patterns. Read it now.
  2.2. If no reference matches, fall back to your general knowledge and web search. Use posthog.com/docs as the primary search source.

STEP 3: Create or find the feature flag.
  - Check if a PostHog MCP server is connected. If available, use its tools to search for an existing feature flag the user wants to instrument, or create a new one.
  - If no MCP server is available, instruct the user to create the flag in the PostHog dashboard.

STEP 4: Plan release conditions.
  - Determine the rollout strategy (percentage rollout, user targeting, group targeting, etc.).
  - Plan how the feature flag will gate the new functionality in code.

STEP 5: Instrument the feature.
  - Add the feature flag code following the platform-specific reference patterns.
  - Use server-side evaluation when possible to avoid UI flicker.
  - Do not alter the fundamental architecture of existing files. Make additions minimal and targeted.
  - You must read a file immediately before attempting to write it.

STEP 6: Set up environment variables.
  - If an env-file-tools MCP server is connected, use check_env_keys to see which keys already exist, then use set_env_values to create or update the PostHog API key and host.
  - Reference these environment variables in code instead of hardcoding them.

## Reference files

- `references/react.md` - React feature flags installation - docs
- `references/react-native.md` - React native feature flags installation - docs
- `references/web.md` - Web feature flags installation - docs
- `references/nodejs.md` - Node.js feature flags installation - docs
- `references/python.md` - Python feature flags installation - docs
- `references/php.md` - Php feature flags installation - docs
- `references/ruby.md` - Ruby feature flags installation - docs
- `references/go.md` - Go feature flags installation - docs
- `references/java.md` - Java feature flags installation - docs
- `references/rust.md` - Rust feature flags installation - docs
- `references/dotnet.md` - .net feature flags installation - docs
- `references/elixir.md` - Elixir feature flags installation - docs
- `references/android.md` - Android feature flags installation - docs
- `references/ios.md` - Ios feature flags installation - docs
- `references/flutter.md` - Flutter feature flags installation - docs
- `references/api.md` - API feature flags installation - docs
- `references/next-js.md` - Next.js - docs
- `references/adding-feature-flag-code.md` - Adding feature flag code - docs
- `references/best-practices.md` - Feature flag best practices - docs

Each platform reference contains SDK-specific installation, flag evaluation, and code examples. Find the one matching the user's stack. If unlisted, use the API reference as a fallback.

## Key principles

- **Environment variables**: Always use environment variables for PostHog keys. Never hardcode them.
- **Minimal changes**: Add feature flag code alongside existing logic. Don't replace or restructure existing code.
- **Boolean flags first**: Default to boolean flag checks unless the user specifically asks for multivariate flags.
- **Server-side when possible**: Prefer server-side flag evaluation to avoid UI flicker.