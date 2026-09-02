# Alerts

## AlertConfiguration (`system.alerts`)

Alerts monitor insight values and notify subscribed users when thresholds are breached.

### Columns

Column | Type | Nullable | Description
`id` | String | NOT NULL | Alert UUID.
`team_id` | Integer | NOT NULL |
`name` | String | NOT NULL | User-given name of the alert.
`insight_id` | Integer | NOT NULL | Insight the alert watches; joins to insights.id.
`enabled` | Boolean | NOT NULL | Whether the alert is active.
`state` | String | NOT NULL | Current alert state: 'Firing', 'Not firing', 'Errored', or 'Snoozed'.
`calculation_interval` | String | NOT NULL | How often the alert is evaluated, e.g. 'daily'.
`condition` | JSON | NOT NULL | JSON definition of the threshold/condition to check.
`config` | JSON | NOT NULL | JSON alert configuration (series, comparison settings, etc.).
`created_at` | DateTime | NOT NULL | When the alert was created.
`last_notified_at` | DateTime | NOT NULL | When a notification was last sent.
`last_checked_at` | DateTime | NOT NULL | When the alert was last evaluated.
`next_check_at` | DateTime | NOT NULL | When the alert is next scheduled to be evaluated.
`snoozed_until` | DateTime | NOT NULL | Alert is snoozed (no notifications) until this time.
`skip_weekend` | Boolean | NOT NULL | Whether evaluation is skipped on weekends.
`schedule_restriction` | JSON | NOT NULL | JSON restricting which days/hours the alert may fire.

### Key Relationships

- Each alert monitors exactly one **Insight** (`insight_id` → `system.insights.id`)
- Alerts belong to a **Team** (`team_id`)
- Subscribers are managed via `AlertSubscription` (not exposed as a system table)

### Important Notes

- The `condition.type` determines evaluation mode:
  - `absolute_value` — fires when the value crosses the threshold bounds
  - `relative_increase` — fires when the value increases beyond the threshold
  - `relative_decrease` — fires when the value decreases beyond the threshold
- The `config.series_index` selects which series in a multi-series insight to monitor
- `real_time` requires a Scale or Enterprise plan
- `every_15_minutes` requires a Boost, Scale, or Enterprise add-on
- Creating or updating alerts through MCP requires the `alert:write` scope. Reconnect the MCP connection if these tools are unavailable
- Alerts have a per-team limit (2 on the free tier, higher on paid plans)
