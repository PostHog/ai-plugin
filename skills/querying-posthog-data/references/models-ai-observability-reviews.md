# AI observability reviews

## Trace review (`system.trace_reviews`)

Trace reviews are review records attached to LLM traces.
Each active trace can have at most one active review at a time.

### Columns

Column | Type | Nullable | Description
`id` | UUID | NOT NULL | Review UUID.
`team_id` | Integer | NOT NULL |
`trace_id` | String | NOT NULL | LLM trace that was reviewed.
`created_by_id` | Integer | NULL | User who created the review record.
`reviewed_by_id` | Integer | NULL | User who performed the review.
`comment` | String | NULL | Reviewer's free-text comment.
`created_at` | DateTime | NOT NULL | When the review was created.
`updated_at` | DateTime | NULL | When the review was last updated.
`deleted` | Integer | NOT NULL | 1 if the review has been deleted, 0 otherwise.
`deleted_at` | DateTime | NULL | When the review was deleted; NULL if not deleted.

### Key relationships

- **Review scores**: One trace review can have many `system.trace_review_scores` rows via `review_id`
- **Pending queue items**: `trace_id` overlaps with `system.review_queue_items.trace_id`

---

## Trace review score (`system.trace_review_scores`)

Trace review scores store the saved scorer values for a review.
Each row captures one scorer definition and exactly one value type.

### Columns

Column | Type | Nullable | Description
`id` | UUID | NOT NULL | Score UUID.
`team_id` | Integer | NOT NULL |
`review_id` | UUID | NOT NULL | Review this score belongs to; joins to trace_reviews.id.
`definition_id` | UUID | NOT NULL | Score definition scored against; joins to score_definitions.id.
`definition_version` | UUID | NOT NULL | Specific version of the score definition used.
`definition_version_number` | Integer | NOT NULL | Numeric version of the score definition used.
`definition_config` | JSON | NOT NULL | JSON snapshot of the definition config at scoring time.
`categorical_values` | Array | NULL | Selected category values, for categorical score kinds.
`numeric_value` | Decimal | NULL | Recorded value, for numeric score kinds.
`boolean_value` | Boolean | NULL | Recorded value, for boolean score kinds.
`created_by_id` | Integer | NULL | User who recorded the score.
`created_at` | DateTime | NOT NULL | When the score was recorded.
`updated_at` | DateTime | NULL | When the score was last updated.

### Important notes

- Exactly one of `categorical_values`, `numeric_value`, or `boolean_value` is populated per row
- Use `definition_config` when you need the historical scoring rules rather than the current scorer definition

---

## Review queue (`system.review_queues`)

Review queues are named buckets used to route traces that still need review.

### Columns

Column | Type | Nullable | Description
`id` | UUID | NOT NULL | Queue UUID.
`team_id` | Integer | NOT NULL |
`name` | String | NOT NULL | Queue name.
`created_by_id` | Integer | NULL | User who created the queue.
`created_at` | DateTime | NOT NULL | When the queue was created.
`updated_at` | DateTime | NULL | When the queue was last updated.
`deleted` | Integer | NOT NULL | 1 if the queue has been deleted, 0 otherwise.
`deleted_at` | DateTime | NULL | When the queue was deleted; NULL if not deleted.

### Key relationships

- **Queue items**: One review queue can have many `system.review_queue_items` rows via `queue_id`

---

## Review queue item (`system.review_queue_items`)

Review queue items are pending trace assignments inside review queues.
An active trace can only be pending in one queue at a time.

### Columns

Column | Type | Nullable | Description
`id` | UUID | NOT NULL | Queue item UUID.
`team_id` | Integer | NOT NULL |
`queue_id` | UUID | NOT NULL | Queue this item belongs to; joins to review_queues.id.
`trace_id` | String | NOT NULL | LLM trace queued for review.
`created_by_id` | Integer | NULL | User who added the item to the queue.
`created_at` | DateTime | NOT NULL | When the item was queued.
`updated_at` | DateTime | NULL | When the item was last updated.
`deleted` | Integer | NOT NULL | 1 if the item has been deleted, 0 otherwise.
`deleted_at` | DateTime | NULL | When the item was deleted; NULL if not deleted.

### Important notes

- Queue items represent pending work, not completed reviews
- Saving a matching trace review may soft-delete the pending queue item

---

## Score definition (`system.score_definitions`)

Score definitions (a.k.a. "scorers") are reusable structured-score fields used by trace reviews.
Each scorer has a stable identity but config is versioned and immutable — bumping config creates a new version row.

### Columns

Column | Type | Nullable | Description
`id` | UUID | NOT NULL | Score definition UUID.
`team_id` | Integer | NOT NULL |
`name` | String | NOT NULL | Score definition name.
`description` | String | NOT NULL | What the score measures.
`kind` | String | NOT NULL | Score value type, e.g. 'categorical', 'numeric', 'boolean'.
`archived` | Boolean | NOT NULL | Whether the definition is archived.
`current_version_id` | UUID | NULL | Currently active version of this definition.
`created_by_id` | Integer | NULL | User who created the definition.
`created_at` | DateTime | NOT NULL | When the definition was created.
`updated_at` | DateTime | NULL | When the definition was last updated.

### Key relationships

- **Score values**: `system.trace_review_scores.definition_id` references `id` and `definition_version` references the current/historical version
- **Versions**: `current_version_id` points to the current immutable config; the version table itself is not exposed via HogQL — fetch full version detail through the REST API tools

### Important notes

- `kind` is immutable. Create a new scorer of the desired kind and archive the old one (there is no destroy endpoint)
- Filter on `archived = false` to mirror the default product UX
- Use the REST `llma-score-definition-get` tool when you need the full `config` payload — only metadata is exposed here

---

## Common query patterns

**List active trace reviews with their saved score counts:**

```sql
SELECT
    r.id,
    r.trace_id,
    r.reviewed_by_id,
    r.updated_at,
    count(s.id) AS score_count
FROM system.trace_reviews AS r
LEFT JOIN system.trace_review_scores AS s ON s.review_id = r.id
WHERE r.deleted = 0
GROUP BY r.id, r.trace_id, r.reviewed_by_id, r.updated_at
ORDER BY r.updated_at DESC
LIMIT 20
```

**List active review queues with pending item counts:**

```sql
SELECT
    q.id,
    q.name,
    count(i.id) AS pending_item_count
FROM system.review_queues AS q
LEFT JOIN system.review_queue_items AS i
    ON i.queue_id = q.id
   AND i.deleted = 0
WHERE q.deleted = 0
GROUP BY q.id, q.name
ORDER BY q.name ASC
```

**Find pending traces in a specific review queue:**

```sql
SELECT
    i.trace_id,
    i.created_at,
    i.created_by_id
FROM system.review_queue_items AS i
WHERE i.queue_id = '01234567-89ab-cdef-0123-456789abcdef'
  AND i.deleted = 0
ORDER BY i.created_at ASC
LIMIT 100
```

**List review scores for recently updated reviews:**

```sql
SELECT
    r.trace_id,
    s.definition_id,
    s.definition_version_number,
    s.categorical_values,
    s.numeric_value,
    s.boolean_value
FROM system.trace_review_scores AS s
INNER JOIN system.trace_reviews AS r ON r.id = s.review_id
WHERE r.deleted = 0
ORDER BY r.updated_at DESC, s.created_at ASC
LIMIT 100
```

**List active scorers with how many times each has been used:**

```sql
SELECT
    d.id,
    d.name,
    d.kind,
    count(s.id) AS uses
FROM system.score_definitions AS d
LEFT JOIN system.trace_review_scores AS s ON s.definition_id = d.id
WHERE d.archived = false
GROUP BY d.id, d.name, d.kind
ORDER BY uses DESC, d.name ASC
LIMIT 50
```
