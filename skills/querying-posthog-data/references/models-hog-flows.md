# Hog Flows

## Hog Flow (`system.hog_flows`)

Hog flows are automated user journeys — multi-step workflows that trigger actions (emails, webhooks, etc.) based on user behavior.

### Columns

Column | Type | Nullable | Description
`id` | String | NOT NULL | Flow UUID.
`team_id` | Integer | NOT NULL |
`name` | String | NOT NULL | Flow name.
`description` | String | NOT NULL | Flow description.
`status` | String | NOT NULL | Flow status, e.g. 'active', 'draft', 'archived'.
`version` | Integer | NOT NULL | Flow version number.
`exit_condition` | String | NOT NULL | Condition that causes a person to exit the flow.
`trigger` | JSON | NOT NULL | JSON definition of what enrolls people into the flow.
`edges` | JSON | NOT NULL | JSON edges connecting actions in the flow graph.
`actions` | JSON | NOT NULL | JSON nodes/actions that make up the flow.
`created_by_id` | Integer | NULL | User who created the flow.
`created_at` | DateTime | NOT NULL | When the flow was created.
`updated_at` | DateTime | NOT NULL | When the flow was last updated.

### Status Values

- `draft` — not yet published, not running
- `active` — published and evaluating users
- `archived` — disabled and hidden from default views

### Exit Condition Values

- `exit_on_conversion` — user exits when they convert (complete the goal)
- `exit_on_trigger_not_matched` — user exits if they no longer match the trigger
- `exit_on_trigger_not_matched_or_conversion` — user exits on either condition
- `exit_only_at_end` — user always completes the full flow

### Query Examples

```sql
-- Count flows by status
SELECT status, count() AS total
FROM system.hog_flows
GROUP BY status
ORDER BY total DESC

-- List active flows with their names
SELECT id, name, version, created_at
FROM system.hog_flows
WHERE status = 'active'
ORDER BY created_at DESC

-- Find flows updated in the last 7 days
SELECT id, name, status, updated_at
FROM system.hog_flows
WHERE updated_at > now() - toIntervalDay(7)
ORDER BY updated_at DESC
```
