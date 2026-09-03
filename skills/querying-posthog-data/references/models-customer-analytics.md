# Customer analytics accounts and feature requests

Customer analytics tracks **accounts**, their owners and custom properties, and the feature requests linked to those accounts.

**Source of truth for account ownership questions** ("who is the CSM of X?", "which accounts does Y own?"): answer them from these tables, not from warehouse CRM columns (`salesforce.*`, `hubspot.*`, ...). Warehouse copies of ownership fields can lag behind reassignments made in PostHog.

Prefer the typed `posthog:accounts-*`, `posthog:account-relationship-definitions-*`, `posthog:custom-property-definitions-*`, and `posthog:feature-request*` MCP tools for writes. Use HogQL for reads and aggregations.

## Account (`system.accounts`)

One row per account.

### Columns

Column | Type | Nullable | Description
`id` | UUID | NOT NULL | Account UUID.
`team_id` | Integer | NOT NULL |
`external_id` | String | NULL | Identifier of the account in the source system.
`name` | String | NOT NULL | Display name of the account.
`properties` | JSON | NOT NULL | JSON map of account properties; the CRM id columns below are extracted from this.
`stripe_customer_id` | String | NOT NULL |
`hubspot_deal_id` | String | NOT NULL |
`billing_id` | String | NOT NULL |
`sfdc_id` | String | NOT NULL |
`zendesk_id` | String | NOT NULL |
`created_by_id` | Integer | NULL | User who created the account record.
`created_at` | DateTime | NOT NULL | When the account record was created.
`updated_at` | DateTime | NULL | When the account record was last updated.
`churned_at` | DateTime | NULL | When the account churned; NULL if it has not churned.
`ignored_at` | DateTime | NULL | When Track Rules ignored the account; NULL if tracked.

Lazy-joined fields:

- `tags.names`: tag names.
- `notebooks.count`: number of linked internal notes.
- `custom_properties.values`: current values keyed by immutable definition ID.
- `custom_properties_history.values`: numeric value history keyed by immutable definition ID.
- `relationships.values`: active user IDs keyed by immutable relationship-definition ID.
- `meetings`: meeting count, latest start time, and the newest 10 meeting summaries.
- `slack_summaries`: summary count, latest generation time, and the newest 10 Slack summaries.
- `feature_requests`: active request count, latest update time, and the newest 10 linked requests.
- `support_tickets`: ticket count, latest message time, and the newest 10 linked tickets. Requires ticket access.
- `email_threads`: thread count, latest message time, and the newest 10 linked email threads. Requires ticket access.

The `recent` fields are JSON arrays. They hold at most 10 records, newest first. Use the top-level tables when you need complete history.

## Account relationships (`system.account_relationship_definitions`, `system.account_relationships`)

A **relationship definition** is a team-defined relationship type between a PostHog user and an account — CSM (customer success manager), Account executive, Onboarding manager, and so on. An **account relationship** is one assignment of a user to an account for a definition, with its effective range.

### `system.account_relationship_definitions` columns

Column | Type | Nullable | Description
`id` | UUID | NOT NULL | Relationship definition UUID.
`team_id` | Integer | NOT NULL |
`name` | String | NOT NULL | Human-readable name of the relationship; unique within the team.
`description` | String | NULL | What this relationship means.
`is_single_holder` | Integer | NOT NULL | 1 if only one user can hold this relationship per account at a time, 0 otherwise.
`created_by_id` | Integer | NULL | PostHog user who created the definition.
`created_at` | DateTime | NOT NULL | When the definition was created.
`updated_at` | DateTime | NULL | When the definition was last updated.

### `system.account_relationships` columns

Column | Type | Nullable | Description
`id` | UUID | NOT NULL | Relationship assignment UUID.
`team_id` | Integer | NOT NULL |
`definition_id` | UUID | NOT NULL | Relationship definition this assignment is for; join to `system.account_relationship_definitions.id`.
`account_id` | UUID | NOT NULL | Account the assignment belongs to; join to `system.accounts.id`.
`user_id` | Integer | NULL | Assigned PostHog user id.
`created_by_id` | Integer | NULL | PostHog user who made the assignment.
`started_at` | DateTime | NOT NULL | When the assignment became effective.
`ended_at` | DateTime | NULL | When the assignment ended; NULL while active.
`created_at` | DateTime | NOT NULL | When the assignment row was created.

### Important notes

- Active assignments are `ended_at IS NULL`; ended rows are kept as history.
- Do not read `csm`, `account_executive`, or `account_owner` from `system.accounts.properties`. These keys are retired, and the relationship backfill removes them. Use `system.account_relationships` for ownership.
- `system.account_relationships` exposes `user_id`, but the customer analytics HogQL system tables do not expose a current user email field. Use an account API when current organization member details are required.

## Feature requests

A feature request records a customer need across one or more accounts. Evidence belongs to a specific request and account pair. Product areas categorize requests, and history records each successful save.

The tables apply account access rules. `system.feature_requests` includes a request when the caller can access at least one active linked account. The account links and evidence tables exclude inaccessible and unlinked accounts.

### `system.feature_requests` columns

Column | Type | Nullable | Description
`id` | UUID | NOT NULL | Feature request UUID.
`team_id` | Integer | NOT NULL |
`title` | String | NOT NULL | Customer-facing request title.
`description` | String | NOT NULL | Customer-facing description in Markdown.
`status` | String | NOT NULL | Current lifecycle status: 'requested', 'planned', 'completed', 'wont_fix', or 'duplicate'.
`priority` | String | NULL | Manual priority: 'high', 'medium', 'low', or NULL.
`archived_at` | DateTime | NULL | When the request was archived. NULL while active.
`archived_by_id` | Integer | NULL | PostHog user who archived the request.
`version` | Integer | NOT NULL | Version required for optimistic concurrency on mutations.
`created_by_id` | Integer | NULL | PostHog user who created the request.
`updated_by_id` | Integer | NULL | PostHog user who last updated the request.
`created_at` | DateTime | NOT NULL | When the request was created.
`updated_at` | DateTime | NOT NULL | When the request was last updated.

### `system.feature_request_account_links` columns

One row per active request and account pair visible to the caller.

Column | Type | Nullable | Description
`id` | UUID | NOT NULL | Feature request account link UUID.
`team_id` | Integer | NOT NULL |
`feature_request_id` | UUID | NOT NULL | Feature request this link belongs to. Join to `system.feature_requests.id`.
`account_id` | UUID | NOT NULL | Affected account. Join to `system.accounts.id`.
`created_at` | DateTime | NOT NULL | When the account was first linked.
`updated_at` | DateTime | NULL | When the account link was last changed.

### `system.feature_request_evidence` columns

Column | Type | Nullable | Description
`id` | UUID | NOT NULL | Evidence UUID.
`team_id` | Integer | NOT NULL |
`account_link_id` | UUID | NOT NULL | Request and account pair this evidence supports. Join to `system.feature_request_account_links.id`.
`summary` | String | NOT NULL | Internal summary of the request evidence.
`customer_quote` | String | NOT NULL | Customer quote kept with this evidence item.
`source` | String | NOT NULL | Free-form name of the evidence source.
`source_url` | String | NOT NULL | HTTP or HTTPS link to the source, or an empty string.
`requested_on` | Date | NULL | Date the account made the request, or NULL when unknown.
`image_ids` | Array | NOT NULL | Uploaded image UUIDs attached to this evidence item, in display order.
`created_by_id` | Integer | NULL | PostHog user who added the evidence.
`updated_by_id` | Integer | NULL | PostHog user who last updated the evidence.
`created_at` | DateTime | NOT NULL | When the evidence was added.
`updated_at` | DateTime | NOT NULL | When the evidence was last updated.

### Product area tables

`system.feature_request_product_areas` defines the available areas. `system.feature_request_product_area_links` joins visible requests to those areas.

#### `system.feature_request_product_areas` columns

Column | Type | Nullable | Description
`id` | UUID | NOT NULL | Product area UUID.
`team_id` | Integer | NOT NULL |
`name` | String | NOT NULL | Team-maintained product area name.
`display_order` | Integer | NOT NULL | Position in product area selectors. Lower values appear first.
`is_active` | Integer | NOT NULL | 1 if editors can select this area for new requests, 0 otherwise.
`created_by_id` | Integer | NULL | PostHog user who created the product area.
`updated_by_id` | Integer | NULL | PostHog user who last updated the product area.
`created_at` | DateTime | NOT NULL | When the product area was created.
`updated_at` | DateTime | NOT NULL | When the product area was last updated.

#### `system.feature_request_product_area_links` columns

Column | Type | Nullable | Description
`id` | UUID | NOT NULL | Feature request product area link UUID.
`team_id` | Integer | NOT NULL |
`feature_request_id` | UUID | NOT NULL | Feature request. Join to `system.feature_requests.id`.
`product_area_id` | UUID | NOT NULL | Product area. Join to `system.feature_request_product_areas.id`.
`created_at` | DateTime | NOT NULL | When the product area was linked.

### `system.feature_request_history` columns

Column | Type | Nullable | Description
`id` | UUID | NOT NULL | Feature request history entry UUID.
`team_id` | Integer | NOT NULL |
`feature_request_id` | UUID | NOT NULL | Feature request that changed. Join to `system.feature_requests.id`.
`changed_fields` | Array | NOT NULL | Names of the fields changed in this save. Before and after values are not exposed.
`is_initial` | Integer | NOT NULL | 1 if this entry records the request's initial values, 0 otherwise.
`source` | String | NOT NULL | System that recorded the change.
`actor_id` | Integer | NULL | PostHog user who changed the request.
`changed_at` | DateTime | NOT NULL | When the request changed.

### Feature request query patterns

**List active requests and their affected accounts:**

```sql
SELECT r.id, r.title, r.status, r.priority, a.id AS account_id, a.name AS account_name
FROM system.feature_requests r
JOIN system.feature_request_account_links l ON l.feature_request_id = r.id
JOIN system.accounts a ON a.id = l.account_id
WHERE r.archived_at IS NULL
ORDER BY r.updated_at DESC
```

**Count evidence items by request and account:**

```sql
SELECT r.title, a.name AS account_name, count(e.id) AS evidence_count
FROM system.feature_requests r
JOIN system.feature_request_account_links l ON l.feature_request_id = r.id
JOIN system.accounts a ON a.id = l.account_id
LEFT JOIN system.feature_request_evidence e ON e.account_link_id = l.id
GROUP BY r.id, r.title, a.id, a.name
ORDER BY evidence_count DESC
```

**List requests for one product area:**

```sql
SELECT r.id, r.title, r.status, p.name AS product_area
FROM system.feature_requests r
JOIN system.feature_request_product_area_links l ON l.feature_request_id = r.id
JOIN system.feature_request_product_areas p ON p.id = l.product_area_id
WHERE p.name ILIKE '%analytics%'
ORDER BY r.updated_at DESC
```

## Custom properties (`system.custom_property_definitions`)

Custom properties let a team attach typed attributes to accounts. A **definition** is the attribute's shape (its name and how it is typed and rendered); the per-account **values** are queried through `system.accounts` (see below). Definitions are team-scoped — one set per team, shared across all accounts.

### Columns

Column | Type | Nullable | Description
`id` | UUID | NOT NULL | Custom property definition UUID.
`team_id` | Integer | NOT NULL |
`name` | String | NOT NULL | Human-readable name of the custom property; unique within the team.
`description` | String | NULL | Optional description of what the property represents.
`display_type` | String | NOT NULL | How the property is interpreted and rendered: 'text', 'number', 'currency', 'percent', 'date', 'datetime', 'boolean', 'select' (allowed options stored on the definition), or 'link'.
`is_big_number` | Integer | NOT NULL | 1 if large numeric values are abbreviated (e.g. 10,000 -> 10K), 0 otherwise.
`created_by_id` | Integer | NULL | User who created the definition.
`created_at` | DateTime | NOT NULL | When the definition was created.
`updated_at` | DateTime | NULL | When the definition was last updated.

### Important notes

- `is_big_number` surfaces as an integer (`0`/`1`), not a boolean.
- `display_type` is the rendering hint; effective data type is string for `text`, numeric for `number`/`currency`/`percent`, datetime for `date`/`datetime`, and boolean for `boolean`.

### Reading per-account values (`system.accounts.custom_properties`)

There is no standalone values table. An account's current value for a definition is read through a lazy join on `system.accounts`, keyed by the definition's `id`:

```text
accounts.custom_properties.values.`<definition_id>`
```

The `<definition_id>` is a `system.custom_property_definitions.id` (backtick-quoted, since it is a UUID). Only the current value is returned. Superseded values are excluded. The immutable ID keeps saved queries working when a property name changes.

## Common query patterns

**Who is the CSM (or any relationship holder) of an account:**

```sql
SELECT a.name, d.name AS relationship, r.user_id, r.started_at
FROM system.account_relationships r
JOIN system.account_relationship_definitions d ON d.id = r.definition_id
JOIN system.accounts a ON a.id = r.account_id
WHERE a.name ILIKE '%acme%'
  AND d.name = 'CSM'
  AND r.ended_at IS NULL
```

Do not use `properties.csm.email` as an email shortcut. The role keys in account properties are retired and are stripped by `backfill_account_relationships`. HogQL relationship tables return `user_id`; use an account API when current organization member details are required.

**All accounts a user holds a relationship on:**

```sql
SELECT a.name, d.name AS relationship
FROM system.account_relationships r
JOIN system.account_relationship_definitions d ON d.id = r.definition_id
JOIN system.accounts a ON a.id = r.account_id
WHERE r.user_id = 12345 AND r.ended_at IS NULL
ORDER BY a.name
```

**Assignment history of an account (including ended assignments):**

```sql
SELECT d.name AS relationship, r.user_id, r.started_at, r.ended_at
FROM system.account_relationships r
JOIN system.account_relationship_definitions d ON d.id = r.definition_id
WHERE r.account_id = '0192f000-0000-7000-8000-000000000000'
ORDER BY r.started_at DESC
```

**List all custom property definitions for a team:**

```sql
SELECT id, name, display_type, is_big_number
FROM system.custom_property_definitions
ORDER BY name
```

**Find numeric definitions:**

```sql
SELECT id, name, display_type
FROM system.custom_property_definitions
WHERE display_type IN ('number', 'currency', 'percent')
ORDER BY name
```

**Read a specific custom property value across accounts** (substitute a real definition id from the query above):

```sql
SELECT id, name, custom_properties.values.`0192f000-0000-7000-8000-000000000000` AS plan_tier
FROM system.accounts
ORDER BY name
```
