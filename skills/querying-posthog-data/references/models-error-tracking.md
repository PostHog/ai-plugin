# Error Tracking

## ErrorTrackingIssue (`system.error_tracking_issues`)

Error tracking issues represent grouped exceptions captured by PostHog SDKs. Each issue aggregates multiple exception events that share the same fingerprint.

### Columns

Column | Type | Nullable | Description
`id` | String | NOT NULL | Issue UUID.
`team_id` | Integer | NOT NULL |
`created_at` | DateTime | NOT NULL | When the issue was first created.
`status` | String | NOT NULL | Issue status, e.g. 'active', 'resolved', 'suppressed'.
`severity` | String | NULL | Assigned issue severity, or null when unassigned.
`name` | String | NOT NULL | Issue title (usually the exception type/message).
`description` | String | NOT NULL | Issue description.

### Status Values

Status | Description
`active` | Issue is currently active and being tracked
`archived` | Issue has been archived (hidden from default views)
`resolved` | Issue has been marked as resolved
`pending_release` | Issue is pending verification in a new release
`suppressed` | Issue has been suppressed from alerts and notifications

### Key Relationships

- **Fingerprints**: Issues are linked to fingerprints (not queryable via HogQL)
- **Cohorts**: Issues can be linked to cohorts via `system.cohorts`
- **Exception Events**: Query via `events` table with `event = '$exception'` and `issue_id`

### Important Notes

- Issues group exception events by fingerprint (a hash of exception characteristics)
- The `name` field is typically auto-populated from the first exception's type/message
- Use the `events` table with `event = '$exception'` and `issue_id` to query actual exception occurrences
- Use `system.error_tracking_issues` for all-time issue counts by status or severity
- Access to `system.error_tracking_issues` follows the connected user's Error tracking permissions and only returns rows from the current project
- Use `posthog:query-error-tracking-issues-list` for issues observed during a date range or for impact counts
- Issues can be merged (combining fingerprints) or split (separating fingerprints into new issues)

---

## ErrorTrackingSymbolSet (`system.error_tracking_symbol_sets`)

Symbol sets represent uploaded source maps used to unminify JavaScript stack frames.
Rows can also track missing symbol sets so future uploads know which stack frames may need reprocessing.

### Columns

Column | Type | Nullable | Description
`id` | String | NOT NULL | Symbol set UUID.
`team_id` | Integer | NOT NULL |
`ref` | String | NOT NULL | Reference identifying the symbol set, e.g. a chunk/file id.
`release_id` | String | NULL | Release this symbol set belongs to; joins to error_tracking_releases.id.
`created_at` | DateTime | NOT NULL | When the symbol set was uploaded.
`last_used` | DateTime | NULL | When the symbol set was last used to symbolicate.
`failure_reason` | String | NULL | Why symbolication with this set failed, if applicable.

### Important Notes

- Internal storage pointers and content hashes are intentionally omitted from HogQL.
- Use `posthog:error-tracking-symbol-sets-list` with `status = 'valid'` or `status = 'invalid'` to check upload availability.
- Use `posthog:error-tracking-symbol-sets-list` with an exact `ref` to resolve a reference to an ID, then `posthog:error-tracking-symbol-sets-retrieve` or `posthog:error-tracking-symbol-sets-download-retrieve` by ID. Download URLs expire after one hour; use them immediately and do not echo them back unless the user explicitly asks.

---

## Common Query Patterns

**Find symbol set lookup failures:**

```sql
SELECT id, ref, failure_reason, created_at, last_used
FROM system.error_tracking_symbol_sets
WHERE failure_reason IS NOT NULL
ORDER BY created_at DESC
LIMIT 20
```

**Find symbol set metadata by reference:**

```sql
SELECT id, ref, release_id, created_at, last_used, failure_reason
FROM system.error_tracking_symbol_sets
WHERE ref = 'https://example.com/static/app.min.js'
LIMIT 1
```

**Find issues by status:**

```sql
SELECT id, name, status, created_at
FROM system.error_tracking_issues
WHERE status = 'active'
ORDER BY created_at DESC
LIMIT 20
```

**Find issues by name pattern:**

```sql
SELECT id, name, description, status
FROM system.error_tracking_issues
WHERE name ILIKE '%timeout%'
  AND status != 'archived'
```

**Count issues by status:**

```sql
SELECT status, count() AS count
FROM system.error_tracking_issues
GROUP BY status
ORDER BY count DESC
```

**Count issues by severity:**

```sql
SELECT severity, count() AS count
FROM system.error_tracking_issues
WHERE severity IS NOT NULL
GROUP BY severity
ORDER BY count DESC
```

**Find exception events for a specific issue:**

```sql
SELECT
    timestamp,
    properties.$exception_types[1] AS exception_type,
    properties.$exception_values[1] AS exception_message,
    properties.$exception_sources[1] AS source,
    person.id AS user_id
FROM events
WHERE event = '$exception'
  AND issue_id = '01234567-89ab-cdef-0123-456789abcdef'
  AND timestamp >= now() - INTERVAL 7 DAY
ORDER BY timestamp DESC
LIMIT 50
```

**Aggregate exception stats by issue:**

```sql
SELECT
    issue_id,
    count() AS occurrences,
    count(DISTINCT person.id) AS affected_users,
    min(timestamp) AS first_seen,
    max(timestamp) AS last_seen
FROM events
WHERE event = '$exception'
  AND isNotNull(issue_id)
  AND timestamp >= now() - INTERVAL 7 DAY
GROUP BY issue_id
ORDER BY occurrences DESC
LIMIT 20
```

**Join issues with exception events:**

```sql
SELECT
    i.id,
    i.name,
    i.status
FROM system.error_tracking_issues AS i
WHERE i.status = 'active'
  AND i.id IN (
    SELECT DISTINCT issue_id
    FROM events
    WHERE event = '$exception'
      AND timestamp >= now() - INTERVAL 1 DAY
  )
ORDER BY i.created_at DESC
```
