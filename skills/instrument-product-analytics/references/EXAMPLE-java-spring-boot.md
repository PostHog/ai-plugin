# PostHog java-spring-boot Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/java-spring-boot

---

## README.md

# PostHog Spring Boot example

This is a [Spring Boot](https://spring.io/projects/spring-boot) example demonstrating PostHog integration with product analytics, feature flags, and user identification using the server-side Java SDK.

## Features

- **Product analytics**: Track user events and behaviors
- **User identification**: Associate events with authenticated users via person properties; signed-out visitors get a random id and anonymous events
- **Feature flags**: Control feature rollouts with PostHog feature flags
- **Server-side tracking**: All tracking happens server-side with the `posthog-server` SDK
- **Single client bean**: One PostHog client for the whole app, flushed on shutdown

> **Note on error tracking:** the PostHog Java server SDK does not have automatic
> exception capture. This example reports failures as an explicit `error_occurred`
> event instead. Do not expect session replay or surveys from the server SDK either.

## Getting started

### 1. Configure environment variables

Copy `.env.example` to `.env` and fill in your values, then export them:

```bash
export POSTHOG_PROJECT_TOKEN=your_posthog_project_token
export POSTHOG_HOST=https://us.i.posthog.com
```

Get your PostHog project token from your [PostHog project settings](https://app.posthog.com/project/settings).

### 2. Run the app

```bash
./gradlew bootRun
```

Open [http://localhost:8000](http://localhost:8000) with your browser to see the app.

## Project structure

```
java-spring-boot/
├── build.gradle                 # Gradle build with the posthog-server dependency
├── settings.gradle
├── .env.example                 # Environment variable template
├── .gitignore
└── src/main/
    ├── resources/
    │   ├── application.properties   # Binds POSTHOG_* env vars into config
    │   └── templates/               # Thymeleaf pages
    │       ├── home.html            # Home / login page
    │       ├── burrito.html         # Event tracking
    │       ├── dashboard.html       # Feature flag example
    │       └── profile.html         # Error reporting
    └── java/com/posthog/example/
        ├── Application.java         # Spring Boot entry point
        ├── config/
        │   └── PostHogConfiguration.java   # The single PostHog client bean
        └── controller/
            └── BurritoController.java      # Events, identify, flags, errors
```

## Key integration points

### PostHog client bean (config/PostHogConfiguration.java)

Create **one client per process** and expose it as a singleton bean. `destroyMethod = "close"` makes Spring flush queued events when the app shuts down.

```java
@Bean(destroyMethod = "close")
public PostHogInterface posthog(
        @Value("${posthog.project-token:}") String projectToken,
        @Value("${posthog.host:https://us.i.posthog.com}") String host) {

    PostHogConfig config = PostHogConfig
            .builder(projectToken)
            .host(host)
            .build();

    return PostHog.with(config);
}
```

### Configuration from the environment (application.properties)

Read the token and host from the environment so secrets never live in source:

```properties
posthog.project-token=${POSTHOG_PROJECT_TOKEN:}
posthog.host=${POSTHOG_HOST:https://us.i.posthog.com}
```

### User identification (controller/BurritoController.java)

The server SDK identifies a user by attaching person properties to a capture with `userProperty(...)`. The `distinctId` (first argument) must match the id your frontend `identify` call uses.

```java
posthog.capture(
        userId,
        "user_logged_in",
        PostHogCaptureOptions
                .builder()
                .userProperty("email", email)
                .property("login_method", "email")
                .build());
```

### Signed-out visitors (controller/BurritoController.java)

The `visitor` helper returns the distinct id and whether the visitor is anonymous. Signed-in users keep their stable user id from the session. For everyone else it generates a random UUID, stores it in the session (which is cookie-backed) so it is reused for the rest of the visit, and sets `$process_person_profile` to `false` on their events so PostHog does not create a person profile for them.

```java
Visitor visitor = visitor(session);

PostHogCaptureOptions.Builder options = PostHogCaptureOptions
        .builder()
        .property("total_considerations", count);
if (visitor.anonymous()) {
    options.property("$process_person_profile", false);
}
posthog.capture(visitor.id(), "burrito_considered", options.build());
```

Feature flags use the same visitor id, so flag evaluation works for anonymous visitors too.

### Event tracking (controller/BurritoController.java)

```java
Visitor visitor = visitor(session);
PostHogCaptureOptions.Builder options = PostHogCaptureOptions
        .builder()
        .property("total_considerations", count);
if (visitor.anonymous()) {
    options.property("$process_person_profile", false);
}
posthog.capture(visitor.id(), "burrito_considered", options.build());
```

### Feature flags (controller/BurritoController.java)

Evaluate flags once per request, then read individual flags off the snapshot. Avoid the deprecated per-flag helpers.

```java
PostHogFeatureFlagEvaluations flags = posthog.evaluateFlags(userId);
boolean showNewFeature = flags.isEnabled("new-dashboard-feature");
```

### Error reporting (controller/BurritoController.java)

There is no automatic exception capture in the Java server SDK, so report failures as an explicit event:

```java
try {
    riskyOperation();
} catch (RuntimeException e) {
    posthog.capture(
            userId,
            "error_occurred",
            PostHogCaptureOptions
                    .builder()
                    .property("error_type", e.getClass().getSimpleName())
                    .property("error_message", e.getMessage())
                    .build());
}
```

### Flush and shutdown

`destroyMethod = "close"` on the bean handles this for you at shutdown. If you ever
manage the client yourself, flush and close explicitly:

```java
posthog.flush(); // send any remaining events
posthog.close(); // shut down the client
```

## Learn more

- [PostHog Java integration](https://posthog.com/docs/libraries/java)
- [PostHog feature flags](https://posthog.com/docs/feature-flags)
- [PostHog documentation](https://posthog.com/docs)
- [Spring Boot documentation](https://spring.io/projects/spring-boot)

---

## .env.example

```example
POSTHOG_PROJECT_TOKEN=
POSTHOG_HOST=https://us.i.posthog.com

```

---

## src/main/java/com/posthog/example/Application.java

```java
package com.posthog.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Entry point for the PostHog Spring Boot example.
 *
 * <p>The interesting integration code lives in:
 * <ul>
 *   <li>{@link com.posthog.example.config.PostHogConfiguration} &mdash; the single
 *       PostHog client, exposed as a Spring bean and flushed on shutdown.</li>
 *   <li>{@link com.posthog.example.controller.BurritoController} &mdash; where events,
 *       user identification, feature flags, and error reporting happen.</li>
 * </ul>
 */
@SpringBootApplication
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}

```

---

## src/main/java/com/posthog/example/config/PostHogConfiguration.java

```java
package com.posthog.example.config;

import com.posthog.server.PostHog;
import com.posthog.server.PostHogConfig;
import com.posthog.server.PostHogInterface;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Wires a single PostHog client into the Spring context.
 *
 * <p>Key integration points demonstrated here:
 * <ul>
 *   <li><b>One client per process.</b> The client is a {@code @Bean}, so Spring
 *       creates exactly one instance and injects it everywhere. Never construct a
 *       new client per request.</li>
 *   <li><b>Config from the environment.</b> The project token and host are read
 *       from configuration (backed by env vars) &mdash; secrets are never hardcoded.</li>
 *   <li><b>Flush on shutdown.</b> {@code destroyMethod = "close"} makes Spring call
 *       {@link PostHogInterface#close()} when the context shuts down, so queued
 *       events are flushed before the JVM exits.</li>
 *   <li><b>Fail loudly, but never break the app.</b> A missing token logs a clear
 *       warning instead of throwing, so a misconfigured environment is obvious in
 *       dev without taking the whole service down.</li>
 * </ul>
 */
@Configuration
public class PostHogConfiguration {

    private static final Logger log = LoggerFactory.getLogger(PostHogConfiguration.class);

    @Bean(destroyMethod = "close")
    public PostHogInterface posthog(
            @Value("${posthog.project-token:}") String projectToken,
            @Value("${posthog.host:https://us.i.posthog.com}") String host) {

        if (projectToken == null || projectToken.isBlank()) {
            log.warn("POSTHOG_PROJECT_TOKEN is not set. PostHog events will not be delivered. "
                    + "Set it in your environment (see .env.example) to enable analytics.");
        }

        PostHogConfig config = PostHogConfig
                .builder(projectToken)
                .host(host)
                .build();

        return PostHog.with(config);
    }
}

```

---

## src/main/java/com/posthog/example/controller/BurritoController.java

```java
package com.posthog.example.controller;

import com.posthog.server.PostHogCaptureOptions;
import com.posthog.server.PostHogFeatureFlagEvaluations;
import com.posthog.server.PostHogInterface;
import jakarta.servlet.http.HttpSession;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

/**
 * A tiny "burrito" app that mirrors the other PostHog example apps.
 *
 * <p>Each handler shows one integration point. The PostHog client is injected once
 * (constructor injection) and reused &mdash; the same singleton bean from
 * {@link com.posthog.example.config.PostHogConfiguration}.
 */
@Controller
public class BurritoController {

    private static final Logger log = LoggerFactory.getLogger(BurritoController.class);

    private final PostHogInterface posthog;

    public BurritoController(PostHogInterface posthog) {
        this.posthog = posthog;
    }

    /** Home / login page. */
    @GetMapping("/")
    public String home(HttpSession session, Model model) {
        // Only signed-in users have a "userId"; anonymous visitors see the login form.
        model.addAttribute("userId", session.getAttribute("userId"));
        return "home";
    }

    /**
     * User identification.
     *
     * <p>The server SDK identifies a user by attaching person properties to a capture
     * via {@code userProperty(...)}. The {@code distinctId} (first argument) is the
     * stable user id and must match the id used by your frontend {@code identify} call.
     *
     * <p><b>Identity note:</b> this demo takes the id from a form field for simplicity.
     * A real app must derive {@code distinctId} from the authenticated principal
     * (session / JWT), never from an unverified request parameter — otherwise a client
     * could pick any id and overwrite another person's profile.
     */
    @PostMapping("/login")
    public String login(@RequestParam String userId,
                        @RequestParam(required = false) String email,
                        HttpSession session) {
        session.setAttribute("userId", userId);

        posthog.capture(
                userId,
                "user_logged_in",
                PostHogCaptureOptions
                        .builder()
                        .userProperty("email", email == null ? "" : email)
                        .property("login_method", "email")
                        .build());

        return "redirect:/";
    }

    /**
     * Event tracking.
     *
     * <p>Capture a meaningful business event with the visitor's distinct id and a couple of
     * event properties. Keep PII in person properties (see {@link #login}), not here.
     */
    @PostMapping("/burrito")
    public String considerBurrito(HttpSession session, Model model) {
        Visitor visitor = visitor(session);
        Object previous = session.getAttribute("burritoCount");
        int count = (previous == null ? 0 : (int) previous) + 1;
        session.setAttribute("burritoCount", count);

        PostHogCaptureOptions.Builder options = PostHogCaptureOptions
                .builder()
                .property("total_considerations", count);
        posthog.capture(visitor.id(), "burrito_considered", withPersonProfile(options, visitor).build());

        model.addAttribute("count", count);
        return "burrito";
    }

    /**
     * Feature flags.
     *
     * <p>Evaluate flags once per request with {@code evaluateFlags(distinctId)}, then read
     * individual flags off the returned snapshot. Avoid the deprecated per-flag helpers.
     */
    @GetMapping("/dashboard")
    public String dashboard(HttpSession session, Model model) {
        String userId = visitor(session).id();

        // evaluateFlags makes a network call; if PostHog is slow or down it can throw.
        // Never let flag evaluation take the page down — fall back to the flag being off.
        // (This fetches on every request; a real app should cache/bound it, not fetch per render.)
        boolean showNewFeature = false;
        try {
            PostHogFeatureFlagEvaluations flags = posthog.evaluateFlags(userId);
            showNewFeature = flags.isEnabled("new-dashboard-feature");
        } catch (RuntimeException e) {
            log.warn("feature flag evaluation failed", e);
        }

        model.addAttribute("showNewFeature", showNewFeature);
        return "dashboard";
    }

    /**
     * Error reporting.
     *
     * <p>Note: the PostHog Java server SDK does not have automatic exception capture, so
     * we report failures as an explicit event with the exception details. Do not promise
     * or scaffold error-tracking features the SDK does not support.
     */
    @GetMapping("/profile")
    public String profile(HttpSession session, Model model) {
        Visitor visitor = visitor(session);
        String userId = visitor.id();
        try {
            riskyOperation();
        } catch (RuntimeException e) {
            log.warn("profile risky_operation failed", e);
            PostHogCaptureOptions.Builder options = PostHogCaptureOptions
                    .builder()
                    .property("error_type", e.getClass().getSimpleName())
                    .property("error_message", e.getMessage())
                    .property("source", "profile_view");
            posthog.capture(userId, "error_occurred", withPersonProfile(options, visitor).build());
            model.addAttribute("error", e.getMessage());
        }
        model.addAttribute("userId", userId);
        return "profile";
    }

    private void riskyOperation() {
        throw new IllegalStateException("profile data source is temporarily unavailable");
    }

    /** The distinct id for the current request and whether the visitor is anonymous. */
    private record Visitor(String id, boolean anonymous) {}

    /**
     * Resolves the distinct id. Signed-in users keep their stable user id (it must match
     * your frontend {@code identify} call). Signed-out visitors get a random UUID kept in
     * the session, so it is reused for the rest of the visit instead of every visitor
     * sharing one id.
     */
    private Visitor visitor(HttpSession session) {
        Object userId = session.getAttribute("userId");
        if (userId != null) {
            return new Visitor(userId.toString(), false);
        }
        Object anonymousId = session.getAttribute("anonymousId");
        if (anonymousId == null) {
            anonymousId = UUID.randomUUID().toString();
            session.setAttribute("anonymousId", anonymousId);
        }
        return new Visitor(anonymousId.toString(), true);
    }

    /**
     * Anonymous events set {@code $process_person_profile} to false so PostHog does not
     * create a person profile for the visitor.
     */
    private PostHogCaptureOptions.Builder withPersonProfile(PostHogCaptureOptions.Builder options, Visitor visitor) {
        return visitor.anonymous() ? options.property("$process_person_profile", false) : options;
    }
}

```

---

## src/main/resources/application.properties

```properties
# PostHog configuration.
# Values come from the environment so secrets never live in source.
# See .env.example for the variables this app expects.
posthog.project-token=${POSTHOG_PROJECT_TOKEN:}
posthog.host=${POSTHOG_HOST:https://us.i.posthog.com}

# Do not cache Thymeleaf templates during local development.
spring.thymeleaf.cache=false
server.port=8000

```

---

## src/main/resources/templates/burrito.html

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head><title>Burrito considered</title></head>
<body>
  <h1>🌯 Burrito considered</h1>
  <p>You have considered a burrito <strong th:text="${count}">0</strong> time(s).</p>
  <p>A <code>burrito_considered</code> event was sent to PostHog.</p>
  <a href="/">Back home</a>
</body>
</html>

```

---

## src/main/resources/templates/dashboard.html

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head><title>Dashboard</title></head>
<body>
  <h1>Dashboard</h1>
  <p th:if="${showNewFeature}">✨ The <code>new-dashboard-feature</code> flag is enabled for you.</p>
  <p th:unless="${showNewFeature}">The <code>new-dashboard-feature</code> flag is off for you.</p>
  <a href="/">Back home</a>
</body>
</html>

```

---

## src/main/resources/templates/home.html

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head><title>PostHog Spring Boot example</title></head>
<body>
  <h1>🌯 Burrito app</h1>

  <div th:if="${userId}">
    <p>Logged in as <strong th:text="${userId}">user</strong>.</p>
    <ul>
      <li><a href="/dashboard">Dashboard (feature flag)</a></li>
      <li><a href="/profile">Profile (error reporting)</a></li>
    </ul>
    <form method="post" action="/burrito">
      <button type="submit">Consider a burrito (track event)</button>
    </form>
  </div>

  <form th:unless="${userId}" method="post" action="/login">
    <p>Log in to identify yourself with PostHog:</p>
    <input name="userId" placeholder="user id" required />
    <input name="email" placeholder="email" type="email" />
    <button type="submit">Log in</button>
  </form>
</body>
</html>

```

---

## src/main/resources/templates/profile.html

```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head><title>Profile</title></head>
<body>
  <h1>Profile</h1>
  <p th:if="${error}">Something went wrong: <strong th:text="${error}">error</strong>.</p>
  <p th:if="${error}">An <code>error_occurred</code> event was sent to PostHog.</p>
  <a href="/">Back home</a>
</body>
</html>

```

---

