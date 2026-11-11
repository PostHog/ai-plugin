# PostHog wordpress Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/wordpress

---

## README.md

# PostHog WordPress Example

A minimal WordPress plugin demonstrating PostHog integration for self-hosted WordPress sites: client-side autocapture plus one server-side capture call via the PHP SDK.

## Purpose

This example serves as:
- **Verification** that the context-mill wizard works for self-hosted WordPress projects
- **Reference implementation** of PostHog best practices for WordPress plugin code
- **Working example** you can drop into a real WordPress install and modify

## Why a plugin, not `functions.php`

The existing PostHog WordPress docs teach editing a theme's `functions.php` for the client snippet, which is theme-coupled and has no path to server-side capture. This example uses a small standalone plugin instead — the same approach a real integration on self-hosted WordPress (VIP, WP Engine, Pantheon, or any host with file access) would take.

## Features Demonstrated

- **Client-side autocapture** — the same `wp_head` JS-snippet pattern as the PostHog WordPress docs, sourced from a `wp-config.php` constant instead of hardcoded
- **One server-side event** — captures a real WordPress action (`comment_post`) with `PostHog::capture(...)`, then flushes immediately since a PHP-FPM/mod_php request has no single explicit exit point
- **Error tracking** — enabled in `PostHog::init(...)` so unhandled PHP errors reach PostHog

## Quick Start

```bash
cd posthog-example
composer install
```

Add your PostHog project token to the site's `wp-config.php` — the same file that holds `DB_PASSWORD`:

```php
define('POSTHOG_PROJECT_TOKEN', 'phc_your_project_token_here');
define('POSTHOG_HOST', 'https://us.i.posthog.com'); // optional, this is the default
```

Then drop `posthog-example/` into the install's `wp-content/plugins/` directory and activate it.

## What Gets Tracked

| Event | Trigger | Properties |
|-------|---------|------------|
| `$pageview` (autocapture) | Any page load | Standard PostHog JS autocapture |
| `comment_posted` | `comment_post` action | `comment_id`, `post_id`, `comment_approved` |
| `$exception` | Unhandled PHP errors | Exception details from the PHP SDK |

## Code Structure

```
example-apps/wordpress/
├── README.md                       # This file
└── posthog-example/                # The plugin — copy this into wp-content/plugins/
    ├── posthog-example.php         # Plugin entry: init, client snippet, server capture
    ├── composer.json               # Pulls in posthog/posthog-php
    └── .gitignore                  # Ignores vendor/, composer.lock
```

## Key Implementation Patterns

### 1. Guard the entry file

```php
if (!defined('ABSPATH')) {
    exit;
}
```

Every plugin file must refuse to run outside WordPress.

### 2. Initialize once, on `plugins_loaded`

```php
PostHog::init($token, [
    'host' => $host,
    'error_tracking' => ['enabled' => true],
]);
add_action('plugins_loaded', 'posthog_example_init');
```

### 3. Config from `wp-config.php`, snippet on `wp_head`, token escaped

```php
$token = esc_js(posthog_example_token()); // reads the POSTHOG_PROJECT_TOKEN constant
add_action('wp_head', 'posthog_example_client_snippet', 999);
```

The token lives in `wp-config.php`, never in plugin source. Never echo a raw token into markup. Priority 999 keeps the snippet late in `<head>`.

### 4. Server-side capture on a real WordPress action

```php
PostHog::capture([
    'distinctId' => (string) $distinct_id,
    'event' => 'comment_posted',
    'properties' => ['comment_id' => $comment_id],
]);
```

Use the client SDK for pageviews. Reserve the PHP SDK for actions that only exist server-side (`comment_post`, `woocommerce_thankyou`, `user_register`).

### 5. Flush after capture

```php
PostHog::flush();
```

A web request has no single exit point like a CLI script does, so flush where you capture.

## Reverse proxy

Ad blockers often drop browser requests sent to PostHog's own domain, so the client-side snippet loses events. Point `POSTHOG_HOST` at a reverse proxy to keep them. The quickest option is PostHog's [managed reverse proxy](https://posthog.com/docs/advanced/proxy/managed-reverse-proxy.md). You can also proxy through your host or CDN, such as [Cloudflare](https://posthog.com/docs/advanced/proxy/cloudflare.md) or [nginx](https://posthog.com/docs/advanced/proxy/nginx.md). Server-side calls from PHP aren't affected by ad blockers and don't need the proxy.

## Running Without PostHog

The plugin works fine without PostHog configured. If the `POSTHOG_PROJECT_TOKEN` constant is undefined — or still holds the `phc_your_...` placeholder — the plugin skips initialization, prints no snippet, and captures nothing. WordPress is unaffected.

## Next Steps

- Track another WordPress action: `user_register`, `publish_post`, or `woocommerce_thankyou`
- Identify logged-in users with `PostHog::identify(...)` instead of the hashed anonymous id
- Move the token to a WordPress option with a settings screen if the plugin should be configurable from wp-admin
- Add feature flags — evaluate them client-side if the site sits behind full-page caching

## Learn More

- [PostHog WordPress docs](https://posthog.com/docs/libraries/wordpress)
- [PostHog PHP SDK docs](https://posthog.com/docs/libraries/php)
- [PostHog PHP error tracking](https://posthog.com/docs/error-tracking/installation/php)

---

## posthog-example/posthog-example.php

```php
<?php
/**
 * Plugin Name: PostHog Example
 * Description: Minimal WordPress plugin demonstrating client-side autocapture plus one server-side PostHog PHP SDK capture.
 * Version: 0.1.0
 * License: MIT
 */

declare(strict_types=1);

if (!defined('ABSPATH')) {
    exit;
}

require __DIR__ . '/vendor/autoload.php';

use PostHog\PostHog;

/**
 * Configuration comes from wp-config.php constants — the same file that
 * already holds DB_PASSWORD and the auth salts:
 *
 *     define('POSTHOG_PROJECT_TOKEN', 'phc_...');
 *     define('POSTHOG_HOST', 'https://us.i.posthog.com'); // optional
 *
 * A distributable plugin would offer a settings screen backed by
 * get_option() instead.
 */
function posthog_example_token(): string
{
    return defined('POSTHOG_PROJECT_TOKEN') ? (string) POSTHOG_PROJECT_TOKEN : '';
}

function posthog_example_host(): string
{
    return defined('POSTHOG_HOST') ? (string) POSTHOG_HOST : 'https://us.i.posthog.com';
}

function posthog_example_configured(): bool
{
    $token = posthog_example_token();
    return $token !== '' && !str_starts_with($token, 'phc_your_');
}

function posthog_example_init(): void
{
    if (!posthog_example_configured()) {
        return;
    }

    PostHog::init(posthog_example_token(), [
        'host' => posthog_example_host(),
        'error_tracking' => [
            'enabled' => true,
        ],
    ]);
}
add_action('plugins_loaded', 'posthog_example_init');

/**
 * Client-side autocapture. Same pattern as the PostHog WordPress docs
 * (https://posthog.com/docs/libraries/wordpress) — inject the JS snippet
 * on wp_head at priority 999, but sourced from the wp-config.php constants
 * above instead of hardcoded in plugin source.
 */
function posthog_example_client_snippet(): void
{
    if (!posthog_example_configured()) {
        return;
    }

    $token = esc_js(posthog_example_token());
    $host = esc_js(posthog_example_host());
    ?>
    <script>
      // POSTHOG_BROWSER_SNIPPET_START
      !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],Object.defineProperty(u,"toString",{configurable:!0,enumerable:!0,writable:!0,value:function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e}}),Object.defineProperty(u.people,"toString",{configurable:!0,enumerable:!0,writable:!0,value:function(){return u.toString(1)+".people (stub)"}}),o="init capture register register_once register_for_session unregister unregister_for_session getFeatureFlag getFeatureFlagResult isFeatureEnabled reloadFeatureFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey getNextSurveyStep identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset get_distinct_id getGroups get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording sessionRecordingStarted captureException loadToolbar get_property getSessionProperty createPersonProfile opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing clear_opt_in_out_capturing debug".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
      // POSTHOG_BROWSER_SNIPPET_END
      posthog.init('<?php echo $token; ?>',{api_host:'<?php echo $host; ?>',defaults:'2026-08-30'})
    </script>
    <?php
}
add_action('wp_head', 'posthog_example_client_snippet', 999);

/**
 * One server-side event: capture a real WordPress action (a new comment)
 * with PostHog::capture(...), then flush immediately since a PHP-FPM /
 * mod_php request has no single explicit exit point to hook otherwise.
 */
function posthog_example_track_comment(int $comment_id, $comment_approved, array $comment_data): void
{
    if (!posthog_example_configured()) {
        return;
    }

    $distinct_id = $comment_data['user_id'] ?? 'anon_' . md5($comment_data['comment_author_email'] ?? (string) $comment_id);

    PostHog::capture([
        'distinctId' => (string) $distinct_id,
        'event' => 'comment_posted',
        'properties' => [
            'comment_id' => $comment_id,
            'post_id' => $comment_data['comment_post_ID'] ?? null,
            'comment_approved' => $comment_approved,
        ],
    ]);

    PostHog::flush();
}
add_action('comment_post', 'posthog_example_track_comment', 10, 3);

```

---

