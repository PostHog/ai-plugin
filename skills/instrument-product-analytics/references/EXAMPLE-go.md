# PostHog go Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/go

---

## README.md

# PostHog Go example

This is a [Go](https://go.dev) example demonstrating PostHog integration with product analytics, feature flags, user identification, and error tracking using the server-side Go SDK and the standard library `net/http`.

## Features

- **Product analytics**: Track user events and behaviors
- **User identification**: Associate events with a user via person properties (`$set`); signed-out visitors get a random id and anonymous events
- **Feature flags**: Control feature rollouts with PostHog feature flags
- **Error tracking**: Report exceptions to PostHog error tracking
- **Server-side tracking**: All tracking happens server-side with the `posthog-go` SDK
- **Single client per process**: One PostHog client for the whole app, flushed on shutdown

## Getting started

### 1. Install dependencies

```bash
go get github.com/posthog/posthog-go
```

### 2. Configure environment variables

Copy `.env.example` to `.env` and fill in your values, then export them:

```bash
export POSTHOG_PROJECT_TOKEN=your_posthog_project_token
export POSTHOG_HOST=https://us.i.posthog.com
```

Get your PostHog project token from your [PostHog project settings](https://app.posthog.com/project/settings).

### 3. Run the app

```bash
go run .
```

Open [http://localhost:8000](http://localhost:8000) with your browser to see the app.

## Project structure

```
go/
├── go.mod            # Module definition and the posthog-go dependency
├── .env.example      # Environment variable template
├── .gitignore
├── main.go           # Entry point: server wiring + graceful shutdown
├── posthog.go        # The single PostHog client (config from env)
└── handlers.go       # Routes: identify, events, flags, error tracking
```

## Key integration points

### PostHog client (posthog.go)

Create **one client per process** with `posthog.NewWithConfig` and share it across every request. Never construct a new client per request — the SDK batches events on a background goroutine.

```go
client, err := posthog.NewWithConfig(projectToken, posthog.Config{
    Endpoint: host,
})
```

### Configuration from the environment (posthog.go)

Read the token and host from the environment so secrets never live in source. A blank token logs a clear warning and the app keeps running.

```go
projectToken := os.Getenv("POSTHOG_PROJECT_TOKEN")

host := os.Getenv("POSTHOG_HOST")
if host == "" {
    host = "https://us.i.posthog.com"
}

if projectToken == "" {
    log.Println("WARNING: POSTHOG_PROJECT_TOKEN is not set. PostHog events will not be delivered.")
}
```

### User identification (handlers.go)

The Go SDK identifies a user by capturing an event whose properties include `$set` (person properties). The `DistinctId` is the stable user id and must match the id your frontend `identify` call uses.

```go
client.Enqueue(posthog.Capture{
    DistinctId: userId,
    Event:      "user_logged_in",
    Properties: posthog.NewProperties().
        Set("login_method", "email").
        Set("$set", map[string]any{"email": email}),
})
```

### Signed-out visitors (handlers.go)

The `visitor` helper returns the distinct id and whether the visitor is anonymous. Signed-in users (a `user_id` cookie) keep their stable user id. For everyone else it generates a random UUID, stores it in an `anon_id` cookie so it is reused for the rest of the visit, and the `properties` helper sets `$process_person_profile` to `false` so PostHog does not create a person profile for them.

```go
userId, anonymous := visitor(w, r)

client.Enqueue(posthog.Capture{
    DistinctId: userId,
    Event:      "burrito_considered",
    Properties: properties(anonymous), // adds $process_person_profile=false when anonymous
})
```

Feature flags use the same visitor id, so flag evaluation works for anonymous visitors too.

### Event tracking (handlers.go)

Capture a business event with the visitor's distinct id and a couple of event properties.

```go
client.Enqueue(posthog.Capture{
    DistinctId: userId,
    Event:      "burrito_considered",
    Properties: properties(anonymous).
        Set("total_considerations", count),
})
```

### Feature flags (handlers.go)

Evaluate flags once per request with `EvaluateFlags`, then read individual flags off the returned snapshot with `IsEnabled`. This is the current API — avoid the deprecated per-flag helpers.

```go
flags, err := client.EvaluateFlags(posthog.EvaluateFlagsPayload{
    DistinctId: userId,
    FlagKeys:   []string{"new-dashboard-feature"},
})
if err == nil {
    showNewFeature := flags.IsEnabled("new-dashboard-feature")
    // ... branch on showNewFeature
}
```

### Error tracking (handlers.go)

Report an exception with `posthog.NewDefaultException` (timestamp, distinct id, exception type, message) and enqueue it like any other event.

```go
if err := riskyOperation(); err != nil {
    exception := posthog.NewDefaultException(
        time.Now(),
        userId,
        "ProfileDataError",
        err.Error(),
    )
    client.Enqueue(exception)
}
```

### Flush and shutdown (main.go)

Call `client.Close()` on shutdown so the background batch of queued events is flushed before the process exits. Here it is wired to `SIGINT`/`SIGTERM`.

```go
stop := make(chan os.Signal, 1)
signal.Notify(stop, syscall.SIGINT, syscall.SIGTERM)
<-stop

if err := client.Close(); err != nil {
    log.Printf("error closing PostHog client: %v", err)
}
```

## Learn more

- [PostHog Go integration](https://posthog.com/docs/libraries/go)
- [PostHog feature flags](https://posthog.com/docs/feature-flags)
- [PostHog error tracking](https://posthog.com/docs/error-tracking)
- [PostHog documentation](https://posthog.com/docs)
- [Go documentation](https://go.dev/doc/)

---

## .env.example

```example
POSTHOG_PROJECT_TOKEN=
POSTHOG_HOST=https://us.i.posthog.com

```

---

## go.mod

```mod
module posthog-go-example

go 1.22

require (
	github.com/google/uuid v1.6.0
	github.com/posthog/posthog-go v1.42.2
)

require (
	github.com/andybalholm/brotli v1.1.1 // indirect
	github.com/goccy/go-json v0.10.6 // indirect
	github.com/hashicorp/golang-lru/v2 v2.0.7 // indirect
	github.com/klauspost/compress v1.17.11 // indirect
	golang.org/x/sys v0.21.0 // indirect
	golang.org/x/text v0.21.0 // indirect
)

```

---

## go.sum

```sum
github.com/andybalholm/brotli v1.1.1 h1:PR2pgnyFznKEugtsUo0xLdDop5SKXd5Qf5ysW+7XdTA=
github.com/andybalholm/brotli v1.1.1/go.mod h1:05ib4cKhjx3OQYUY22hTVd34Bc8upXjOLL2rKwwZBoA=
github.com/davecgh/go-spew v1.1.1 h1:vj9j/u1bqnvCEfJOwUhtlOARqs3+rkHYY13jYWTU97c=
github.com/davecgh/go-spew v1.1.1/go.mod h1:J7Y8YcW2NihsgmVo/mv3lAwl/skON4iLHjSsI+c5H38=
github.com/goccy/go-json v0.10.6 h1:p8HrPJzOakx/mn/bQtjgNjdTcN+/S6FcG2CTtQOrHVU=
github.com/goccy/go-json v0.10.6/go.mod h1:oq7eo15ShAhp70Anwd5lgX2pLfOS3QCiwU/PULtXL6M=
github.com/google/go-cmp v0.7.0 h1:wk8382ETsv4JYUZwIsn6YpYiWiBsYLSJiTsyBybVuN8=
github.com/google/go-cmp v0.7.0/go.mod h1:pXiqmnSA92OHEEa9HXL2W4E7lf9JzCmGVUdgjX3N/iU=
github.com/google/uuid v1.6.0 h1:NIvaJDMOsjHA8n1jAhLSgzrAzy1Hgr+hNrb57e+94F0=
github.com/google/uuid v1.6.0/go.mod h1:TIyPZe4MgqvfeYDBFedMoGGpEw/LqOeaOT+nhxU+yHo=
github.com/hashicorp/golang-lru/v2 v2.0.7 h1:a+bsQ5rvGLjzHuww6tVxozPZFVghXaHOwFs4luLUK2k=
github.com/hashicorp/golang-lru/v2 v2.0.7/go.mod h1:QeFd9opnmA6QUJc5vARoKUSoFhyfM2/ZepoAG6RGpeM=
github.com/klauspost/compress v1.17.11 h1:In6xLpyWOi1+C7tXUUWv2ot1QvBjxevKAaI6IXrJmUc=
github.com/klauspost/compress v1.17.11/go.mod h1:pMDklpSncoRMuLFrf1W9Ss9KT+0rH90U12bZKk7uwG0=
github.com/pmezard/go-difflib v1.0.0 h1:4DBwDE0NGyQoBHbLQYPwSUPoCMWR5BEzIk/f1lZbAQM=
github.com/pmezard/go-difflib v1.0.0/go.mod h1:iKH77koFhYxTK1pcRnkKkqfTogsbg7gZNVY4sRDYZ/4=
github.com/posthog/posthog-go v1.42.2 h1:JBrGCH9xyBrbmpffHAL5cJTrlW3/eSFD2SvlsFrgduk=
github.com/posthog/posthog-go v1.42.2/go.mod h1:rN0C9Urenhytgo3KQ/QVorGkyGfpouquDTSs2Ujzr+g=
github.com/stretchr/testify v1.11.1 h1:7s2iGBzp5EwR7/aIZr8ao5+dra3wiQyKjjFuvgVKu7U=
github.com/stretchr/testify v1.11.1/go.mod h1:wZwfW3scLgRK+23gO65QZefKpKQRnfz6sD981Nm4B6U=
github.com/xyproto/randomstring v1.0.5 h1:YtlWPoRdgMu3NZtP45drfy1GKoojuR7hmRcnhZqKjWU=
github.com/xyproto/randomstring v1.0.5/go.mod h1:rgmS5DeNXLivK7YprL0pY+lTuhNQW3iGxZ18UQApw/E=
golang.org/x/sys v0.21.0 h1:rF+pYz3DAGSQAxAu1CbC7catZg4ebC4UIeIhKxBZvws=
golang.org/x/sys v0.21.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
golang.org/x/text v0.21.0 h1:zyQAAkrwaneQ066sspRyJaG9VNi/YJ1NfzcGB3hZ/qo=
golang.org/x/text v0.21.0/go.mod h1:4IBbMaMmOPCJ8SecivzSH54+73PCFmPWxNTLm+vZkEQ=
gopkg.in/yaml.v3 v3.0.1 h1:fxVm/GzAzEWqLHuvctI91KS9hhNmmWOoWu0XTYJS7CA=
gopkg.in/yaml.v3 v3.0.1/go.mod h1:K4uyk7z7BCEPqu6E+C64Yfv1cQ7kz7rIZviUmN+EgEM=

```

---

## handlers.go

```go
package main

import (
	"errors"
	"fmt"
	"html"
	"log"
	"net/http"
	"time"

	"github.com/google/uuid"
	"github.com/posthog/posthog-go"
)

// app holds the shared dependencies for every request handler. The single
// PostHog client lives here and is reused across all requests.
type app struct {
	posthog posthog.Client
}

// visitor returns the distinct id for the current request and whether the
// visitor is anonymous.
//
// Signed-in users have a "user_id" cookie; that stable id is the join key for
// all analytics and MUST match the id your frontend `posthog.identify(...)`
// call uses so server- and client-side events land on the same person.
//
// Signed-out visitors get a random UUID stored in a cookie so it is reused for
// the rest of the visit. Never share one fixed id across visitors: they would
// all collapse into a single person.
func visitor(w http.ResponseWriter, r *http.Request) (id string, anonymous bool) {
	if c, err := r.Cookie("user_id"); err == nil && c.Value != "" {
		return c.Value, false
	}
	if c, err := r.Cookie("anon_id"); err == nil && c.Value != "" {
		return c.Value, true
	}
	id = uuid.NewString()
	http.SetCookie(w, &http.Cookie{
		Name: "anon_id", Value: id, Path: "/",
		HttpOnly: true, Secure: true, SameSite: http.SameSiteLaxMode,
	})
	return id, true
}

// properties returns event properties for a capture. Anonymous events set
// "$process_person_profile" to false so PostHog does not create a person
// profile for the visitor.
func properties(anonymous bool) posthog.Properties {
	props := posthog.NewProperties()
	if anonymous {
		props.Set("$process_person_profile", false)
	}
	return props
}

// home renders the login form (or a short greeting once logged in).
func (a *app) home(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path != "/" {
		http.NotFound(w, r)
		return
	}
	id, anonymous := visitor(w, r)
	status := "Signed in as"
	if anonymous {
		status = "Not signed in, anonymous visitor"
	}
	page(w, "Burrito app", fmt.Sprintf(`
		<p>%s: <strong>%s</strong></p>
		<form method="POST" action="/login">
			<label>User id <input name="user_id" value="burrito-fan-42"></label>
			<label>Email <input name="email" value="fan@example.com"></label>
			<button type="submit">Log in</button>
		</form>
		<ul>
			<li><a href="/burrito">Consider a burrito</a> (event tracking)</li>
			<li><a href="/dashboard">Dashboard</a> (feature flag)</li>
			<li><a href="/profile">Profile</a> (error tracking)</li>
		</ul>`, status, html.EscapeString(id)))
}

// login demonstrates user identification.
//
// The Go SDK identifies a user by capturing an event with person properties set
// via the "$set" property. The DistinctId is the stable user id and must match
// the id used by your frontend identify() call.
func (a *app) login(w http.ResponseWriter, r *http.Request) {
	userId := r.FormValue("user_id")
	if userId == "" {
		userId = "burrito-fan-42"
	}
	email := r.FormValue("email")

	// Persist the id in a simple cookie so later requests are attributed.
	// HttpOnly keeps it away from client-side JS; Secure sends it over HTTPS
	// only; SameSite guards against CSRF.
	http.SetCookie(w, &http.Cookie{
		Name: "user_id", Value: userId, Path: "/",
		HttpOnly: true, Secure: true, SameSite: http.SameSiteLaxMode,
	})

	a.posthog.Enqueue(posthog.Capture{
		DistinctId: userId,
		Event:      "user_logged_in",
		Properties: posthog.NewProperties().
			Set("login_method", "email").
			// "$set" attaches person properties to this distinct id — the
			// server-side equivalent of identify().
			Set("$set", map[string]any{"email": email}),
	})

	http.Redirect(w, r, "/", http.StatusSeeOther)
}

// burrito demonstrates event tracking: capture a business event with a stable
// distinct id and a couple of event properties.
func (a *app) burrito(w http.ResponseWriter, r *http.Request) {
	userId, anonymous := visitor(w, r)

	// Toy per-session counter kept in a cookie — just so the event has a
	// changing property to show off.
	count := 1
	if c, err := r.Cookie("burrito_count"); err == nil {
		fmt.Sscanf(c.Value, "%d", &count)
		count++
	}
	http.SetCookie(w, &http.Cookie{
		Name: "burrito_count", Value: fmt.Sprintf("%d", count), Path: "/",
		HttpOnly: true, Secure: true, SameSite: http.SameSiteLaxMode,
	})

	a.posthog.Enqueue(posthog.Capture{
		DistinctId: userId,
		Event:      "burrito_considered",
		Properties: properties(anonymous).
			Set("total_considerations", count),
	})

	page(w, "Burrito considered", fmt.Sprintf(`
		<p>You have considered a burrito <strong>%d</strong> time(s).</p>
		<p>A <code>burrito_considered</code> event was captured for <code>%s</code>.</p>
		<p><a href="/">Back home</a></p>`, count, html.EscapeString(userId)))
}

// dashboard demonstrates feature flag evaluation.
//
// Evaluate flags once per request with EvaluateFlags, then read individual flags
// off the returned snapshot with IsEnabled. This is the current API — avoid the
// deprecated per-flag IsFeatureEnabled/GetFeatureFlag helpers.
func (a *app) dashboard(w http.ResponseWriter, r *http.Request) {
	userId, _ := visitor(w, r)

	showNewFeature := false
	flags, err := a.posthog.EvaluateFlags(posthog.EvaluateFlagsPayload{
		DistinctId: userId,
		FlagKeys:   []string{"new-dashboard-feature"},
	})
	if err != nil {
		// Flag evaluation failing should never take the page down — log it and
		// fall back to the flag being off.
		log.Printf("feature flag evaluation failed: %v", err)
	} else {
		showNewFeature = flags.IsEnabled("new-dashboard-feature")
	}

	body := "<p>You are seeing the <strong>standard</strong> dashboard.</p>"
	if showNewFeature {
		body = "<p>🎉 You are seeing the <strong>new</strong> dashboard feature!</p>"
	}
	page(w, "Dashboard", body+fmt.Sprintf(`
		<p>Flag <code>new-dashboard-feature</code> for <code>%s</code>: <strong>%t</strong></p>
		<p><a href="/">Back home</a></p>`, html.EscapeString(userId), showNewFeature))
}

// profile demonstrates error tracking.
//
// The Go SDK captures exceptions via posthog.NewDefaultException, which is then
// enqueued like any other event. We deliberately trigger a failure, catch it,
// and report it — the app keeps serving.
func (a *app) profile(w http.ResponseWriter, r *http.Request) {
	userId, anonymous := visitor(w, r)

	var caught string
	if err := riskyOperation(); err != nil {
		caught = err.Error()
		log.Printf("profile risky_operation failed: %v", err)

		// Report the exception to PostHog error tracking. Arguments in order:
		// timestamp, distinct id, exception type (shown as the title), message.
		exception := posthog.NewDefaultException(
			time.Now(),
			userId,
			"ProfileDataError",
			caught,
		)
		exception.Properties = properties(anonymous)
		a.posthog.Enqueue(exception)
	}

	page(w, "Profile", fmt.Sprintf(`
		<p>User: <strong>%s</strong></p>
		<p>Triggered and captured an exception: <code>%s</code></p>
		<p><a href="/">Back home</a></p>`, html.EscapeString(userId), html.EscapeString(caught)))
}

func riskyOperation() error {
	return errors.New("profile data source is temporarily unavailable")
}

// page writes a minimal HTML document so the example needs no template files.
func page(w http.ResponseWriter, title, body string) {
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	fmt.Fprintf(w, `<!doctype html><html><head><meta charset="utf-8">`+
		`<title>%s</title></head><body><h1>%s</h1>%s</body></html>`, title, title, body)
}

```

---

## main.go

```go
// Command posthog-go-example is a tiny "burrito app" that mirrors the other
// PostHog example apps. Each route shows one server-side integration point:
//
//	/          home / login form
//	/login     user identification (capture with $set person properties)
//	/burrito   event tracking (burrito_considered)
//	/dashboard feature flags (new-dashboard-feature via EvaluateFlags)
//	/profile   error tracking (NewDefaultException)
//
// The PostHog client is created once and flushed on shutdown.
package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"
)

func main() {
	// One client per process. Created here, shared by every handler, closed on
	// shutdown so queued events flush before we exit.
	client := newPostHogClient()

	a := &app{posthog: client}

	mux := http.NewServeMux()
	mux.HandleFunc("/", a.home)
	mux.HandleFunc("/login", a.login)
	mux.HandleFunc("/burrito", a.burrito)
	mux.HandleFunc("/dashboard", a.dashboard)
	mux.HandleFunc("/profile", a.profile)

	srv := &http.Server{Addr: ":8000", Handler: mux}

	// Graceful shutdown: on SIGINT/SIGTERM, stop the server and Close() the
	// PostHog client so the background batch of events is flushed before exit.
	// Close() blocks until the queue drains — skipping it can drop events.
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		log.Println("listening on http://localhost:8000")
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("server error: %v", err)
		}
	}()

	<-stop
	log.Println("shutting down...")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := srv.Shutdown(ctx); err != nil {
		log.Printf("graceful shutdown failed: %v", err)
	}

	// Flush and shut down the PostHog client.
	if err := client.Close(); err != nil {
		log.Printf("error closing PostHog client: %v", err)
	}
	log.Println("bye")
}

```

---

## posthog.go

```go
package main

import (
	"log"
	"os"

	"github.com/posthog/posthog-go"
)

// newPostHogClient builds the single, process-wide PostHog client.
//
// Key integration points demonstrated here:
//   - One client per process. This is called exactly once from main and the
//     returned client is shared by every request handler. Never construct a new
//     client per request — the SDK batches events on a background goroutine, and
//     a fresh client per request would defeat that and leak resources.
//   - Config from the environment. The project token and host come from env vars
//     (see .env.example) so secrets never live in source.
//   - Fail loudly, but never break the app. A blank token logs a clear warning
//     and we continue with a client anyway; the app stays up, and the missing
//     config is obvious in the logs.
func newPostHogClient() posthog.Client {
	projectToken := os.Getenv("POSTHOG_PROJECT_TOKEN")

	host := os.Getenv("POSTHOG_HOST")
	if host == "" {
		host = "https://us.i.posthog.com"
	}

	if projectToken == "" {
		log.Println("WARNING: POSTHOG_PROJECT_TOKEN is not set. PostHog events will " +
			"not be delivered. Set it in your environment (see .env.example) to enable analytics.")
	}

	// Endpoint is the ingestion/flags host. We do not set PersonalApiKey here:
	// EvaluateFlags works against the flags endpoint with just the project token.
	client, err := posthog.NewWithConfig(projectToken, posthog.Config{
		Endpoint: host,
	})
	if err != nil {
		// NewWithConfig only errors on an invalid interval/config, not on a bad
		// token, so this is a genuine programmer error — fail fast.
		log.Fatalf("failed to create PostHog client: %v", err)
	}

	return client
}

```

---

