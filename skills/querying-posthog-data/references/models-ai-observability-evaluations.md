# AI observability evaluations

## Evaluation directory (`system.evaluation_directories`)

Evaluation directories organize online evaluations. Directories are flat. An evaluation with no directory is at the top level.

### Columns

Column | Type | Nullable | Description
`id` | UUID | NOT NULL | Directory UUID.
`team_id` | Integer | NOT NULL |
`name` | String | NOT NULL | Directory name.
`created_by_id` | Integer | NULL | User who created the directory.
`created_at` | DateTime | NOT NULL | When the directory was created.
`updated_at` | DateTime | NULL | When the directory was last updated.

## Evaluation (`system.evaluations`)

Online evaluations score AI generations or traces. Evaluation results are stored as `$ai_evaluation` events, not on this configuration table.

### Columns

Column | Type | Nullable | Description
`id` | UUID | NOT NULL | Evaluation UUID.
`team_id` | Integer | NOT NULL |
`directory_id` | UUID | NULL | Directory containing the evaluation; NULL means the top level.
`name` | String | NOT NULL | Evaluation name.
`description` | String | NOT NULL | Evaluation description.
`enabled` | Boolean | NOT NULL | Whether the evaluation is active.
`status` | String | NOT NULL | Evaluation status.
`status_reason` | String | NULL | Reason for the current status, when available.
`evaluation_type` | String | NOT NULL | Evaluation implementation type.
`evaluation_config` | JSON | NOT NULL | Evaluation-specific configuration.
`output_type` | String | NOT NULL | Evaluation result type.
`output_config` | JSON | NOT NULL | Evaluation output configuration.
`conditions` | JSON | NOT NULL | Conditions that select matching input.
`target` | String | NOT NULL | Unit evaluated, such as a generation or trace.
`target_config` | JSON | NOT NULL | Target-specific configuration.
`model_configuration_id` | UUID | NULL | Model configuration used by an LLM judge evaluation.
`created_by_id` | Integer | NULL | User who created the evaluation.
`created_at` | DateTime | NOT NULL | When the evaluation was created.
`updated_at` | DateTime | NOT NULL | When the evaluation was last updated.
`deleted` | Boolean | NOT NULL | Whether the evaluation has been deleted.

### Important notes

- Filter on `deleted = false` to match the default online evals list.
- Use `directory_id IS NULL` for evaluations at the top level.
- Deleting a directory preserves its evaluations and sets their `directory_id` to NULL.

## Common query patterns

**List directories with active evaluation counts:**

```sql
SELECT
    d.id,
    d.name,
    count(e.id) AS evaluation_count
FROM system.evaluation_directories AS d
LEFT JOIN system.evaluations AS e
    ON e.directory_id = d.id
   AND e.deleted = false
GROUP BY d.id, d.name
ORDER BY d.name ASC
```

**List active evaluations at the top level:**

```sql
SELECT id, name, evaluation_type, status, updated_at
FROM system.evaluations
WHERE deleted = false
  AND directory_id IS NULL
ORDER BY updated_at DESC
LIMIT 100
```
