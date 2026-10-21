> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Upload source maps

Canonical URL: https://posthog.com/docs/error-tracking/upload-source-maps

If you serve compiled or minified code, PostHog requires source maps to generate accurate stack traces.

If your source maps are not publicly hosted, you will need to upload them during your build process to see unminified code in your stack traces.

## AI wizard

If you're using a JavaScript or TypeScript framework, set up source map uploading automatically with our wizard by running this command in your project directory with your terminal (it also works for [LLM coding agents](https://posthog.com/blog/envoy-wizard-llm-agent.md) like Cursor and Bolt):

`npx @posthog/wizard upload-source-maps`

Otherwise, choose your platform below for manual instructions.

## Platforms

Python, Ruby, and PHP apps have no source maps to upload. To link their exceptions to releases, see [link releases](https://posthog.com/docs/error-tracking/link-releases.md).

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/js.svg)Web](https://posthog.com/docs/error-tracking/upload-source-maps/web.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/frameworks/nextjs.svg)Next.js](https://posthog.com/docs/error-tracking/upload-source-maps/nextjs.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/nodejs.svg)Node.js](https://posthog.com/docs/error-tracking/upload-source-maps/node.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/react.svg)React](https://posthog.com/docs/error-tracking/upload-source-maps/react.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/docs/integrate/frameworks/angular.svg)Angular](https://posthog.com/docs/error-tracking/upload-source-maps/angular.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/frameworks/nuxt.svg)Nuxt](https://posthog.com/docs/error-tracking/upload-source-maps/nuxt.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/react.svg)React Native](https://posthog.com/docs/error-tracking/upload-source-maps/react-native.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/Android_robot_bec2fb7318.svg)Android](https://posthog.com/docs/error-tracking/upload-mappings/android.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/flutter.svg)Flutter](https://posthog.com/docs/error-tracking/upload-source-maps/flutter.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/go.svg)Go](https://posthog.com/docs/error-tracking/upload-source-maps/go.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/ios.svg)iOS](https://posthog.com/docs/error-tracking/upload-source-maps/ios.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/kmp.svg)Kotlin Multiplatform](https://posthog.com/docs/error-tracking/upload-debug-symbols/kmp.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/rust.svg)Rust](https://posthog.com/docs/error-tracking/upload-source-maps/rust.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/Rollup_js_c306a2fde3.svg)Rollup](https://posthog.com/docs/error-tracking/upload-source-maps/rollup.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/webpack_3fc774b5a5.svg)Webpack](https://posthog.com/docs/error-tracking/upload-source-maps/webpack.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/Vitejs_logo_98ffe5d5ee.svg)Vite](https://posthog.com/docs/error-tracking/upload-source-maps/vite.md)

-   [CLI](https://posthog.com/docs/error-tracking/upload-source-maps/cli.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/github_mark_903e35d471.svg)GitHub Action](https://posthog.com/docs/error-tracking/upload-source-maps/github-actions.md)
