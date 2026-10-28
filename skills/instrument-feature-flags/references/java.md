> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Java Feature Flags installation

Canonical URL: https://posthog.com/docs/feature-flags/installation/java

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.i.posthog.com` instead of `https://us.i.posthog.com` (ingestion host).

## On this page

- [Install with the wizard](#install-with-the-wizard)
- [Integrating with Spring](#integrating-with-spring)
- [Debug mode](#debug-mode)

## Install with the wizard

Run this command in your project directory to add PostHog to your Java project. The wizard detects your framework, installs the SDK, and sets up your first events.

`npx @posthog/wizard`

Or set it up manually by following the rest of this guide.

The best way to install the PostHog Java SDK is with a build system like Gradle or Maven. This ensures you can easily upgrade to the latest versions.

Look up the latest version of [`com.posthog.posthog-server`](https://central.sonatype.com/artifact/com.posthog/posthog-server).

#### Gradle

All you need to do is add the `posthog-server` module to your `build.gradle`:

build.gradle

```kotlin
dependencies {
  implementation 'com.posthog:posthog-server:2.+'
}
```

#### Maven

All you need to do is add the `posthog-server` module to your `pom.xml`:

pom.xml

```xml
<dependency>
  <groupId>com.posthog</groupId>
  <artifactId>posthog-server</artifactId>
  <version>LATEST</version>
</dependency>
```

#### Other

See [`com.posthog.posthog-server`](https://central.sonatype.com/artifact/com.posthog/posthog-server) in the Maven Central Repository. Clicking on the latest version shows you options for adding dependencies for other build systems.

### Setup

```java
import com.posthog.server.PostHog;
import com.posthog.server.PostHogConfig;
import com.posthog.server.PostHogInterface;

class Sample {
  private static final String POSTHOG_API_KEY = "<ph_project_token>";
  private static final String POSTHOG_HOST = "https://us.i.posthog.com";

  public static void main(String args[]) {
    PostHogConfig config = PostHogConfig
            .builder(POSTHOG_API_KEY)
            .host(POSTHOG_HOST)
            .build();

    PostHogInterface posthog = PostHog.with(config);

    posthog.flush(); // send any remaining events
    posthog.close(); // shut down the client
  }
}
```

## Integrating with Spring

To see how to integrate the PostHog SDK with Spring, check out this [sample project](https://github.com/PostHog/posthog-android/tree/main/posthog-samples/posthog-spring-sample).

## Debug mode

If you're not seeing the expected events being captured, or the feature flags being evaluated, you can enable debug mode to see what's happening.

To see detailed logging, set the debug configuration option to true.

```java
PostHogConfig config = PostHogConfig
          .builder(POSTHOG_API_KEY)
          .host(POSTHOG_HOST)
          .debug(true)
          .build();
```
