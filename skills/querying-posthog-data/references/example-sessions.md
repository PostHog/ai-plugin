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
    and(less($start_timestamp, toDateTime('2026-07-28 07:15:13.067838')), greater($start_timestamp, toDateTime('2026-07-27 07:15:08.068134')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
