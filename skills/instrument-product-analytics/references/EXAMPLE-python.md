# PostHog python Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/python

---

## README.md

# PostHog Python Example - CLI Todo App

A simple command-line todo application built with plain Python (no frameworks) demonstrating PostHog integration for CLIs, scripts, data pipelines, and non-web Python applications.

## Purpose

This example serves as:
- **Verification** that the context-mill wizard works for plain Python projects
- **Reference implementation** of PostHog best practices for non-framework Python code
- **Working example** you can run and modify

## Features Demonstrated

- **Instance-based API** - Uses `Posthog(...)` class instead of module-level API
- **Exception autocapture** - Automatic tracking of unhandled exceptions
- **Proper shutdown** - Uses `shutdown()` to flush events before exit
- **Event tracking** - Captures user actions with `distinct_id` and properties
- **User identification** - Sets properties on users via `identify()`, and updates them later with `set()` and `setOnce()`
- **Error handling** - Manual exception capture for handled errors

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure PostHog

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your PostHog project token
# POSTHOG_PROJECT_TOKEN=phc_your_project_token_here
# POSTHOG_HOST=https://us.i.posthog.com
```

### 3. Run the App

```bash
# Add a todo
python todo.py add "Buy groceries"

# List all todos
python todo.py list

# Complete a todo
python todo.py complete 1

# Delete a todo
python todo.py delete 1

# Show statistics
python todo.py stats
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

## Code Structure

```
basics/python/
├── todo.py              # Main CLI application
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variable template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Key Implementation Patterns

### 1. Instance-Based Initialization

```python
from posthog import Posthog

posthog = Posthog(
    api_key,
    host='https://us.i.posthog.com',
    enable_exception_autocapture=True  # Automatically capture exceptions
)
```

### 2. Event Tracking Pattern

```python
# Track events with distinct_id
posthog_client.capture(
    distinct_id="user_123",
    event="event_name",
    properties={"key": "value"}
)
```

### 3. Proper Shutdown

```python
try:
    # Your application code
    pass
finally:
    # Always call shutdown() to flush events and close connections
    posthog.shutdown()
```

### 4. Identifying Users

```python
# Set person properties on a user profile
posthog_client.set(
    distinct_id="user_123",
    properties={"email": "user@example.com", "plan": "pro"}
)
```

### 5. Exception Handling

```python
try:
    # Code that might fail
    risky_operation()
except Exception as e:
    # Manually capture handled errors you want to track
    posthog_client.capture_exception(e, distinct_id="user_123")
```

## Running Without PostHog

The app works fine without PostHog configured - it simply won't track analytics. You'll see a warning message but the app continues to function normally.

## Next Steps

- Modify `todo.py` to experiment with PostHog tracking
- Add new commands and track their usage
- Explore feature flags: `posthog.feature_enabled('flag-name', user_id)`
- Check your PostHog dashboard to see tracked events

## Learn More

- [PostHog Python SDK Documentation](https://posthog.com/docs/libraries/python)
- [PostHog Python SDK API Reference](https://posthog.com/docs/references/posthog-python)
- [PostHog Product Analytics](https://posthog.com/docs/product-analytics)

---

## .env.example

```example
# PostHog Configuration
POSTHOG_PROJECT_TOKEN=phc_your_project_token_here
POSTHOG_HOST=https://us.i.posthog.com

# Optional: Enable debug mode to see PostHog requests
# POSTHOG_DEBUG=true

```

---

## requirements.txt

```txt
posthog>=3.0.0
python-dotenv>=1.0.0

```

---

## todo.py

```py
#!/usr/bin/env python3
"""Simple CLI Todo App with PostHog Analytics

A minimal plain Python CLI application demonstrating PostHog integration
for non-framework Python projects (CLIs, scripts, data pipelines, etc.).
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from posthog import Posthog

# Load environment variables
load_dotenv()

# Data file location
DATA_FILE = Path.home() / ".todo_app.json"


def initialize_posthog():
    """Initialize PostHog with instance-based API.

    Returns PostHog instance or None if project token not configured.
    """
    project_token = os.getenv('POSTHOG_PROJECT_TOKEN')

    if not project_token:
        print("WARNING: PostHog not configured (POSTHOG_PROJECT_TOKEN not set)")
        print("         App will work but analytics won't be tracked")
        return None

    # Create PostHog instance with opinionated defaults
    posthog = Posthog(
        project_token,
        host=os.getenv('POSTHOG_HOST', 'https://us.i.posthog.com'),
        debug=os.getenv('POSTHOG_DEBUG', 'False').lower() == 'true',
        enable_exception_autocapture=True  # Auto-capture unhandled exceptions
    )

    return posthog


def get_user_id():
    """Get or create a user ID for this installation.

    Uses a UUID stored in the data file to represent this user.
    In a real app, this would be your actual user ID.
    """
    import uuid

    if DATA_FILE.exists():
        data = json.loads(DATA_FILE.read_text())
        if 'user_id' in data:
            return data['user_id']

    # Create new user ID
    return f"user_{uuid.uuid4().hex[:8]}"


def load_todos():
    """Load todos from disk."""
    if not DATA_FILE.exists():
        return {"user_id": get_user_id(), "todos": []}

    return json.loads(DATA_FILE.read_text())


def save_todos(data):
    """Save todos to disk."""
    DATA_FILE.write_text(json.dumps(data, indent=2))


def track_event(posthog, event_name, properties=None):
    """Track an event with PostHog.

    Uses the real PostHog Python SDK API.
    """
    if not posthog:
        return

    posthog.capture(
        distinct_id=get_user_id(),
        event=event_name,
        properties=properties or {}
    )


def cmd_add(args, posthog):
    """Add a new todo item."""
    data = load_todos()

    todo = {
        "id": len(data["todos"]) + 1,
        "text": args.text,
        "completed": False,
        "created_at": datetime.now().isoformat()
    }

    data["todos"].append(todo)
    save_todos(data)

    print(f"Added todo #{todo['id']}: {todo['text']}")

    # Track the event
    track_event(posthog, "todo_added", {
        "todo_id": todo["id"],
        "todo_length": len(todo["text"]),
        "total_todos": len(data["todos"])
    })


def cmd_list(args, posthog):
    """List all todos."""
    data = load_todos()

    if not data["todos"]:
        print("No todos yet! Add one with: todo add 'Your task'")
        return

    print(f"\nYour Todos ({len(data['todos'])} total):\n")

    for todo in data["todos"]:
        status = "X" if todo["completed"] else " "
        print(f"  [{status}] #{todo['id']}: {todo['text']}")

    print()

    # Track the event
    track_event(posthog, "todos_viewed", {
        "total_todos": len(data["todos"]),
        "completed_todos": sum(1 for t in data["todos"] if t["completed"])
    })


def cmd_complete(args, posthog):
    """Mark a todo as completed."""
    data = load_todos()

    todo = next((t for t in data["todos"] if t["id"] == args.id), None)

    if not todo:
        print(f"ERROR: Todo #{args.id} not found")
        return

    if todo["completed"]:
        print(f"Todo #{args.id} is already completed")
        return

    todo["completed"] = True
    todo["completed_at"] = datetime.now().isoformat()
    save_todos(data)

    print(f"Completed todo #{todo['id']}: {todo['text']}")

    # Track the event
    track_event(posthog, "todo_completed", {
        "todo_id": todo["id"],
        "time_to_complete_hours": (
            datetime.fromisoformat(todo["completed_at"]) -
            datetime.fromisoformat(todo["created_at"])
        ).total_seconds() / 3600
    })


def cmd_delete(args, posthog):
    """Delete a todo."""
    data = load_todos()

    todo = next((t for t in data["todos"] if t["id"] == args.id), None)

    if not todo:
        print(f"ERROR: Todo #{args.id} not found")
        return

    data["todos"].remove(todo)
    save_todos(data)

    print(f"Deleted todo #{args.id}")

    # Track the event
    track_event(posthog, "todo_deleted", {
        "todo_id": todo["id"],
        "was_completed": todo["completed"]
    })


def cmd_stats(args, posthog):
    """Show usage statistics."""
    data = load_todos()

    total = len(data["todos"])
    completed = sum(1 for t in data["todos"] if t["completed"])
    pending = total - completed

    print(f"\nStats:\n")
    print(f"  Total todos:     {total}")
    print(f"  Completed:       {completed}")
    print(f"  Pending:         {pending}")
    print(f"  Completion rate: {(completed/total*100) if total > 0 else 0:.1f}%")
    print()

    # Track the event
    track_event(posthog, "stats_viewed", {
        "total_todos": total,
        "completed_todos": completed,
        "pending_todos": pending
    })


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Simple todo app with PostHog analytics"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new todo")
    add_parser.add_argument("text", help="Todo text")

    # List command
    subparsers.add_parser("list", help="List all todos")

    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Mark todo as completed")
    complete_parser.add_argument("id", type=int, help="Todo ID")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a todo")
    delete_parser.add_argument("id", type=int, help="Todo ID")

    # Stats command
    subparsers.add_parser("stats", help="Show statistics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize PostHog
    posthog = initialize_posthog()

    try:
        # Route to appropriate command
        if args.command == "add":
            cmd_add(args, posthog)
        elif args.command == "list":
            cmd_list(args, posthog)
        elif args.command == "complete":
            cmd_complete(args, posthog)
        elif args.command == "delete":
            cmd_delete(args, posthog)
        elif args.command == "stats":
            cmd_stats(args, posthog)

    except Exception as e:
        print(f"ERROR: {e}")

        # Manually capture handled errors
        if posthog:
            posthog.capture_exception(e, get_user_id())

        sys.exit(1)

    finally:
        # IMPORTANT: Always shutdown PostHog to flush events
        if posthog:
            posthog.shutdown()


if __name__ == "__main__":
    main()

```

---

