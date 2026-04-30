# Trends (unique users, for specific 90 days)

```sql
SELECT
    arrayMap(number -> plus(toStartOfInterval(assumeNotNull(toDateTime('2025-11-10 00:00:00')), toIntervalDay(1)), toIntervalDay(number)), range(0, plus(coalesce(dateDiff('day', toStartOfInterval(assumeNotNull(toDateTime('2025-11-10 00:00:00')), toIntervalDay(1)), toStartOfInterval(assumeNotNull(toDateTime('2025-12-10 23:59:59')), toIntervalDay(1)))), 1))) AS date,
    arrayMap(_match_date -> arraySum(arraySlice(groupArray(ifNull(count, 0)), indexOf(groupArray(day_start) AS _days_for_count, _match_date) AS _index, plus(minus(arrayLastIndex(x -> equals(x, _match_date), _days_for_count), _index), 1))), date) AS total
FROM
    (SELECT
        sum(total) AS count,
        day_start
    FROM
        (SELECT
            count(DISTINCT e.person_id) AS total,
            toStartOfDay(timestamp) AS day_start
        FROM
            events AS e
        WHERE
            and(greaterOrEquals(timestamp, toStartOfInterval(assumeNotNull(toDateTime('2025-11-10 00:00:00')), toIntervalDay(1))), lessOrEquals(timestamp, assumeNotNull(toDateTime('2025-12-10 23:59:59'))), equals(event, 'chat with ai'))
        GROUP BY
            day_start)
    GROUP BY
        day_start
    ORDER BY
        day_start ASC)
ORDER BY
    arraySum(total) DESC
LIMIT 50000
```
