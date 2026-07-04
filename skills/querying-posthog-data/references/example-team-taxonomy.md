# Team taxonomy (top events by count, paginated)

```sql
SELECT
    event,
    count() AS count
FROM
    events
WHERE
    and(greaterOrEquals(timestamp, minus(now(), toIntervalDay(30))), notIn(event, ['$pageleave', '$autocapture', '$$heatmap', '$copy_autocapture', '$set', '$opt_in', '$feature_flag_called', '$feature_view', '$feature_interaction', '$element_viewed', '$capture_metrics', '$create_alias', '$merge_dangerously', '$groupidentify', 'mcp_tool_call', 'mcp_tools_list', 'mcp_initialize', 'mcp_resources_list', 'mcp_resource_read', 'mcp_prompts_list', 'mcp_prompt_get', 'mcp_custom', 'posthog_identify', 'mcp init', 'mcp_mcpcat:identify', 'mcp_posthog:identify', 'mcp_tool_called', 'mcp tool call', 'mcp tool response', '$snapshot']))
GROUP BY
    event
ORDER BY
    count DESC,
    event ASC
LIMIT 50000
```
