# Team taxonomy (top events by count, paginated)

```sql
SELECT
    event,
    count() AS count
FROM
    events
WHERE
    and(greaterOrEquals(timestamp, minus(now(), toIntervalDay(30))), notIn(event, ['$pageleave', '$autocapture', '$$heatmap', '$copy_autocapture', '$set', '$opt_in', '$feature_flag_called', '$feature_view', '$feature_interaction', '$element_viewed', '$capture_metrics', '$create_alias', '$merge_dangerously', '$groupidentify']))
GROUP BY
    event
ORDER BY
    count DESC,
    event ASC
LIMIT 50000
```
