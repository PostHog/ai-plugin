# Heatmaps

## Heatmap interactions (`heatmaps`)

Every click, rageclick, mouse move, and scroll-depth sample captured by the SDK when `heatmaps_opt_in` is on for the team.
This is a first-class HogQL table (no `system.` prefix). Coordinates are stored scaled _down_ by `scale_factor` (always 16) — **multiply** `x`/`y`/`viewport_*` by `scale_factor` to recover CSS pixels (e.g. `y * scale_factor`). Retained for 90 days.

### Columns

Column | Type | Nullable | Description
`session_id` | String | NOT NULL | Recording session the interaction belongs to; matches `session_replay_events.session_id`.
`team_id` | Integer | NOT NULL |
`distinct_id` | String | NOT NULL | Identifier of the user/device that interacted.
`x` | Integer | NOT NULL | X coordinate snapped to an NxN grid; multiply by `scale_factor` for the original pixel value.
`y` | Integer | NOT NULL | Y coordinate snapped to an NxN grid; multiply by `scale_factor` for the original pixel value.
`scale_factor` | Integer | NOT NULL | Grid resolution applied to `x`/`y` coordinates.
`viewport_width` | Integer | NOT NULL | Viewport width at capture time, stored scaled down like `x`; multiply by `scale_factor` for CSS pixels.
`viewport_height` | Integer | NOT NULL | Viewport height at capture time, stored scaled down like `y`; multiply by `scale_factor` for CSS pixels.
`pointer_target_fixed` | Boolean | NOT NULL | Whether the clicked element stays fixed when the page scrolls.
`current_url` | String | NOT NULL | URL of the page where the interaction occurred.
`timestamp` | DateTime | NOT NULL | When the interaction occurred (in UTC).
`type` | String | NOT NULL | Interaction type, e.g. 'click', 'rageclick', 'mousemove', 'scrolldepth'.

### Example: top click hotspots on a page (last 7 days)

```sql
SELECT
    round(x / viewport_width, 2) AS rel_x,
    y * scale_factor AS client_y,
    count() AS clicks
FROM heatmaps
WHERE current_url = 'https://example.com/pricing'
  AND type = 'click'
  AND timestamp >= now() - INTERVAL 7 DAY
GROUP BY rel_x, client_y
ORDER BY clicks DESC
LIMIT 20
```

### Example: rageclick volume by page

```sql
SELECT current_url, count() AS rageclicks
FROM heatmaps
WHERE type = 'rageclick' AND timestamp >= now() - INTERVAL 7 DAY
GROUP BY current_url
ORDER BY rageclicks DESC
LIMIT 20
```

### Important notes

- Heatmaps store coordinates, not element identity. To learn _what_ sits at a hotspot, cross-reference `$autocapture` events on the same `current_url` (their `elements_chain` / `$el_text` name the elements).
- `scrolldepth` rows encode reach down the page: `(y + viewport_height) * scale_factor` is how far the person scrolled.

## Saved heatmaps

Saved heatmaps (a pinned page URL plus rendered screenshots to overlay data on) are an operational catalog, not an analytics table — manage them through the MCP heatmap tools (`heatmaps-saved-list`, `heatmaps-saved-get`, `heatmaps-saved-create`, `heatmaps-saved-update`, `heatmaps-saved-regenerate`) rather than via SQL. The rendered screenshot itself isn't exposed over MCP; the user views it in the PostHog UI.
