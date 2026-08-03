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
    and(less($start_timestamp, toDateTime('2026-08-03 10:58:51.183159')), greater($start_timestamp, toDateTime('2026-08-02 10:58:46.183449')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
