# Notebooks

## Notebook (`system.notebooks`)

Notebooks are collaborative documents combining text, insights, and code.

### Columns

Column | Type | Nullable | Description
`id` | String | NOT NULL | Notebook UUID.
`short_id` | String | NOT NULL | Short URL-safe id used in notebook links.
`team_id` | Integer | NOT NULL |
`title` | String | NOT NULL | Notebook title.
`content` | JSON | NOT NULL | JSON rich-text document (ProseMirror) content.
`markdown` | String | NULL | Markdown source for markdown notebooks; NULL for legacy rich-text notebooks.
`text_content` | String | NOT NULL | Plain-text rendering of the notebook, for search.
`deleted` | Integer | NOT NULL | 1 if the notebook has been deleted, 0 otherwise.
`visibility` | String | NOT NULL | Visibility: 'default' (normal notebook) or 'internal' (system-generated, hidden from the main list).
`version` | Integer | NOT NULL | Notebook version number.
`created_by_id` | Integer | NULL | User who created the notebook.
`created_at` | DateTime | NOT NULL | When the notebook was created.
`last_modified_at` | DateTime | NOT NULL | When the notebook was last modified.

### Content Structure

Notebooks use a block-based content format:

```json
{
  "type": "doc",
  "content": [
    {
      "type": "heading",
      "attrs": {"level": 1},
      "content": [{"type": "text", "text": "Analysis Report"}]
    },
    {
      "type": "paragraph",
      "content": [{"type": "text", "text": "This notebook analyzes..."}]
    },
    {
      "type": "ph-query",
      "attrs": {
        "query": {"kind": "TrendsQuery", ...},
        "title": "Daily Active Users"
      }
    },
    {
      "type": "ph-recording-playlist",
      "attrs": {"filters": {...}}
    }
  ]
}
```

Markdown notebooks store a single `ph-markdown-notebook` block in `content`.
Use the `markdown` column when reading or editing markdown notebooks instead of selecting and parsing the raw `content` JSON.

### Block Types

Type | Description
`heading` | Header text (h1-h6)
`paragraph` | Text paragraph
`ph-query` | Embedded insight/query
`ph-recording-playlist` | Session recording list
`ph-person` | Person profile embed
`ph-cohort` | Cohort embed
`ph-feature-flag` | Feature flag embed
`codeBlock` | Code snippet

### Key Relationships

- **Team**: `team_id` -> `system.teams.id` (required)

### Important Notes

- `short_id` is unique per team and used in URLs: `/notebooks/{short_id}`
- `text_content` is auto-extracted from `content` for full-text search
- Visibility controls who can view/edit the notebook
- Notebooks support real-time collaboration via version tracking

---

## Common Query Patterns

**List notebooks by title:**

```sql
SELECT id, short_id, title, visibility, last_modified_at
FROM system.notebooks
WHERE title ILIKE '%analysis%' AND NOT deleted
ORDER BY last_modified_at DESC
LIMIT 20
```

**Find notebooks with specific content:**

```sql
SELECT id, short_id, title
FROM system.notebooks
WHERE NOT deleted
  AND text_content ILIKE '%retention%'
```

**Read markdown source for a notebook:**

```sql
SELECT short_id, title, markdown
FROM system.notebooks
WHERE short_id = 'abc123'
  AND markdown IS NOT NULL
```
