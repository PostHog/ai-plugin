# Autoresearch

## AutoresearchPipeline (`system.autoresearch_pipelines`)

A standing prediction question: a target event, a population, and a horizon ("who will download a file in the next 30 days?").
An agent searches for a model that answers it, and the product scores the population on a cadence.

### Columns

Column | Type | Nullable | Description
--- | --- | --- | ---
`id` | UUID | NOT NULL | Pipeline UUID.
`team_id` | Integer | NOT NULL | Team the pipeline belongs to.
`name` | String | NOT NULL | Human-readable name.
`description` | String | NOT NULL | Free-text description; blank when unset.
`target_event` | String | NOT NULL | Event the pipeline predicts, for example '$pageview'.
`horizon_days` | Integer | NOT NULL | Number of days ahead the prediction looks for the target event.
`status` | String | NOT NULL | One of draft, bootstrapping, running, converged, paused, archived.
`iteration_budget` | Integer | NOT NULL | Maximum training iterations the agent loop may spend.
`iteration_budget_remaining` | Integer | NULL | Training iterations still available to spend (NULL when unset).
`output_person_property` | String | NOT NULL | Person property the champion model's score is written to; blank when unset.
`last_scored_at` | DateTime | NULL | When inference last ran (NULL before the first run).
`created_at` | DateTime | NOT NULL | When the pipeline was created.
`updated_at` | DateTime | NOT NULL | When the pipeline was last modified.

### Key Relationships

- Pipelines belong to a **Team** (`team_id`)
- A pipeline owns its training runs, iterations, trained models, operational runs, and suggestions. None of those are exposed as system tables, and there is no read path for them yet.
