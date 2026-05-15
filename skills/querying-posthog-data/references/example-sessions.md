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
    and(less($start_timestamp, toDateTime('2026-05-14 18:19:14.065688')), greater($start_timestamp, toDateTime('2026-05-13 18:19:09.066319')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
