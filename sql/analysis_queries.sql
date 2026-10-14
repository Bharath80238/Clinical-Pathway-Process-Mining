SELECT
    COUNT(*) AS total_events,
    COUNT(DISTINCT case_id) AS total_cases
FROM events_analysis;

SELECT
    activity,
    COUNT(*) AS event_count
FROM events_analysis
GROUP BY activity
ORDER BY event_count DESC;

SELECT
    case_id,
    COUNT(*) AS event_count
FROM events_analysis
GROUP BY case_id
ORDER BY event_count DESC;

SELECT
    case_id,
    MIN(event_time) AS first_event,
    MAX(event_time) AS last_event
FROM events_analysis
GROUP BY case_id;

SELECT
    case_id,
    (julianday(MAX(event_time)) -
     julianday(MIN(event_time))) * 24 AS case_duration_hours
FROM events_analysis
GROUP BY case_id
ORDER BY case_duration_hours DESC;

WITH ordered_events AS (
    SELECT
        case_id,
        activity,
        event_time,
        LEAD(activity) OVER (
            PARTITION BY case_id
            ORDER BY event_time, activity
        ) AS next_activity,
        LEAD(event_time) OVER (
            PARTITION BY case_id
            ORDER BY event_time, activity
        ) AS next_event_time
    FROM events_analysis
)
SELECT
    case_id,
    activity,
    event_time,
    next_activity,
    next_event_time,
    (julianday(next_event_time) -
     julianday(event_time)) * 24 * 60 AS minutes_until_next_event
FROM ordered_events
WHERE next_event_time IS NOT NULL
ORDER BY minutes_until_next_event DESC;

SELECT
    case_id,
    activity,
    COUNT(*) AS activity_count
FROM events_analysis
GROUP BY case_id, activity
HAVING COUNT(*) > 1
ORDER BY activity_count DESC;