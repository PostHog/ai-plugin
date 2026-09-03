# Usage metrics

## GroupUsageMetric (`system.usage_metrics`)

Usage metrics are team-defined numeric measures that render on Customer Analytics profile pages — for example "weekly active users", "events in the last 7 days", or "revenue over the last 30 days". Each metric compiles a HogQL filter expression over the events table, optionally summing a numeric property.

**Not group-specific.** Despite the model name (`GroupUsageMetric`) and the presence of `group_type_index`, metrics are defined at the **team** level and applied to **both groups and persons**. They were originally built for group profiles and later reused for person profiles without renaming; every metric a team defines surfaces on every profile type.

### Columns

Column | Type | Nullable | Description
`id` | String | NOT NULL | Usage metric UUID.
`team_id` | Integer | NOT NULL |
`group_type_index` | Integer | NOT NULL | Legacy; the query runner ignores it and evaluates every metric regardless. Don't filter on it.
`name` | String | NOT NULL | Metric name.
`format` | String | NOT NULL | Display format: 'numeric' or 'currency'.
`interval` | Integer | NOT NULL | Rolling window length, in days, the metric is computed over.
`display` | String | NOT NULL | How the metric is visualized, e.g. 'number' or 'sparkline'.
`filters` | JSON | NOT NULL | JSON event/action filters ({"events": [...], "actions": [...], "properties": [...]}) or data warehouse filters ({"source": "data_warehouse", "table_name": "...", "timestamp_field": "...", "key_field": "..."}).
`math` | String | NOT NULL | Aggregation: 'count' or 'sum'; 'sum' aggregates math_property.
`math_property` | String | NULL | Property aggregated when math is property-based, e.g. sum.

### Key relationships

- Metrics are referenced by the Customer Analytics profile UI for both group and person profiles. There is no direct FK to insights, dashboards, group types, or persons.
- The stored `(team_id, group_type_index, name)` unique constraint is an artifact of the group-only era; treat `name` as unique per team in practice.

### Important notes

- Metric values are not stored here; they are computed on demand by executing `filters` against the events table for the profile being viewed. An internal `bytecode` column (not exposed) caches the compiled filter.
- `interval` is stored in days. The API accepts only integer day values; there is no sub-day granularity.
- Do not assume `group_type_index` filters the scope of metrics — it doesn't. Treat it as historical metadata.

---

## Common query patterns

**List all usage metrics for a team:**

```sql
SELECT id, name, math, interval, display, format
FROM system.usage_metrics
ORDER BY name
```

**Find all `sum`-math metrics in the team:**

```sql
SELECT id, name, math_property, interval
FROM system.usage_metrics
WHERE math = 'sum'
ORDER BY name
```

**Group metrics by the rolling window they use:**

```sql
SELECT interval, count() AS metric_count
FROM system.usage_metrics
GROUP BY interval
ORDER BY interval
```
