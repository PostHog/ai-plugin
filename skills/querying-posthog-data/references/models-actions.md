# Actions

## Action (`system.actions`)

Actions are named combinations of events and conditions used for filtering and analysis.

### Columns

Column | Type | Nullable | Description
`id` | Integer | NOT NULL | Action id.
`team_id` | Integer | NOT NULL |
`name` | String | NOT NULL | Action name.
`description` | String | NOT NULL | Action description.
`deleted` | Integer | NOT NULL | 1 if the action has been deleted, 0 otherwise.
`created_by_id` | Integer | NULL | User who created the action.
`created_at` | DateTime | NOT NULL | When the action was created.
`updated_at` | DateTime | NOT NULL | When the action was last updated.
`steps_json` | JSON | NOT NULL | JSON array of match steps (event/selector/url conditions).

### Steps JSON Structure

```json
[
  {
    "id": "uuid",
    "event": "$pageview",
    "url": "https://example.com/pricing",
    "url_matching": "contains",
    "properties": [{ "key": "$current_url", "value": "pricing", "operator": "icontains" }]
  },
  {
    "id": "uuid",
    "event": "button_clicked",
    "selector": "button.cta-primary",
    "text": "Sign Up",
    "text_matching": "exact"
  }
]
```

### Step Matching Options

Field | Description
`event` | Event name to match
`url` | URL pattern to match
`url_matching` | `exact`, `contains`, `regex`
`selector` | CSS selector for element
`text` | Element text to match
`text_matching` | `exact`, `contains`, `regex`
`properties` | Additional property filters

### Key Relationships

- **Surveys**: Actions can be linked to surveys via `system.surveys`

### Important Notes

- Actions can combine multiple event conditions (steps)
- Steps are OR'd together - matching any step triggers the action
- Actions can be used in insights, cohorts, and feature flag targeting

---

## Common Query Patterns

**Find actions by name:**

```sql
SELECT id, name, description, steps_json
FROM system.actions
WHERE name ILIKE '%signup%' AND NOT deleted
```

**Find actions with specific event:**

```sql
SELECT id, name, steps_json
FROM system.actions
WHERE NOT deleted
  AND JSONExtractString(steps_json, 1, 'event') = '$pageview'
```

**Find events matching a specific action:**

By action's name:

```sql
SELECT count()
FROM events
WHERE matchesAction('clicked homepage button')
```

By action's ID:

```sql
SELECT count()
FROM events
WHERE matchesAction(43)
```
