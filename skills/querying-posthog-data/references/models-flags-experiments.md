# Flags & Experiments

## Feature Flag (`system.feature_flags`)

Feature flags control rollouts of new features and are used for A/B testing.

### Columns

These are the only columns exposed via HogQL — the full flag model (e.g. `active`, `ensure_experience_continuity`, `last_called_at`, rollback settings) is not queryable here; fetch the flag via the feature flag API tools instead.

Column | Type | Nullable | Description
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

## Experiment (`system.experiments`)

Experiments are A/B tests that compare variants against a control group.

### Columns

These are the only columns exposed via HogQL — the full experiment model (e.g. `deleted`, `conclusion`, `metrics`, `metrics_secondary`, `stats_config`, `exposure_criteria`, `holdout_id`, `type`) is not queryable here; fetch the experiment via the experiment API tools instead.

Column | Type | Nullable | Description
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
  "feature_flag_variants": [
    {"key": "control", "name": "Control", "rollout_percentage": 50},
    {"key": "test", "name": "Test", "rollout_percentage": 50}
  ],
  "custom_exposure_filter": {...}
}
```

### Key Relationships

- **Feature Flag**: `feature_flag_id` -> `system.feature_flags.id` (required)

### Important Notes

- An experiment is a "draft" if `start_date` is NULL
- Soft-deleted experiments still appear in this table — there is no `deleted` column to filter them out; confirm via the experiment API tools when deletion status matters
- Each experiment requires an associated feature flag
- The feature flag controls variant assignment
