# Session Recordings

## SessionRecording (`system.session_recordings`)

Metadata for session recordings captured by the PostHog SDK. The actual replay data lives in ClickHouse and object storage; this Postgres table stores recording-level metadata used for listing and filtering.

### Columns

Column | Type | Nullable | Description
`id` | String | NOT NULL | Recording row UUID.
`session_id` | String | NOT NULL | Session identifier; matches events.$session_id.
`team_id` | Integer | NOT NULL |
`distinct_id` | String | NOT NULL | Distinct id of the user/device recorded.
`duration` | Integer | NOT NULL | Total recording length in seconds (active + inactive).
`active_seconds` | Integer | NOT NULL | Seconds of active user engagement.
`inactive_seconds` | Integer | NOT NULL | Seconds with no user activity.
`start_time` | DateTime | NOT NULL | When the recording started.
`end_time` | DateTime | NOT NULL | When the recording ended.
`click_count` | Integer | NOT NULL | Number of clicks captured.
`keypress_count` | Integer | NOT NULL | Number of keypresses captured.
`mouse_activity_count` | Integer | NOT NULL | Number of mouse-activity events captured.
`console_log_count` | Integer | NOT NULL | Number of console.log messages captured.
`console_warn_count` | Integer | NOT NULL | Number of console.warn messages captured.
`console_error_count` | Integer | NOT NULL | Number of console.error messages captured.
`start_url` | String | NOT NULL | URL where the recording started.
`deleted` | Integer | NOT NULL | 1 if the recording has been deleted, 0 otherwise.
`created_at` | DateTime | NOT NULL | When the recording metadata row was created.
`retention_period_days` | Integer | NOT NULL | How long the recording is retained, in days.
`storage_version` | String | NOT NULL | Storage format version of the recording payload.

### Key Relationships

- Each recording belongs to a **Team** (`team_id`)
- Recordings are linked to persons via `distinct_id`
- Recordings can be added to **Session Recording Playlists** via `SessionRecordingPlaylistItem`

### Important Notes

- Recordings are created by the SDK, not via the API
- The `session_id` field is the user-facing ID (used in URLs and API calls), not the internal `id`
- Activity data (click_count, duration, etc.) is populated from ClickHouse and may be NULL for older recordings
- Filter out soft-deleted recordings with `ifNull(deleted, 0) = 0` — `deleted` is an integer 0/1, NULL for older rows
