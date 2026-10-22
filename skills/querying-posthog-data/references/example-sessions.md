# Sessions (listing sessions with duration, pageviews, and bounce rate)

```sql
SELECT
    session_id,
    $start_timestamp,
    $end_timestamp,
    $session_duration,
    $pageview_count,
    $is_bounce,
    $entry_current_url,
    $end_current_url
FROM
    sessions
WHERE
    and(less($start_timestamp, toDateTime('2026-10-22 11:26:08.581053')), greater($start_timestamp, toDateTime('2026-10-21 11:26:03.581406')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
