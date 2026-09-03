# Messaging opt-outs

## Message recipient preferences (`system.message_recipient_preferences`)

Messaging preferences per recipient, one row per recipient. The `preferences` map records opt-outs and opt-ins per message category.

### Columns

Column | Type | Nullable | Description
`id` | String | NOT NULL | Preference row UUID.
`team_id` | Integer | NOT NULL |
`identifier` | String | NOT NULL | Recipient identifier, usually an email address.
`preferences` | JSON | NOT NULL | JSON map of message category ID to 'OPTED_OUT' or 'OPTED_IN'. The key '$all' covers all marketing messages; other keys are message_categories ids.
`deleted` | Integer | NOT NULL | 1 if the row has been deleted, 0 otherwise.
`created_at` | DateTime | NOT NULL | When the recipient was first recorded.
`updated_at` | DateTime | NOT NULL | When the recipient's preferences last changed.

## Message categories (`system.message_categories`)

Message categories recipients can opt out of, one row per category. Category IDs are the keys in `message_recipient_preferences.preferences`.

### Columns

Column | Type | Nullable | Description
`id` | String | NOT NULL | Category UUID, used as the key in recipient preferences.
`team_id` | Integer | NOT NULL |
`key` | String | NOT NULL | Stable category key used in the API, e.g. 'newsletter'.
`name` | String | NOT NULL | Display name of the category.
`description` | String | NOT NULL | Internal description of the category.
`public_description` | String | NOT NULL | Description shown to recipients on the preferences page.
`category_type` | String | NOT NULL | 'marketing' (opt-out applies) or 'transactional'.
`deleted` | Integer | NOT NULL | 1 if the category has been deleted, 0 otherwise.
`created_at` | DateTime | NOT NULL | When the category was created.
`updated_at` | DateTime | NOT NULL | When the category was last updated.

### Query Examples

```sql
-- Recipients opted out of all marketing messages
SELECT identifier, updated_at
FROM system.message_recipient_preferences
WHERE deleted = 0 AND JSONExtractString(preferences, '$all') = 'OPTED_OUT'
ORDER BY updated_at DESC

-- Opt-out counts per category
SELECT c.key, c.name, count() AS opted_out
FROM system.message_recipient_preferences AS p
JOIN system.message_categories AS c ON JSONExtractString(p.preferences, toString(c.id)) = 'OPTED_OUT'
WHERE p.deleted = 0 AND c.deleted = 0
GROUP BY c.key, c.name
ORDER BY opted_out DESC

-- Is a specific recipient opted out of a category (falling back to the all-marketing flag)?
SELECT identifier,
       JSONExtractString(preferences, (SELECT toString(id) FROM system.message_categories WHERE key = 'newsletter')) AS category_status,
       JSONExtractString(preferences, '$all') AS all_marketing_status
FROM system.message_recipient_preferences
WHERE deleted = 0 AND identifier = 'ally@example.com'
```
