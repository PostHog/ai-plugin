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
    and(less($start_timestamp, toDateTime('2026-06-25 06:03:01.827605')), greater($start_timestamp, toDateTime('2026-06-24 06:02:56.828358')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
