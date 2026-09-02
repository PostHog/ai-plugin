# Annotations

## Annotation (`system.annotations`)

Annotations are timestamped notes used to mark product changes, incidents, or releases directly on charts.

### Columns

Column | Type | Nullable | Description
`id` | Integer | NOT NULL | Annotation id.
`team_id` | Integer | NOT NULL |
`content` | String | NULL | Annotation text.
`scope` | String | NOT NULL | Where the annotation applies: 'project', 'organization', 'dashboard', 'dashboard_item' (insight), or 'recording'.
`creation_type` | String | NOT NULL | How the annotation was created, e.g. user-created vs GitHub.
`date_marker` | DateTime | NULL | The point in time the annotation marks on a chart.
`deleted` | Integer | NOT NULL | 1 if the annotation has been deleted, 0 otherwise.
`dashboard_item_id` | Integer | NULL | Insight this annotation is scoped to; joins to insights.id.
`dashboard_id` | Integer | NULL | Dashboard this annotation is scoped to; joins to dashboards.id.
`created_by_id` | Integer | NULL | User who created the annotation.
`created_at` | DateTime | NULL | When the annotation was created.
`updated_at` | DateTime | NOT NULL | When the annotation was last updated.

### Key Relationships

- **Insights**: `dashboard_item_id` -> `system.insights.id`
- **Dashboards**: `dashboard_id` -> `system.dashboards.id`

### Important Notes

- The API usually hides `deleted=true` rows; SQL queries should filter them explicitly when needed.
- `scope='organization'` annotations can appear across multiple projects in the same organization.

---

## Common Query Patterns

**List recent non-deleted annotations:**

```sql
SELECT id, scope, content, date_marker, created_at
FROM system.annotations
WHERE NOT deleted
ORDER BY date_marker DESC NULLS LAST
LIMIT 100
```

**Find annotations around a release window:**

```sql
SELECT id, content, scope, date_marker
FROM system.annotations
WHERE NOT deleted
  AND date_marker >= toDateTime('2026-03-01 00:00:00')
  AND date_marker < toDateTime('2026-03-08 00:00:00')
ORDER BY date_marker ASC
```

**Get organization-scoped annotations only:**

```sql
SELECT id, content, date_marker, created_by_id
FROM system.annotations
WHERE NOT deleted
  AND scope = 'organization'
ORDER BY date_marker DESC NULLS LAST
```
