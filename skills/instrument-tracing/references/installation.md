> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Install tracing

Canonical URL: https://posthog.com/docs/distributed-tracing/installation

PostHog Tracing works with any OpenTelemetry-compatible client – point its OTLP trace exporter at PostHog and you're done, with no PostHog-specific packages.

On Node.js and Python, the PostHog SDK can also create and export spans on its own, with no OpenTelemetry dependency. See the [Node.js](https://posthog.com/docs/distributed-tracing/installation/nodejs.md) and [Python](https://posthog.com/docs/distributed-tracing/installation/python.md) guides for both routes.

## Platforms

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/nodejs.svg)Node.js tracing installation](https://posthog.com/docs/distributed-tracing/installation/nodejs.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/frameworks/nextjs.svg)Next.js tracing installation](https://posthog.com/docs/distributed-tracing/installation/nextjs.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/python.svg)Python tracing installation](https://posthog.com/docs/distributed-tracing/installation/python.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/go.svg)Go tracing installation](https://posthog.com/docs/distributed-tracing/installation/go.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/java.svg)Java tracing installation](https://posthog.com/docs/distributed-tracing/installation/java.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/dotnet_logo_7e446176f2.svg).NET tracing installation](https://posthog.com/docs/distributed-tracing/installation/dotnet.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/php.svg)PHP tracing installation](https://posthog.com/docs/distributed-tracing/installation/php.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/ruby.svg)Ruby tracing installation](https://posthog.com/docs/distributed-tracing/installation/ruby.md)

> **Note:** Tracing uses the OpenTelemetry Protocol (OTLP) standard over HTTP. If your language isn't listed, check the [OpenTelemetry documentation](https://opentelemetry.io/docs/languages/) for a compatible SDK and point its OTLP trace exporter at PostHog.
