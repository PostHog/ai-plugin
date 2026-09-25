# Replay Vision

Replay Vision runs LLM scanners over session recordings.
A scanner watches a slice of recordings and records one observation per session it scans.
Observations land as `$recording_observed` events, so query findings from `events`, and query scanner configuration from the table below.

## ReplayScanner (`system.replay_scanners`)

One row per saved scanner.
One-off inline scans are not listed.

### Columns

Column | Type | Nullable | Description
--- | --- | --- | ---
`id` | String | NOT NULL | Scanner UUID.
`team_id` | Integer | NOT NULL |
`name` | String | NOT NULL | Scanner name, unique within the project.
`description` | String | NOT NULL | Free-text description; blank when unset.
`scanner_type` | String | NOT NULL | One of monitor, classifier, scorer, summarizer.
`scanner_config` | JSON | NOT NULL | Type-specific JSON config; always includes the prompt.
`query` | JSON | NOT NULL | JSON RecordingsQuery selecting the sessions the scanner watches.
`sampling_rate` | Float | NOT NULL | Random share of matching sessions scanned, 0 to 1.
`sampling_mode` | String | NOT NULL | Quality pre-filter: focused, balanced or comprehensive.
`model` | String | NOT NULL | LLM model that scans each session; sets the price.
`enabled` | Integer | NOT NULL | 1 when the scanner sweeps new recordings on schedule, 0 otherwise.
`emits_signals` | Integer | NOT NULL | 1 when findings are also pushed into the Signals inbox, 0 otherwise.
`scanner_version` | Integer | NOT NULL | Config version, bumped on every config edit.
`credit_limit` | Integer | NULL | Per-period credit cap for this scanner (NULL when uncapped).
`estimated_monthly_observations` | Integer | NULL | Last projection of observations per month (NULL before the first estimate).
`last_swept_at` | DateTime | NULL | When the scheduled sweep last ran (NULL before it has).
`created_by_id` | Integer | NULL | User who created the scanner (NULL when deleted).
`created_at` | DateTime | NOT NULL | When the scanner was created.
`updated_at` | DateTime | NOT NULL | When the scanner was last modified.

### Key Relationships

- `$recording_observed` events carry the scanner as `properties.scanner_id` and the recording as `properties.session_id`

### Important Notes

- Alerts and backfills are not system tables, because their API checks permissions a system table cannot. Read them with `vision-alerts-list` and `vision-scanners-backfills-list`.
