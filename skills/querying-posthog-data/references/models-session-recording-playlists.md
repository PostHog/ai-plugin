# Session Recording Playlists

## SessionRecordingPlaylist (`system.session_recording_playlists`)

Saved views for organizing session recordings. There are two types: collections (manually curated lists) and filters (saved filter criteria that dynamically match recordings).

### Columns

Column | Type | Nullable | Description
`id` | Integer | NOT NULL | Playlist id.
`short_id` | String | NOT NULL | Short URL-safe id used in playlist links.
`name` | String | NOT NULL | User-given playlist name.
`derived_name` | String | NOT NULL | Auto-generated name used when no name is set.
`description` | String | NOT NULL | Playlist description.
`team_id` | Integer | NOT NULL |
`pinned` | Integer | NOT NULL | 1 if the playlist is pinned, 0 otherwise.
`deleted` | Integer | NOT NULL | 1 if the playlist has been deleted, 0 otherwise.
`filters` | JSON | NOT NULL | JSON filters defining which recordings are in the playlist.
`type` | String | NOT NULL | Playlist type, e.g. filter-based or a collection of pinned recordings.
`created_at` | DateTime | NOT NULL | When the playlist was created.
`created_by_id` | Integer | NOT NULL | User who created the playlist.
`last_modified_at` | DateTime | NOT NULL | When the playlist was last modified.
`last_modified_by_id` | Integer | NOT NULL | User who last modified the playlist.

### Key Relationships

- Each playlist belongs to a **Team** (`team_id`)
- Playlists are created by a **User** (`created_by_id`)
- Collection playlists contain recordings via `SessionRecordingPlaylistItem` (not exposed as a system table)

### Important Notes

- The `type` field determines behavior:
  - `collection` — manually curated list of recordings
  - `filters` — saved filter criteria that dynamically match recordings
- Use `short_id` for lookups (this is the API lookup field)
- Use `deleted = 0` to filter out soft-deleted playlists — `deleted` is an integer 0/1
- The `filters` field is only meaningful when `type = 'filters'`
