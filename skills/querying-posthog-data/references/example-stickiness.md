# Stickiness (counted by pageviews from unique users, defined by at least one event for the interval, non-cumulative)

```sql
SELECT
    groupArray(num_actors) AS counts,
    groupArray(num_intervals) AS intervals
FROM
    (SELECT
        sum(num_actors) AS num_actors,
        num_intervals
    FROM
        (SELECT
            0 AS num_actors,
            plus(number, 1) AS num_intervals
        FROM
            numbers(ceil(divide(dateDiff('day', toStartOfInterval(assumeNotNull(toDateTime('2025-12-03 00:00:00')), toIntervalDay(1)), plus(toStartOfInterval(assumeNotNull(toDateTime('2025-12-10 23:59:59')), toIntervalDay(1)), toIntervalDay(1))), 1))) AS numbers
        UNION ALL
        SELECT
            count(DISTINCT aggregation_target) AS num_actors,
            num_intervals
        FROM
            (SELECT
                aggregation_target,
                count() AS num_intervals
            FROM
                (SELECT
                    e.person_id AS aggregation_target,
                    toStartOfInterval(e.timestamp, toIntervalDay(1)) AS start_of_interval
                FROM
                    events AS e
                WHERE
                    and(greaterOrEquals(timestamp, toStartOfInterval(assumeNotNull(toDateTime('2025-12-03 00:00:00')), toIntervalDay(1))), lessOrEquals(timestamp, assumeNotNull(toDateTime('2025-12-10 23:59:59'))), equals(event, '$pageview'))
                GROUP BY
                    aggregation_target,
                    start_of_interval
                HAVING
                    greater(count(), 0))
            GROUP BY
                aggregation_target)
        GROUP BY
            num_intervals
        ORDER BY
            num_intervals ASC)
    GROUP BY
        num_intervals
    ORDER BY
        num_intervals ASC)
LIMIT 50000
```
