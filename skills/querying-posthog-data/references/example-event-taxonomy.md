# Event taxonomy (properties of an event, with sample values)

All properties for a given event, with up to 5 sample values each:

```sql
SELECT
    key,
    arrayMap(item -> item.3, arraySlice(reverse(arraySort(item -> tuple(item.1, item.2, item.3), groupArray(tuple(value_count, latest_seen, value)))), 1, 5)) AS values,
    count(DISTINCT value) AS total_count
FROM
    (SELECT
        key,
        value,
        count() AS value_count,
        max(timestamp) AS latest_seen
    FROM
        (SELECT
            JSONExtractKeysAndValues(properties, 'String') AS kv,
            timestamp
        FROM
            events
        WHERE
            and(greaterOrEquals(timestamp, minus(now(), toIntervalDay(30))), equals(event, '$pageview'))
        ORDER BY
            timestamp DESC
        LIMIT 100)
    ARRAY JOIN (kv).1 AS key, (kv).2 AS value
    WHERE
        and(not(match(key, '(\\$set|\\$time|\\$set_once|\\$sent_at|distinct_id|\\$ip|\\$feature\\/|\\$feature_enrollment\\/|\\$feature_interaction\\/|\\$product_tour|__|survey_dismiss|survey_responded|phjs|partial_filter_chosen|changed_action|window-id|changed_event|partial_filter)')), notEquals(value, NULL), notEquals(value, ''))
    GROUP BY
        key,
        value)
GROUP BY
    key
ORDER BY
    total_count DESC,
    key ASC
LIMIT 50000
```

Specific properties only (faster, skips the omit filter):

```sql
SELECT
    key,
    arrayMap(item -> item.3, arraySlice(reverse(arraySort(item -> tuple(item.1, item.2, item.3), groupArray(tuple(value_count, latest_seen, value)))), 1, 5)) AS values,
    count(DISTINCT value) AS total_count
FROM
    (SELECT
        key,
        value,
        count() AS value_count,
        max(timestamp) AS latest_seen
    FROM
        (SELECT
            [tuple('$browser', JSONExtractString(properties, '$browser')), tuple('$os', JSONExtractString(properties, '$os'))] AS kv,
            timestamp
        FROM
            events
        WHERE
            and(greaterOrEquals(timestamp, minus(now(), toIntervalDay(30))), equals(event, '$pageview'), or(notEquals(JSONExtractString(properties, '$browser'), ''), notEquals(JSONExtractString(properties, '$os'), ''))))
    ARRAY JOIN (kv).1 AS key, (kv).2 AS value
    WHERE
        and(notEquals(value, NULL), notEquals(value, ''))
    GROUP BY
        key,
        value)
GROUP BY
    key
ORDER BY
    total_count DESC,
    key ASC
LIMIT 50000
```
