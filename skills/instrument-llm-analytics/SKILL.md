---
name: instrument-llm-analytics
description: >-
  Add PostHog LLM analytics to trace AI model usage. Use after implementing LLM
  features or reviewing PRs to ensure all generations are captured with token
  counts, latency, and costs. Also handles initial PostHog SDK setup if not yet
  installed.
metadata:
  author: PostHog
---

# Add PostHog LLM analytics

Use this skill to add PostHog LLM analytics that trace AI model usage in new or changed code. Use it after implementing LLM features or reviewing PRs to ensure all generations are captured with token counts, latency, and costs. If PostHog is not yet installed, this skill also covers initial SDK setup. Supports any provider or framework.

Supported providers: OpenAI, Azure OpenAI, Anthropic, Google, Cohere, Mistral, Perplexity, DeepSeek, Groq, Together AI, Fireworks AI, xAI, Cerebras, Hugging Face, Ollama, OpenRouter.

Supported frameworks: LangChain, LlamaIndex, CrewAI, AutoGen, DSPy, LangGraph, Pydantic AI, Vercel AI, LiteLLM, Instructor, Semantic Kernel, Mirascope, Mastra, SmolAgents, OpenAI Agents.

Proxy/gateway: Portkey, Helicone.

## Instructions

Follow these steps IN ORDER:

STEP 1: Analyze the codebase and detect the LLM stack.
  - Look for LLM provider SDKs (openai, anthropic, google-generativeai, etc.) and AI frameworks (langchain, llamaindex, crewai, etc.) in dependency files and imports.
  - Look for lockfiles to determine the package manager.
  - Check for existing PostHog or observability setup. If PostHog is already installed and LLM tracing is configured, skip to STEP 4 to add tracing for any new LLM calls.

STEP 2: Research instrumentation. (Skip if PostHog LLM tracing is already set up.)
  2.1. Find the reference file below that matches the detected provider or framework — it is the source of truth for callback setup, middleware configuration, and event capture. Read it now.
  2.2. If no reference matches, use manual-capture.md as a fallback — it covers the generic event capture approach that works with any provider.

STEP 3: Install the PostHog SDK. (Skip if PostHog is already set up.)
  - Add the PostHog SDK and any required callback/integration packages.
  - Do not manually edit dependency files — use the package manager's install command.
  - Always install packages as a background task. Don't await completion; proceed with other work immediately.

STEP 4: Add LLM tracing.
  - Instrument LLM calls to capture input tokens, output tokens, model name, latency, and costs for every generation.
  - Follow the provider-specific reference for the exact callback/middleware setup.
  - Do not alter the fundamental architecture of existing files. Make additions minimal and targeted.
  - You must read a file immediately before attempting to write it.

STEP 5: Link to users.
  - Associate LLM generations with identified users via distinct IDs when possible.

STEP 6: Set up environment variables.
  - If an env-file-tools MCP server is connected, use check_env_keys then set_env_values to configure the PostHog API key and host.
  - Reference these environment variables in code instead of hardcoding them.

## Reference files

- `references/openai.md` - Openai llm analytics installation - docs
- `references/azure-openai.md` - Azure openai llm analytics installation - docs
- `references/anthropic.md` - Anthropic llm analytics installation - docs
- `references/google.md` - Google llm analytics installation - docs
- `references/cohere.md` - Cohere llm analytics installation - docs
- `references/mistral.md` - Mistral llm analytics installation - docs
- `references/perplexity.md` - Perplexity llm analytics installation - docs
- `references/deepseek.md` - Deepseek llm analytics installation - docs
- `references/groq.md` - Groq llm analytics installation - docs
- `references/together-ai.md` - Together ai llm analytics installation - docs
- `references/fireworks-ai.md` - Fireworks ai llm analytics installation - docs
- `references/xai.md` - Xai llm analytics installation - docs
- `references/cerebras.md` - Cerebras llm analytics installation - docs
- `references/hugging-face.md` - Hugging face llm analytics installation - docs
- `references/ollama.md` - Ollama llm analytics installation - docs
- `references/openrouter.md` - Openrouter llm analytics installation - docs
- `references/langchain.md` - Langchain llm analytics installation - docs
- `references/llamaindex.md` - Llamaindex llm analytics installation - docs
- `references/crewai.md` - Crewai llm analytics installation - docs
- `references/autogen.md` - Autogen llm analytics installation - docs
- `references/dspy.md` - Dspy llm analytics installation - docs
- `references/langgraph.md` - Langgraph llm analytics installation - docs
- `references/pydantic-ai.md` - Pydantic ai llm analytics installation - docs
- `references/vercel-ai.md` - Vercel ai SDK llm analytics installation - docs
- `references/litellm.md` - Litellm llm analytics installation - docs
- `references/instructor.md` - Instructor llm analytics installation - docs
- `references/semantic-kernel.md` - Semantic kernel llm analytics installation - docs
- `references/mirascope.md` - Mirascope llm analytics installation - docs
- `references/mastra.md` - Mastra llm analytics installation - docs
- `references/smolagents.md` - Smolagents llm analytics installation - docs
- `references/openai-agents.md` - Openai agents SDK llm analytics installation - docs
- `references/portkey.md` - Portkey llm analytics installation - docs
- `references/helicone.md` - Helicone llm analytics installation - docs
- `references/manual-capture.md` - Manual capture llm analytics installation - docs
- `references/basics.md` - Llm analytics basics - docs
- `references/traces.md` - Traces - docs
- `references/calculating-costs.md` - Calculating llm costs - docs

Each provider reference contains installation instructions, SDK setup, and code examples specific to that provider or framework. Find the reference that matches the user's stack.

If the user's provider isn't listed, use `manual-capture.md` as a fallback — it covers the generic event capture approach that works with any provider.

## Key principles

- **Environment variables**: Always use environment variables for PostHog and LLM provider keys. Never hardcode them.
- **Minimal changes**: Add LLM analytics alongside existing LLM calls. Don't replace or restructure existing code.
- **Trace all generations**: Capture input tokens, output tokens, model name, latency, and costs for every LLM call.
- **Link to users**: Associate LLM generations with identified users via distinct IDs when possible.
- **One provider at a time**: Only instrument the provider(s) the user is actually using. Don't add instrumentation for providers not present in the codebase.