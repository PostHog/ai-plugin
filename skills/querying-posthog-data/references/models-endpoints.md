# Data Modeling Endpoints

## Endpoint (`system.data_modeling_endpoints`)

API endpoints that expose saved HogQL or insight queries as callable API routes.

### Columns

Column | Type | Nullable | Description
`id` | String | NOT NULL | Endpoint UUID.
`team_id` | Integer | NOT NULL |
`name` | String | NOT NULL | Endpoint name, used to call it.
`is_active` | Integer | NOT NULL | 1 if the endpoint is active and callable, 0 otherwise.
`current_version` | Integer | NOT NULL | Version number currently served; joins to data_modeling_endpoint_versions.version.
`derived_from_insight` | String | NOT NULL | Short id of the insight this endpoint was created from, if any.
`created_by_id` | Integer | NULL | User who created the endpoint.
`created_at` | DateTime | NOT NULL | When the endpoint was created.
`updated_at` | DateTime | NOT NULL | When the endpoint was last updated.
`last_executed_at` | DateTime | NOT NULL | When the endpoint was last called/executed.
`deleted` | Integer | NOT NULL |

### Example Queries

    -- List all active endpoints with their current version
    SELECT name, is_active, current_version
    FROM system.data_modeling_endpoints
    WHERE is_active = 1

    -- Find endpoints that haven't been executed recently
    SELECT name, last_executed_at
    FROM system.data_modeling_endpoints
    WHERE last_executed_at < now() - INTERVAL 30 DAY

    -- Join with versions to get current version description
    SELECT e.name, ev.description, ev.version
    FROM system.data_modeling_endpoints e
    LEFT JOIN system.data_modeling_endpoint_versions ev
      ON ev.endpoint_id = e.id AND ev.version = e.current_version

### Important Notes

- Endpoints are looked up by `name`, not `id`
- Use `system.data_modeling_endpoint_versions` to access version-specific details
- Boolean fields (`is_active`) are exposed as integers (0/1) for HogQL compatibility

---

## Endpoint Version (`system.data_modeling_endpoint_versions`)

Immutable query snapshots.
A new version is created each time an endpoint's query changes.

### Columns

Column | Type | Nullable | Description
`id` | String | NOT NULL | Endpoint version UUID.
`team_id` | Integer | NOT NULL |
`endpoint_id` | String | NOT NULL | Parent endpoint; joins to data_modeling_endpoints.id.
`version` | Integer | NOT NULL | Version number within the endpoint.
`description` | String | NOT NULL | Description of this endpoint version.
`query` | JSON | NOT NULL | JSON HogQL query executed by this version.
`data_freshness_seconds` | Integer | NOT NULL | Max age, in seconds, of cached results before re-running.
`created_at` | DateTime | NOT NULL | When this version was created.
`is_active` | Integer | NOT NULL | 1 if this version can be executed, 0 if inactive; independent of the endpoint's current_version.
`columns` | JSON | NOT NULL | JSON schema of the version's output columns.

### Example Queries

    -- Get version history for an endpoint
    SELECT ev.version, ev.description, ev.created_at
    FROM system.data_modeling_endpoint_versions ev
    LEFT JOIN system.data_modeling_endpoints e ON e.id = ev.endpoint_id
    WHERE e.name = 'my-endpoint'
    ORDER BY ev.version DESC
