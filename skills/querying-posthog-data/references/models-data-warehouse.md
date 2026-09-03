# Data Warehouse

## External Data Source (`system.data_warehouse_sources`)

External data sources represent connections to third-party data providers (Stripe, Hubspot, Postgres, etc.) that sync data into PostHog.

### Columns

Column | Type | Nullable | Description
`id` | String | NOT NULL | Source UUID. Pass it as a query's connection id to live-query a direct connection.
`team_id` | Integer | NOT NULL |
`source_type` | String | NOT NULL | Source connector type, e.g. 'Stripe', 'Postgres', 'Hubspot'.
`status` | String | NOT NULL | Legacy source-level status, deprecated in favour of per-schema status in source_schemas.status; may be stale.
`access_method` | String | NOT NULL | 'direct' for a live-query connection (nothing is synced; its tables exist only when queried through the connection), or 'warehouse' for a source synced into PostHog.
`direct_query_enabled` | Integer | NOT NULL | 1 if this synced source may also be live-queried through a direct connection, 0 otherwise. Meaningless for sources that are already access_method='direct'.
`is_live_queryable` | Integer | NOT NULL | 1 if this source can be live-queried by passing its id as a query's connection id, 0 otherwise. Use `WHERE is_live_queryable = 1` to list every connection available for live queries.
`api_version` | String | NOT NULL | Vendor API version this source is pinned to (opaque vendor label); NULL resolves to the source type's default version at sync time.
`prefix` | String | NOT NULL | Table-name prefix applied to all tables synced from this source.
`created_by_id` | Integer | NULL | User who created the source.
`created_at` | DateTime | NOT NULL | When the source was connected.
`updated_at` | DateTime | NOT NULL | When the source config was last updated.
`deleted` | Integer | NOT NULL | 1 if the source has been deleted, 0 otherwise.
`deleted_at` | DateTime | NOT NULL | When the source was deleted; NULL if not deleted.

### Source Types

Common source types include:

- `Stripe` - Payment and subscription data
- `Hubspot` - CRM and marketing data
- `Postgres` - PostgreSQL databases
- `MySQL` - MySQL databases
- `Snowflake` - Snowflake data warehouse
- `BigQuery` - Google BigQuery
- `S3` - Amazon S3 files
- `Zendesk` - Customer support data
- `Salesforce` - CRM data

### Key Relationships

- **Tables**: One source can have many `system.data_warehouse_tables` entries

---

## Data Warehouse Table (`system.data_warehouse_tables`)

Individual tables synced from external sources or manually uploaded. Each table contains columns with their types and metadata.

### Columns

Column | Type | Nullable | Description
`id` | String | NOT NULL | Warehouse table UUID.
`team_id` | Integer | NOT NULL |
`name` | String | NOT NULL | Warehouse table name (includes the source prefix).
`columns` | JSON | NOT NULL | JSON schema of the table's columns.
`row_count` | Integer | NOT NULL | Approximate number of rows in the table.
`external_data_source_id` | String | NOT NULL | Source that produced this table; joins to data_warehouse_sources.id.
`created_at` | DateTime | NOT NULL | When the table was first synced.
`updated_at` | DateTime | NOT NULL | When the table metadata was last updated.
`deleted` | Integer | NOT NULL | 1 if the table has been deleted, 0 otherwise.
`deleted_at` | DateTime | NOT NULL | When the table was deleted; NULL if not deleted.

### Columns JSON Structure

The `columns` field contains column definitions with their types:

```json
{
  "id": {
    "hogql": "IntegerDatabaseField",
    "clickhouse": "Int64",
    "valid": true
  },
  "email": {
    "hogql": "StringDatabaseField",
    "clickhouse": "Nullable(String)",
    "valid": true
  },
  "created_at": {
    "hogql": "DateTimeDatabaseField",
    "clickhouse": "DateTime64(3)",
    "valid": true
  }
}
```

### Key Relationships

- **Source**: `external_data_source_id` -> `system.data_warehouse_sources.id`

### Important Notes

- Table names may include source prefix (e.g., `stripe_customers` for Stripe source with no custom prefix)
- The `columns` field is synced from the actual data schema
- `valid: false` columns may have type mismatches or other issues
- Tables with `external_data_source_id` are managed by the sync system
- Tables without a source are user-uploaded or manually created

---

## Source Schemas (`system.source_schemas`)

Per-table sync configuration for external data sources.
Each schema represents one table or entity being synced from an external source.

### Columns

Column | Type | Nullable | Description
`id` | String | NOT NULL | Schema UUID.
`team_id` | Integer | NOT NULL |
`name` | String | NOT NULL | Name of the table/endpoint in the external source.
`source_id` | String | NOT NULL | Parent source; joins to data_warehouse_sources.id.
`table_id` | String | NOT NULL | Resulting warehouse table; joins to data_warehouse_tables.id.
`should_sync` | Boolean | NOT NULL | Whether this table is enabled for syncing.
`status` | String | NOT NULL | Latest sync status for this table, e.g. Running, Completed, Error.
`sync_type` | String | NOT NULL | Sync strategy, e.g. 'full_refresh' or 'incremental'.
`last_synced_at` | DateTime | NOT NULL | When this table last finished syncing.
`latest_error` | String | NOT NULL | Most recent sync error message, if any.
`created_at` | DateTime | NOT NULL | When the schema config was created.
`updated_at` | DateTime | NOT NULL | When the schema config was last updated.
`deleted` | Integer | NOT NULL | 1 if the schema config has been deleted, 0 otherwise.
`deleted_at` | DateTime | NOT NULL | When it was deleted; NULL if not deleted.

### Status Values

- `Running` - Sync currently in progress
- `Paused` - Sync paused by user
- `Completed` - Last sync finished successfully
- `Failed` - Last sync encountered an error
- `BillingLimitReached` - Stopped due to billing limit
- `BillingLimitTooLow` - Billing limit too low to sync

### Sync Types

- `full_refresh` - Full data reload each sync
- `incremental` - Only sync new/changed data
- `append` - Append new data without updating existing rows

### Key Relationships

- **Source**: `source_id` -> `system.data_warehouse_sources.id`
- **Table**: `table_id` -> `system.data_warehouse_tables.id`

---

## Source Sync Jobs (`system.source_sync_jobs`)

Individual sync job runs for external data sources.
Each job tracks the status, row count, and timing of a single sync operation.

### Columns

Column | Type | Nullable | Description
`id` | String | NOT NULL | Sync job UUID.
`team_id` | Integer | NOT NULL |
`pipeline_id` | String | NOT NULL | Source whose pipeline ran; joins to data_warehouse_sources.id.
`schema_id` | String | NOT NULL | Source schema being synced; joins to source_schemas.id.
`status` | String | NOT NULL | Job status, e.g. Running, Completed, Failed.
`rows_synced` | Integer | NOT NULL | Number of rows synced by this job.
`billable` | Boolean | NOT NULL | Whether the rows synced count toward billing.
`latest_error` | String | NOT NULL | Error message if the job failed.
`created_at` | DateTime | NOT NULL | When the job started.
`finished_at` | DateTime | NOT NULL | When the job finished; NULL while running.
`updated_at` | DateTime | NOT NULL | When the job row was last updated.

### Status Values

- `Running` - Sync currently in progress
- `Completed` - Sync finished successfully
- `Failed` - Sync encountered an error
- `BillingLimitReached` - Stopped due to billing limit
- `BillingLimitTooLow` - Billing limit too low to sync

### Key Relationships

- **Source**: `pipeline_id` -> `system.data_warehouse_sources.id`

---

## Common Query Patterns

**List all data warehouse tables:**

```sql
SELECT name, row_count, created_at
FROM system.data_warehouse_tables
WHERE NOT deleted
ORDER BY created_at DESC
```

**Find tables by source type:**

```sql
SELECT t.name, t.row_count, s.source_type
FROM system.data_warehouse_tables AS t
INNER JOIN system.data_warehouse_sources AS s ON t.external_data_source_id = s.id
WHERE NOT t.deleted AND s.source_type = 'Stripe'
```

**List columns for a specific table:**

```sql
SELECT name, columns
FROM system.data_warehouse_tables
WHERE name = 'stripe_customers' AND NOT deleted
```

**Find tables with specific column:**

```sql
SELECT name, JSONExtractString(columns, 'email', 'clickhouse') AS email_type
FROM system.data_warehouse_tables
WHERE NOT deleted
  AND JSONHas(columns, 'email')
```

**List active data sources with table counts:**

```sql
SELECT
  s.source_type,
  s.prefix,
  count(t.id) AS table_count,
  sum(t.row_count) AS total_rows
FROM system.data_warehouse_sources AS s
LEFT JOIN system.data_warehouse_tables AS t ON t.external_data_source_id = s.id AND NOT t.deleted
WHERE NOT s.deleted
GROUP BY s.source_type, s.prefix
ORDER BY table_count DESC
```

**View recent sync jobs with their source type:**

```sql
SELECT
  j.status,
  j.rows_synced,
  j.created_at,
  j.finished_at,
  j.latest_error,
  s.source_type
FROM system.source_sync_jobs AS j
INNER JOIN system.data_warehouse_sources AS s ON j.pipeline_id = s.id
ORDER BY j.created_at DESC
LIMIT 50
```

**Find failed sync jobs in the last 7 days:**

```sql
SELECT
  j.pipeline_id,
  j.latest_error,
  j.created_at,
  s.source_type,
  s.prefix
FROM system.source_sync_jobs AS j
INNER JOIN system.data_warehouse_sources AS s ON j.pipeline_id = s.id
WHERE j.status = 'Failed'
  AND j.created_at >= now() - INTERVAL 7 DAY
ORDER BY j.created_at DESC
```

**Get sync statistics per source:**

```sql
SELECT
  s.source_type,
  s.prefix,
  count(j.id) AS total_jobs,
  countIf(j.status = 'Completed') AS completed,
  countIf(j.status = 'Failed') AS failed,
  sum(j.rows_synced) AS total_rows_synced
FROM system.source_sync_jobs AS j
INNER JOIN system.data_warehouse_sources AS s ON j.pipeline_id = s.id
GROUP BY s.source_type, s.prefix
ORDER BY total_jobs DESC
```
