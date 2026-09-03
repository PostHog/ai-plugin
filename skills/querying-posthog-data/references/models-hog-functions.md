# Hog Functions

## Hog Function (`system.hog_functions`)

Hog functions are programmable event handlers in PostHog's CDP (Customer Data Platform). They process events in real time to send data to external destinations, transform events during ingestion, or run site-side apps.

### Function Types

- `destination` — sends event data to external services (Slack, webhooks, CRMs, etc.)
- `site_destination` — client-side destination running in the browser
- `internal_destination` — PostHog internal processing (e.g. triggering workflows)
- `source_webhook` — receives inbound webhooks and converts them to PostHog events
- `warehouse_source_webhook` — receives webhooks for data warehouse ingestion
- `site_app` — client-side app running in the browser (e.g. surveys, feedback widgets)
- `transformation` — modifies events during ingestion before they reach ClickHouse

### Columns

Column | Type | Nullable | Description
`id` | String | NOT NULL | Function UUID.
`team_id` | Integer | NOT NULL |
`name` | String | NOT NULL | Function name.
`description` | String | NOT NULL | Function description.
`type` | String | NOT NULL | Function type, e.g. 'destination', 'transformation', 'site_app'.
`enabled` | Integer | NOT NULL | 1 if the function is enabled, 0 otherwise.
`deleted` | Integer | NOT NULL | 1 if the function has been deleted, 0 otherwise.
`icon_url` | String | NOT NULL | URL of the function's icon.
`template_id` | String | NOT NULL | Id of the template this function was created from.
`execution_order` | Integer | NOT NULL | Order in which the function runs relative to others of its type.
`inputs_schema` | JSON | NOT NULL | JSON schema describing the function's configurable inputs.
`filters` | JSON | NOT NULL | JSON filters deciding which events the function runs on.
`created_at` | DateTime | NOT NULL | When the function was created.
`updated_at` | DateTime | NOT NULL | When the function was last updated.

### Query Examples

```sql
-- List all enabled destinations
SELECT id, name, template_id, updated_at
FROM system.hog_functions
WHERE type = 'destination' AND enabled = 1 AND deleted = 0
ORDER BY updated_at DESC

-- Count functions by type
SELECT type, count() AS total
FROM system.hog_functions
WHERE deleted = 0
GROUP BY type
ORDER BY total DESC

-- List transformations in execution order
SELECT id, name, execution_order, enabled
FROM system.hog_functions
WHERE type = 'transformation' AND deleted = 0
ORDER BY execution_order ASC

-- Find functions created from a specific template
SELECT id, name, enabled, created_at
FROM system.hog_functions
WHERE template_id = 'template-slack' AND deleted = 0

-- Find functions updated in the last 7 days
SELECT id, name, type, updated_at
FROM system.hog_functions
WHERE updated_at > now() - toIntervalDay(7) AND deleted = 0
ORDER BY updated_at DESC
```
