# Flags & Experiments

## Feature Flag (`system.feature_flags`)

Feature flags control rollouts of new features and are used for A/B testing.

### Columns

These are the only columns exposed via HogQL — the full flag model (e.g. `active`, `ensure_experience_continuity`, `last_called_at`, rollback settings) is not queryable here; fetch the flag via the feature flag API tools instead.

Column | Type | Nullable | Description
--- | --- | --- | ---
`id` | Integer | NOT NULL | Flag id.
`team_id` | Integer | NOT NULL |
`key` | String | NOT NULL | Flag key used by SDKs to evaluate the flag.
`name` | String | NOT NULL | Human-readable flag name/description.
`filters` | JSON | NOT NULL | JSON targeting rules, variants, and release conditions.
`rollout_percentage` | Integer | NOT NULL | Top-level rollout percentage (0-100); detailed rules live in filters.
`created_by_id` | Integer | NULL | User who created the flag.
`created_at` | DateTime | NOT NULL | When the flag was created.
`deleted` | Integer | NOT NULL | 1 if the flag has been deleted, 0 otherwise.

### Filters Structure

```json
{
  "groups": [
    {
      "properties": [...],
      "rollout_percentage": 50,
      "variant": "test"
    }
  ],
  "multivariate": {
    "variants": [
      {"key": "control", "rollout_percentage": 50},
      {"key": "test", "rollout_percentage": 50}
    ]
  },
  "payloads": {
    "control": {"value": "A"},
    "test": {"value": "B"}
  },
  "aggregation_group_type_index": null
}
```

### Key Relationships

- **Experiments**: Referenced by `system.experiments.feature_flag_id`
- **Surveys**: Can be linked via `system.surveys`

### Important Notes

- `key` must be unique per team
- Flag evaluation results are cached in Redis
- `aggregation_group_type_index` enables group-based targeting (company-level flags)

---

## Flag calls (`$feature_flag_called`)

An SDK sends a `$feature_flag_called` event when code evaluates a flag.
Its `$feature_flag` property holds the flag key, and `$feature_flag_response` holds the result: `true`, `false`, or a variant key.

PostHog is moving these calls from `events` to `posthog.flag_evaluations`, one organization at a time.
`project-get` returns the organization's `flag_evaluations_mode`:

Mode | Where the flag calls are | `posthog.flag_evaluations`
--- | --- | ---
0 | `events`, and `posthog.flag_evaluations` on PostHog Cloud | Queryable on PostHog Cloud only
1 | `events` and `posthog.flag_evaluations` | Queryable
2 | `posthog.flag_evaluations` only, for 90 days | Queryable

### Query flag calls from `events` in a scan of their own

Filter `event` to `$feature_flag_called` alone, as in `FROM events WHERE event = '$feature_flag_called'`.
That query works in every mode, because PostHog reads such a scan from `posthog.flag_evaluations` when the organization keeps its calls there.
On mode 2 it returns at most the last 90 days.

On mode 2, these shapes can go wrong:

- A scan that filters `event` to flag calls and other events together, such as `event IN ('$feature_flag_called', '$pageview')`, can read only `events` and return no flag calls, with no error.
  A scan with no `event` filter, such as a count of every event, can leave the flag calls out the same way.
  Give the flag calls their own scan: a separate query, or their own branch of a `UNION ALL`.
- `SELECT *` and `SAMPLE` fail with an error that says the calls are only in `posthog.flag_evaluations`.
  Select named columns, or query `posthog.flag_evaluations` directly.
- The project can have no event or property definitions for `$feature_flag_called`, so `read-data-schema` can list neither the event nor its properties.
  A missing definition is not evidence that nothing calls a flag. Count the calls with SQL.

### `posthog.flag_evaluations`

One row per flag call. On PostHog Cloud it is queryable on every mode. Self-hosted, it is queryable only on modes 1 and 2.
Filter on `flag_key` rather than `properties.$feature_flag`: `flag_key` is in the table's sort key.

Column | Type | Nullable | Description
--- | --- | --- | ---
`uuid` | UUID | NOT NULL | Unique identifier of this row.
`event` | String | NOT NULL | Always '$feature_flag_called'.
`properties` | JSON | NOT NULL | JSON map of the event's properties. Access nested keys with `properties.$lib` etc. Prefer the `flag_key`, `response`, `session_id`, `request_id` and `$group_0`..`$group_4` columns where they cover what you need: reading the same value out of this JSON scans far more data. A property that holds an empty string reads as '' here, where `events` can return NULL. A value with an escaped character, such as a quote, can also read differently than on `events`.
`timestamp` | DateTime | NOT NULL | When the flag was evaluated (client timestamp, in UTC).
`team_id` | Integer | NOT NULL |
`distinct_id` | String | NOT NULL | Identifier of the user/device the flag was evaluated for.
`created_at` | DateTime | NOT NULL | When PostHog ingested the event (server timestamp); differs from `timestamp`.
`inserted_at` | DateTime | NOT NULL | When the row was written to ClickHouse; later than `created_at` by the ingestion lag.
`flag_evaluation_person_id` | UUID | NOT NULL | The person written onto the row at ingestion time, before any later identify or merge. Unlike `person_id` it is a stored column, so filtering on it can use the table's index; it stays stale until the person-overrides squash rewrites it.
`person_id` | UUID | NOT NULL | The person the evaluation is attributed to, corrected for any later identify or merge, so `uniq(person_id)` counts a merged person once.
`flag_key` | String | NOT NULL | Key of the flag that was evaluated; the typed copy of `properties.$feature_flag`.
`response` | String | NULL | What the flag returned: 'true', 'false', or a variant key. NULL when the flag returned null or the SDK sent no response, as on events. A variant named 'null' also reads NULL. `JSONHas(properties, '$feature_flag_response')` tells a null response from a missing one.
`session_id` | String | NOT NULL | Session the evaluation happened in, if the SDK sent one.
`request_id` | String | NOT NULL | Identifier of the flag-evaluation request, shared by every flag evaluated in it.
`person_mode` | String | NOT NULL | How ingestion processed the person: 'full', 'propertyless' or 'force_upgrade'. A 'propertyless' evaluation had no person profile, so it carries no person properties.
`poe` | VirtualTable | NOT NULL |
`poe.id` | UUID | NOT NULL | The person the evaluation is attributed to, corrected for any later identify or merge, so `uniq(person_id)` counts a merged person once.
`poe.created_at` | DateTime | NOT NULL |
`poe.properties` | JSON | NOT NULL |
`$group_0` | String | NOT NULL | Key of the type-0 group the evaluation was attributed to. Join to `groups` for its properties.
`$group_1` | String | NOT NULL | Key of the type-1 group.
`$group_2` | String | NOT NULL | Key of the type-2 group.
`$group_3` | String | NOT NULL | Key of the type-3 group.
`$group_4` | String | NOT NULL | Key of the type-4 group.
`goe_0` | VirtualTable | NOT NULL |
`goe_0.key` | String | NOT NULL |
`goe_1` | VirtualTable | NOT NULL |
`goe_1.key` | String | NOT NULL |
`goe_2` | VirtualTable | NOT NULL |
`goe_2.key` | String | NOT NULL |
`goe_3` | VirtualTable | NOT NULL |
`goe_3.key` | String | NOT NULL |
`goe_4` | VirtualTable | NOT NULL |
`goe_4.key` | String | NOT NULL |

Never join this table to another one on `person_id`, because the query fails.
Join on `distinct_id`, or filter with `person_id IN (SELECT person_id FROM posthog.flag_evaluations WHERE ...)`.

---

## Experiment (`system.experiments`)

Experiments are A/B tests that compare variants against a control group.

### Columns

These are the only columns exposed via HogQL — the full experiment model (e.g. `deleted`, `conclusion`, `metrics`, `metrics_secondary`, `stats_config`, `exposure_criteria`, `holdout_id`, `type`) is not queryable here; fetch the experiment via the experiment API tools instead.

Column | Type | Nullable | Description
--- | --- | --- | ---
`id` | Integer | NOT NULL | Experiment id.
`team_id` | Integer | NOT NULL |
`name` | String | NOT NULL | Experiment name.
`description` | String | NOT NULL | Experiment description/hypothesis.
`created_by_id` | Integer | NULL | User who created the experiment.
`created_at` | DateTime | NOT NULL | When the experiment was created.
`updated_at` | DateTime | NOT NULL | When the experiment was last updated.
`filters` | JSON | NOT NULL | JSON definition of the experiment's goal metric filters.
`parameters` | JSON | NOT NULL | JSON experiment parameters (e.g. sample size settings). Flag config such as variants lives on the linked feature flag's filters, not in this column.
`start_date` | DateTime | NOT NULL | When the experiment was launched; NULL if not started.
`end_date` | DateTime | NOT NULL | When the experiment was concluded; NULL if still running.
`archived` | Integer | NOT NULL | 1 if the experiment is archived, 0 otherwise.
`feature_flag_id` | Integer | NOT NULL | Feature flag controlling variant assignment; joins to feature_flags.id.

### Parameters Structure

```json
{
  "minimum_detectable_effect": 5,
  "recommended_running_time": 14,
  "recommended_sample_size": 1000,
  "custom_exposure_filter": {...}
}
```

Variant keys and rollout percentages live on the linked flag. Read them from
`filters.multivariate.variants` in `system.feature_flags`.

### Key Relationships

- **Feature Flag**: `feature_flag_id` -> `system.feature_flags.id` (required)

### Important Notes

- An experiment is a "draft" if `start_date` is NULL
- Soft-deleted experiments still appear in this table — there is no `deleted` column to filter them out; confirm via the experiment API tools when deletion status matters
- Each experiment requires an associated feature flag
- The feature flag controls variant assignment
