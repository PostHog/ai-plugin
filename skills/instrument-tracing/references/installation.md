> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Install tracing

Canonical URL: https://posthog.com/docs/distributed-tracing/installation

PostHog Tracing works with any OpenTelemetry-compatible client – point its OTLP trace exporter at PostHog and you're done, with no PostHog-specific packages.

On Node.js and Python, the PostHog SDK can also create and export spans on its own, with no OpenTelemetry dependency. See the [Node.js](https://posthog.com/docs/distributed-tracing/installation/nodejs.md) and [Python](https://posthog.com/docs/distributed-tracing/installation/python.md) guides for both routes.

## SDK support by signal

| SDK | Logs | Traces | Metrics |
| --- | --- | --- | --- |
| [JavaScript web](https://posthog.com/docs/libraries/js.md) (`posthog-js`) | Native, `1.368.0`+ | OpenTelemetry. `posthog-js` doesn't create spans. Use `tracing_headers` to [link requests to sessions](https://posthog.com/docs/libraries/js/config.md#tracing-headers). | Native `posthog.metrics`, `1.399.0`+ |
| [Node.js](https://posthog.com/docs/libraries/node.md) (`posthog-node`) | OpenTelemetry. `posthog-node` has no logs API. | Native, `5.52.0`\+ (experimental), or OpenTelemetry | Native `posthog.metrics`, `5.43.0`+ |
| [Python](https://posthog.com/docs/libraries/python.md) (`posthog`) | OpenTelemetry | Native, `7.58.0`+, or OpenTelemetry | Native `posthog.metrics`, `7.23.0`+ |
| [React Native](https://posthog.com/docs/libraries/react-native.md) | Native, `posthog-react-native@4.44.0`+ | OpenTelemetry | OpenTelemetry |
| [iOS](https://posthog.com/docs/libraries/ios.md) | Native, `posthog-ios@3.58.0`+ | OpenTelemetry | OpenTelemetry |
| [Android](https://posthog.com/docs/libraries/android.md) | Native, `posthog-android@3.46.0`+ | OpenTelemetry | OpenTelemetry |
| [Flutter](https://posthog.com/docs/libraries/flutter.md) | Native, `posthog_flutter@5.27.0`+ | OpenTelemetry | OpenTelemetry |
| Any other language | OpenTelemetry | OpenTelemetry | OpenTelemetry |

"Native" means the PostHog SDK records the signal with no OpenTelemetry packages. "OpenTelemetry" means you send it with an OpenTelemetry SDK or Collector pointed at your PostHog OTLP endpoint (`/i/v1/logs`, `/i/v1/traces`, or `/i/v1/metrics`) and your project token. Every PostHog SDK also captures events natively. Prometheus exporters can send metrics through the [metrics agent](https://posthog.com/docs/metrics/installation.md).

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
