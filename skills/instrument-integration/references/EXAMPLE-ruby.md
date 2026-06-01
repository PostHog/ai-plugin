# PostHog ruby Example Project

Repository: https://github.com/PostHog/context-mill
Path: basics/ruby

---

## README.md

# PostHog Ruby Example - CLI Todo App

A simple command-line todo application built with plain Ruby (no frameworks) demonstrating PostHog integration for CLIs, scripts, data pipelines, and non-web Ruby applications.

## Purpose

This example serves as:
- **Verification** that the context-mill wizard works for plain Ruby projects
- **Reference implementation** of PostHog best practices for non-framework Ruby code
- **Working example** you can run and modify

## Features Demonstrated

- **Instance-based API** - Uses `PostHog::Client.new(...)` for explicit client management
- **Proper shutdown** - Uses `shutdown` in `ensure` block to flush events before exit
- **Event tracking** - Captures user actions with `distinct_id` and properties
- **User identification** - Associates properties with users via `identify`
- **Error handling** - Manual exception capture for handled errors

## Quick Start

### 1. Install Dependencies

```bash
# Install bundler if needed
gem install bundler

# Install dependencies
bundle install
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
ruby todo.rb add "Buy groceries"

# List all todos
ruby todo.rb list

# Complete a todo
ruby todo.rb complete 1

# Delete a todo
ruby todo.rb delete 1

# Show statistics
ruby todo.rb stats
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
basics/ruby/
├── todo.rb              # Main CLI application
├── Gemfile              # Ruby dependencies
├── .env.example         # Environment variable template
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Key Implementation Patterns

### 1. Instance-Based Initialization

```ruby
require 'posthog-ruby'

posthog = PostHog::Client.new(
  api_key: api_key,
  host: 'https://us.i.posthog.com',
  on_error: proc { |status, msg| puts "PostHog error: #{status} - #{msg}" }
)
```

### 2. Event Tracking Pattern

```ruby
# Track events with distinct_id
posthog.capture(
  distinct_id: 'user_123',
  event: 'event_name',
  properties: { key: 'value' }
)
```

### 3. Proper Shutdown

```ruby
begin
  # Your application code
ensure
  # Always call shutdown to flush events and close connections
  posthog&.shutdown
end
```

### 4. Identifying Users

```ruby
# Identify users (optional - adds user properties)
posthog.identify(
  distinct_id: 'user_123',
  properties: { email: 'user@example.com', plan: 'pro' }
)
```

## Running Without PostHog

The app works fine without PostHog configured - it simply won't track analytics. You'll see a warning message but the app continues to function normally.

## Next Steps

- Modify `todo.rb` to experiment with PostHog tracking
- Add new commands and track their usage
- Explore feature flags: `posthog.is_feature_enabled('flag-name', 'user_id')`
- Check your PostHog dashboard to see tracked events

## Learn More

- [PostHog Ruby SDK Documentation](https://posthog.com/docs/libraries/ruby)
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

## Gemfile

```
source 'https://rubygems.org'

gem 'posthog-ruby', '~> 3.3'
gem 'dotenv', '~> 3.0'

```

---

## todo.rb

```rb
#!/usr/bin/env ruby
# frozen_string_literal: true

# Simple CLI Todo App with PostHog Analytics
#
# A minimal plain Ruby CLI application demonstrating PostHog integration
# for non-framework Ruby projects (CLIs, scripts, data pipelines, etc.).

require 'json'
require 'securerandom'
require 'time'
require 'dotenv/load'
require 'posthog'

# Data file location
DATA_FILE = File.join(Dir.home, '.todo_app.json')

def initialize_posthog
  # Initialize PostHog with instance-based API.
  # Returns PostHog client or nil if project token not configured.
  project_token = ENV['POSTHOG_PROJECT_TOKEN']

  unless project_token
    puts 'WARNING: PostHog not configured (POSTHOG_PROJECT_TOKEN not set)'
    puts '         App will work but analytics won\'t be tracked'
    return nil
  end

  PostHog::Client.new(
    api_key: project_token,
    host: ENV.fetch('POSTHOG_HOST', 'https://us.i.posthog.com'),
    on_error: proc { |status, msg| puts "PostHog error: #{status} - #{msg}" }
  )
end

def get_user_id
  # Get or create a user ID for this installation.
  # Uses a UUID stored in the data file to represent this user.
  if File.exist?(DATA_FILE)
    data = JSON.parse(File.read(DATA_FILE))
    return data['user_id'] if data['user_id']
  end

  "user_#{SecureRandom.hex(4)}"
end

def load_todos
  # Load todos from disk.
  return { 'user_id' => get_user_id, 'todos' => [] } unless File.exist?(DATA_FILE)

  JSON.parse(File.read(DATA_FILE))
end

def save_todos(data)
  # Save todos to disk.
  File.write(DATA_FILE, JSON.pretty_generate(data))
end

def track_event(posthog, event_name, properties = {})
  # Track an event with PostHog.
  return unless posthog

  posthog.capture(
    distinct_id: get_user_id,
    event: event_name,
    properties: properties
  )
end

def cmd_add(text, posthog)
  # Add a new todo item.
  data = load_todos

  todo = {
    'id' => data['todos'].length + 1,
    'text' => text,
    'completed' => false,
    'created_at' => Time.now.iso8601
  }

  data['todos'] << todo
  save_todos(data)

  puts "Added todo ##{todo['id']}: #{todo['text']}"

  track_event(posthog, 'todo_added', {
    'todo_id' => todo['id'],
    'todo_length' => todo['text'].length,
    'total_todos' => data['todos'].length
  })
end

def cmd_list(posthog)
  # List all todos.
  data = load_todos

  if data['todos'].empty?
    puts "No todos yet! Add one with: ruby todo.rb add 'Your task'"
    return
  end

  puts "\nYour Todos (#{data['todos'].length} total):\n\n"

  data['todos'].each do |todo|
    status = todo['completed'] ? 'X' : ' '
    puts "  [#{status}] ##{todo['id']}: #{todo['text']}"
  end

  puts

  track_event(posthog, 'todos_viewed', {
    'total_todos' => data['todos'].length,
    'completed_todos' => data['todos'].count { |t| t['completed'] }
  })
end

def cmd_complete(id, posthog)
  # Mark a todo as completed.
  data = load_todos

  todo = data['todos'].find { |t| t['id'] == id }

  unless todo
    puts "ERROR: Todo ##{id} not found"
    return
  end

  if todo['completed']
    puts "Todo ##{id} is already completed"
    return
  end

  todo['completed'] = true
  todo['completed_at'] = Time.now.iso8601
  save_todos(data)

  puts "Completed todo ##{todo['id']}: #{todo['text']}"

  time_to_complete = (Time.parse(todo['completed_at']) - Time.parse(todo['created_at'])) / 3600.0

  track_event(posthog, 'todo_completed', {
    'todo_id' => todo['id'],
    'time_to_complete_hours' => time_to_complete
  })
end

def cmd_delete(id, posthog)
  # Delete a todo.
  data = load_todos

  todo = data['todos'].find { |t| t['id'] == id }

  unless todo
    puts "ERROR: Todo ##{id} not found"
    return
  end

  data['todos'].delete(todo)
  save_todos(data)

  puts "Deleted todo ##{id}"

  track_event(posthog, 'todo_deleted', {
    'todo_id' => todo['id'],
    'was_completed' => todo['completed']
  })
end

def cmd_stats(posthog)
  # Show usage statistics.
  data = load_todos

  total = data['todos'].length
  completed = data['todos'].count { |t| t['completed'] }
  pending = total - completed

  puts "\nStats:\n\n"
  puts "  Total todos:     #{total}"
  puts "  Completed:       #{completed}"
  puts "  Pending:         #{pending}"
  puts "  Completion rate: #{total > 0 ? format('%.1f', completed.to_f / total * 100) : '0.0'}%"
  puts

  track_event(posthog, 'stats_viewed', {
    'total_todos' => total,
    'completed_todos' => completed,
    'pending_todos' => pending
  })
end

def print_usage
  puts <<~USAGE
    Simple todo app with PostHog analytics

    Usage:
      ruby todo.rb add "Todo text"    Add a new todo
      ruby todo.rb list               List all todos
      ruby todo.rb complete <id>      Mark todo as completed
      ruby todo.rb delete <id>        Delete a todo
      ruby todo.rb stats              Show statistics
  USAGE
end

# Main entry point
posthog = nil

begin
  posthog = initialize_posthog

  command = ARGV[0]

  unless command
    print_usage
    exit 0
  end

  case command
  when 'add'
    text = ARGV[1]
    unless text
      puts 'ERROR: Please provide todo text'
      puts 'Usage: ruby todo.rb add "Your task"'
      exit 1
    end
    cmd_add(text, posthog)
  when 'list'
    cmd_list(posthog)
  when 'complete'
    id = ARGV[1]&.to_i
    unless id && id > 0
      puts 'ERROR: Please provide a valid todo ID'
      puts 'Usage: ruby todo.rb complete <id>'
      exit 1
    end
    cmd_complete(id, posthog)
  when 'delete'
    id = ARGV[1]&.to_i
    unless id && id > 0
      puts 'ERROR: Please provide a valid todo ID'
      puts 'Usage: ruby todo.rb delete <id>'
      exit 1
    end
    cmd_delete(id, posthog)
  when 'stats'
    cmd_stats(posthog)
  else
    puts "ERROR: Unknown command '#{command}'"
    print_usage
    exit 1
  end
rescue StandardError => e
  puts "ERROR: #{e.message}"

  # Manually capture handled errors
  posthog&.capture_exception(e, get_user_id)

  exit 1
ensure
  # IMPORTANT: Always shutdown PostHog to flush events
  posthog&.shutdown
end

```

---

