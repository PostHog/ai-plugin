# PostHog php Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/php

---

## README.md

# PostHog PHP Example - CLI Todo App

A simple command-line todo application built with plain PHP (no framework) demonstrating PostHog integration for CLIs, scripts, data pipelines, and non-web PHP applications.

## Purpose

This example serves as:
- **Verification** that the context-mill wizard works for plain PHP projects
- **Reference implementation** of PostHog best practices for non-framework PHP code
- **Working example** you can run and modify

## Features Demonstrated

- **SDK initialization** - Uses `PostHog::init(...)` once with environment-based configuration
- **Event tracking** - Captures user actions with `distinctId` and properties
- **User identification** - Associates properties with users via `PostHog::identify(...)`
- **Error tracking** - Enables automatic PHP error tracking and manually captures handled exceptions
- **Proper flushing** - Calls `PostHog::flush()` before CLI exit

## Quick Start

### 1. Install Dependencies

```bash
composer install
```

### 2. Configure PostHog

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your PostHog API key
# POSTHOG_API_KEY=phc_your_api_key_here
# POSTHOG_HOST=https://us.i.posthog.com
```

### 3. Run the App

```bash
# Add a todo
php todo.php add "Buy groceries"

# List all todos
php todo.php list

# Complete a todo
php todo.php complete 1

# Delete a todo
php todo.php delete 1

# Show statistics
php todo.php stats
```

## What Gets Tracked

The app tracks these events in PostHog:

| Event | Properties | Purpose |
|-------|-----------|---------|
| `todo_added` | `todo_id`, `todo_length`, `total_todos` | When user adds a new todo |
| `todos_viewed` | `total_todos`, `completed_todos` | When user lists todos |
| `todo_completed` | `todo_id`, `time_to_complete_hours` | When user completes a todo |
| `todo_deleted` | `todo_id`, `was_completed` | When user deletes a todo |
| `stats_viewed` | `total_todos`, `completed_todos`, `pending_todos` | When user views stats |
| `$exception` | exception details and command context | When handled errors occur |

## Code Structure

```
basics/php/
├── todo.php             # Main CLI application
├── composer.json        # PHP dependencies
├── .env.example         # Environment variable template
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Key Implementation Patterns

### 1. Initialize Once

```php
PostHog::init($apiKey, [
    'host' => $host,
    'error_tracking' => [
        'enabled' => true,
    ],
]);
```

### 2. Event Tracking Pattern

```php
PostHog::capture([
    'distinctId' => 'user_123',
    'event' => 'event_name',
    'properties' => ['key' => 'value'],
]);
```

### 3. Identifying Users

```php
PostHog::identify([
    'distinctId' => 'user_123',
    'properties' => ['app_language' => 'php'],
]);
```

### 4. Exception Tracking

```php
try {
    riskyOperation();
} catch (Throwable $e) {
    PostHog::captureException($e, 'user_123', [
        'command' => 'example_command',
    ]);
}
```

### 5. Flush Before CLI Exit

```php
PostHog::flush();
```

## Running Without PostHog

The app works fine without PostHog configured - it simply won't track analytics. You'll see a warning message but the app continues to function normally.

## Next Steps

- Modify `todo.php` to experiment with PostHog tracking
- Add new commands and track their usage
- Explore feature flags: `PostHog::isFeatureEnabled('flag-name', 'user_id')`
- Check your PostHog dashboard to see tracked events

## Learn More

- [PostHog PHP SDK Documentation](https://posthog.com/docs/libraries/php)
- [PostHog PHP Error Tracking](https://posthog.com/docs/error-tracking/installation/php)
- [PostHog Product Analytics PHP installation](https://posthog.com/docs/product-analytics/installation/php)

---

## .env.example

```example
# PostHog configuration
POSTHOG_API_KEY=phc_your_api_key_here
POSTHOG_HOST=https://us.i.posthog.com

```

---

## todo.php

```php
<?php

declare(strict_types=1);

// Simple CLI Todo App with PostHog Analytics
//
// A minimal plain PHP CLI application demonstrating PostHog integration
// for non-framework PHP projects (CLIs, scripts, data pipelines, etc.).

require __DIR__ . '/vendor/autoload.php';

use PostHog\PostHog;

const DATA_FILE = '.todo_app_php.json';

function loadEnvFile(string $path): void
{
    if (!file_exists($path)) {
        return;
    }

    foreach (file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) ?: [] as $line) {
        $line = trim($line);
        if ($line === '' || str_starts_with($line, '#') || !str_contains($line, '=')) {
            continue;
        }

        [$key, $value] = explode('=', $line, 2);
        $key = trim($key);
        $value = trim($value, " \t\n\r\0\x0B\"'");

        if ($key !== '' && getenv($key) === false) {
            putenv($key . '=' . $value);
            $_ENV[$key] = $value;
        }
    }
}

function dataFilePath(): string
{
    $home = getenv('HOME') ?: sys_get_temp_dir();
    return rtrim($home, DIRECTORY_SEPARATOR) . DIRECTORY_SEPARATOR . DATA_FILE;
}

function initializePostHog(): bool
{
    loadEnvFile(__DIR__ . '/.env');

    $apiKey = getenv('POSTHOG_API_KEY');
    if (!$apiKey || str_starts_with($apiKey, 'phc_your_')) {
        echo "WARNING: PostHog not configured (POSTHOG_API_KEY not set)\n";
        echo "         App will work but analytics won't be tracked\n";
        return false;
    }

    PostHog::init($apiKey, [
        'host' => getenv('POSTHOG_HOST') ?: 'https://us.i.posthog.com',
        'error_tracking' => [
            'enabled' => true,
            'context_provider' => static function (array $payload): array {
                return [
                    'distinctId' => getUserId(),
                    'properties' => [
                        'app' => 'php_todo_cli',
                        'runtime' => PHP_VERSION,
                        '$exception_source' => $payload['source'] ?? null,
                    ],
                ];
            },
        ],
    ]);

    return true;
}

function getUserId(): string
{
    $path = dataFilePath();
    if (file_exists($path)) {
        $data = json_decode((string) file_get_contents($path), true);
        if (is_array($data) && isset($data['user_id'])) {
            return (string) $data['user_id'];
        }
    }

    return 'user_' . bin2hex(random_bytes(4));
}

function loadTodos(): array
{
    $path = dataFilePath();
    if (!file_exists($path)) {
        return ['user_id' => getUserId(), 'todos' => []];
    }

    $data = json_decode((string) file_get_contents($path), true);
    if (!is_array($data)) {
        return ['user_id' => getUserId(), 'todos' => []];
    }

    $data['todos'] = $data['todos'] ?? [];
    $data['user_id'] = $data['user_id'] ?? getUserId();
    return $data;
}

function saveTodos(array $data): void
{
    file_put_contents(dataFilePath(), json_encode($data, JSON_PRETTY_PRINT) . PHP_EOL);
}

function identifyUser(bool $posthogEnabled): void
{
    if (!$posthogEnabled) {
        return;
    }

    PostHog::identify([
        'distinctId' => getUserId(),
        'properties' => [
            'app_language' => 'php',
            'app_type' => 'cli',
        ],
    ]);
}

function trackEvent(bool $posthogEnabled, string $eventName, array $properties = []): void
{
    if (!$posthogEnabled) {
        return;
    }

    PostHog::capture([
        'distinctId' => getUserId(),
        'event' => $eventName,
        'properties' => $properties,
    ]);
}

function cmdAdd(string $text, bool $posthogEnabled): void
{
    $data = loadTodos();

    $todo = [
        'id' => count($data['todos']) + 1,
        'text' => $text,
        'completed' => false,
        'created_at' => date(DATE_ATOM),
    ];

    $data['todos'][] = $todo;
    saveTodos($data);

    echo "Added todo #{$todo['id']}: {$todo['text']}\n";

    trackEvent($posthogEnabled, 'todo_added', [
        'todo_id' => $todo['id'],
        'todo_length' => strlen($todo['text']),
        'total_todos' => count($data['todos']),
    ]);
}

function cmdList(bool $posthogEnabled): void
{
    $data = loadTodos();

    if (count($data['todos']) === 0) {
        echo "No todos yet! Add one with: php todo.php add 'Your task'\n";
        return;
    }

    echo "\nYour Todos (" . count($data['todos']) . " total):\n\n";

    foreach ($data['todos'] as $todo) {
        $status = $todo['completed'] ? 'X' : ' ';
        echo "  [{$status}] #{$todo['id']}: {$todo['text']}\n";
    }

    echo "\n";

    trackEvent($posthogEnabled, 'todos_viewed', [
        'total_todos' => count($data['todos']),
        'completed_todos' => count(array_filter($data['todos'], static fn (array $todo): bool => (bool) $todo['completed'])),
    ]);
}

function cmdComplete(int $id, bool $posthogEnabled): void
{
    $data = loadTodos();

    foreach ($data['todos'] as &$todo) {
        if ((int) $todo['id'] !== $id) {
            continue;
        }

        if ($todo['completed']) {
            echo "Todo #{$id} is already completed\n";
            return;
        }

        $todo['completed'] = true;
        $todo['completed_at'] = date(DATE_ATOM);
        saveTodos($data);

        echo "Completed todo #{$todo['id']}: {$todo['text']}\n";

        $timeToComplete = (strtotime($todo['completed_at']) - strtotime($todo['created_at'])) / 3600;
        trackEvent($posthogEnabled, 'todo_completed', [
            'todo_id' => $todo['id'],
            'time_to_complete_hours' => $timeToComplete,
        ]);
        return;
    }

    echo "ERROR: Todo #{$id} not found\n";
}

function cmdDelete(int $id, bool $posthogEnabled): void
{
    $data = loadTodos();

    foreach ($data['todos'] as $index => $todo) {
        if ((int) $todo['id'] !== $id) {
            continue;
        }

        unset($data['todos'][$index]);
        $data['todos'] = array_values($data['todos']);
        saveTodos($data);

        echo "Deleted todo #{$id}\n";

        trackEvent($posthogEnabled, 'todo_deleted', [
            'todo_id' => $todo['id'],
            'was_completed' => $todo['completed'],
        ]);
        return;
    }

    echo "ERROR: Todo #{$id} not found\n";
}

function cmdStats(bool $posthogEnabled): void
{
    $data = loadTodos();

    $total = count($data['todos']);
    $completed = count(array_filter($data['todos'], static fn (array $todo): bool => (bool) $todo['completed']));
    $pending = $total - $completed;
    $rate = $total > 0 ? number_format($completed / $total * 100, 1) : '0.0';

    echo "\nStats:\n\n";
    echo "  Total todos:     {$total}\n";
    echo "  Completed:       {$completed}\n";
    echo "  Pending:         {$pending}\n";
    echo "  Completion rate: {$rate}%\n\n";

    trackEvent($posthogEnabled, 'stats_viewed', [
        'total_todos' => $total,
        'completed_todos' => $completed,
        'pending_todos' => $pending,
    ]);
}

function printUsage(): void
{
    echo <<<USAGE
Simple todo app with PostHog analytics

Usage:
  php todo.php add "Todo text"    Add a new todo
  php todo.php list               List all todos
  php todo.php complete <id>      Mark todo as completed
  php todo.php delete <id>        Delete a todo
  php todo.php stats              Show statistics
USAGE;
}

$posthogEnabled = false;

try {
    $posthogEnabled = initializePostHog();
    identifyUser($posthogEnabled);

    $command = $argv[1] ?? null;
    if (!$command) {
        printUsage();
        exit(0);
    }

    switch ($command) {
        case 'add':
            $text = $argv[2] ?? null;
            if (!$text) {
                echo "ERROR: Please provide todo text\n";
                echo "Usage: php todo.php add \"Your task\"\n";
                exit(1);
            }
            cmdAdd($text, $posthogEnabled);
            break;

        case 'list':
            cmdList($posthogEnabled);
            break;

        case 'complete':
            $id = (int) ($argv[2] ?? 0);
            if ($id <= 0) {
                echo "ERROR: Please provide a valid todo ID\n";
                echo "Usage: php todo.php complete <id>\n";
                exit(1);
            }
            cmdComplete($id, $posthogEnabled);
            break;

        case 'delete':
            $id = (int) ($argv[2] ?? 0);
            if ($id <= 0) {
                echo "ERROR: Please provide a valid todo ID\n";
                echo "Usage: php todo.php delete <id>\n";
                exit(1);
            }
            cmdDelete($id, $posthogEnabled);
            break;

        case 'stats':
            cmdStats($posthogEnabled);
            break;

        default:
            echo "ERROR: Unknown command '{$command}'\n";
            printUsage();
            exit(1);
    }
} catch (Throwable $e) {
    echo "ERROR: {$e->getMessage()}\n";

    if ($posthogEnabled) {
        PostHog::captureException($e, getUserId(), [
            'command' => $argv[1] ?? null,
            'app' => 'php_todo_cli',
        ]);
    }

    exit(1);
} finally {
    if ($posthogEnabled) {
        PostHog::flush();
    }
}

```

---

