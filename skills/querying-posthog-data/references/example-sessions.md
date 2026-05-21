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
    and(less($start_timestamp, toDateTime('2026-05-20 15:24:39.858507')), greater($start_timestamp, toDateTime('2026-05-19 15:24:34.859090')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
