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
    and(less($start_timestamp, toDateTime('2026-05-21 20:38:10.341356')), greater($start_timestamp, toDateTime('2026-05-20 20:38:05.341903')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
