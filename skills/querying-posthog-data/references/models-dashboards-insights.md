# Dashboards, Tiles & Insights

## Dashboard (`system.dashboards`)

Dashboards are collections of insights that provide a unified view of analytics data.

### Columns

Column | Type | Nullable | Description
`id` | Integer | NOT NULL | Dashboard id.
`team_id` | Integer | NOT NULL |
`name` | String | NOT NULL | Dashboard name.
`description` | String | NOT NULL | Dashboard description.
`created_by_id` | Integer | NULL | User who created the dashboard.
`created_at` | DateTime | NOT NULL | When the dashboard was created.
`deleted` | Integer | NOT NULL | 1 if the dashboard has been deleted, 0 otherwise.
`filters` | JSON | NOT NULL | JSON dashboard-level filters applied to all tiles.
`variables` | JSON | NOT NULL | JSON dashboard-level template variables.

### Important Notes

- Soft-deleted dashboards are excluded by default; filter with `NOT deleted`
- Use `filters` to store dashboard-level date ranges and property filters

---

## Insight (`system.insights`)

Insights are saved analytics queries that visualize data.

### Columns

Column | Type | Nullable | Description
`id` | Integer | NOT NULL | Insight id.
`short_id` | String | NOT NULL | Short URL-safe id used in insight links.
`team_id` | Integer | NOT NULL |
`name` | String | NOT NULL | Insight name.
`description` | String | NOT NULL | Insight description.
`filters` | JSON | NOT NULL | Legacy JSON filter-based insight definition.
`query` | JSON | NOT NULL | JSON query (HogQL query schema) defining the insight.
`query_metadata` | JSON | NOT NULL | JSON metadata derived from the query.
`deleted` | Integer | NOT NULL | 1 if the insight has been deleted, 0 otherwise.
`saved` | Integer | NOT NULL | 1 if explicitly saved by a user, 0 if a transient/auto-created insight.
`favorited` | Integer | NOT NULL | 1 if the insight is marked as a favorite, 0 otherwise.
`created_at` | DateTime | NOT NULL | When the insight was created.
`created_by_id` | Integer | NULL | User who created the insight.
`last_modified_at` | DateTime | NOT NULL | When the insight definition was last changed.
`last_modified_by_id` | Integer | NULL | User who last modified the insight.
`updated_at` | DateTime | NOT NULL | When the row was last updated (any field).

### Important Notes

- `short_id` is unique per team and used in URLs: `/insights/{short_id}`
- Only saved insights appear in the insights list; filter with `saved`
- Soft-deleted insights are excluded by default; filter with `NOT deleted`
