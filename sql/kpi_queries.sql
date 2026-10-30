-- =========================================================
-- CAREFLOW: KPI ANALYSIS
-- Database: SQLite 3.45.1
-- Source table: events_analysis
--
-- Definitions:
-- Case-log duration = last recorded event - first recorded event.
-- Inter-event interval = time between consecutive recorded events.
-- These are not automatically hospital length of stay or
-- clinical waiting-time measurements.
-- =========================================================


-- KPI 1: Dataset overview

SELECT
    COUNT(*) AS total_events,
    COUNT(DISTINCT case_id) AS total_cases,
    COUNT(DISTINCT activity) AS unique_activities,
    MIN(event_time) AS first_recorded_event,
    MAX(event_time) AS last_recorded_event
FROM events_analysis;


-- KPI 2: Case-log duration statistics

WITH case_durations AS (
    SELECT
        case_id,
        (
            julianday(MAX(event_time)) -
            julianday(MIN(event_time))
        ) * 24.0 AS duration_hours
    FROM events_analysis
    GROUP BY case_id
),
ranked AS (
    SELECT
        duration_hours,
        ROW_NUMBER() OVER (
            ORDER BY duration_hours
        ) AS row_num,
        COUNT(*) OVER () AS total_cases
    FROM case_durations
)
SELECT
    total_cases,
    ROUND(MIN(duration_hours), 2) AS minimum_hours,
    ROUND(AVG(duration_hours), 2) AS mean_hours,
    ROUND(MAX(duration_hours), 2) AS maximum_hours,
    ROUND(
        AVG(
            CASE
                WHEN row_num IN (
                    CAST((total_cases + 1) / 2 AS INTEGER),
                    CAST((total_cases + 2) / 2 AS INTEGER)
                )
                THEN duration_hours
            END
        ),
        2
    ) AS median_hours,
    ROUND(
        MAX(
            CASE
                WHEN row_num = CAST(total_cases * 0.90 AS INTEGER)
                     + (total_cases * 0.90 > CAST(total_cases * 0.90 AS INTEGER))
                THEN duration_hours
            END
        ),
        2
    ) AS p90_hours
FROM ranked
GROUP BY total_cases;

-- KPI 3: Inter-event interval distribution
-- Use integer epoch seconds to avoid floating-point
-- boundary errors from julianday().

WITH ordered_events AS (
    SELECT
        case_id,
        event_time,
        LEAD(event_time) OVER (
            PARTITION BY case_id
            ORDER BY event_time, activity
        ) AS next_event_time
    FROM events_analysis
),
intervals AS (
    SELECT
        unixepoch(next_event_time) -
        unixepoch(event_time) AS interval_seconds
    FROM ordered_events
    WHERE next_event_time IS NOT NULL
)
SELECT
    COUNT(*) AS total_intervals,
    ROUND(AVG(interval_seconds) / 3600.0, 2)
        AS mean_interval_hours,
    ROUND(MAX(interval_seconds) / 3600.0, 2)
        AS maximum_interval_hours,
    SUM(CASE WHEN interval_seconds > 3600 THEN 1 ELSE 0 END)
        AS intervals_over_1_hour,
    SUM(CASE WHEN interval_seconds > 21600 THEN 1 ELSE 0 END)
        AS intervals_over_6_hours,
    SUM(CASE WHEN interval_seconds > 86400 THEN 1 ELSE 0 END)
        AS intervals_over_24_hours,
    SUM(CASE WHEN interval_seconds > 259200 THEN 1 ELSE 0 END)
        AS intervals_over_72_hours,
    SUM(CASE WHEN interval_seconds > 604800 THEN 1 ELSE 0 END)
        AS intervals_over_7_days,
    SUM(CASE WHEN interval_seconds > 2592000 THEN 1 ELSE 0 END)
        AS intervals_over_30_days
FROM intervals;
-- KPI 4: Consecutive release-to-return transitions

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
),
returns AS (
    SELECT
        case_id,
        activity AS release_activity,
        (
            julianday(next_event_time) -
            julianday(event_time)
        ) AS gap_days
    FROM ordered_events
    WHERE activity LIKE 'Release %'
      AND next_activity = 'Return ER'
)
SELECT
    release_activity,
    COUNT(*) AS transition_count,
    COUNT(DISTINCT case_id) AS distinct_cases,
    ROUND(AVG(gap_days), 2) AS mean_gap_days,
    ROUND(MAX(gap_days), 2) AS maximum_gap_days
FROM returns
GROUP BY release_activity
ORDER BY transition_count DESC;


-- KPI 5: Data-quality indicators

SELECT
    'Missing case IDs' AS quality_check,
    COUNT(*) AS issue_count
FROM events_analysis
WHERE case_id IS NULL OR TRIM(case_id) = ''

UNION ALL

SELECT
    'Missing activities',
    COUNT(*)
FROM events_analysis
WHERE activity IS NULL OR TRIM(activity) = ''

UNION ALL

SELECT
    'Missing timestamps',
    COUNT(*)
FROM events_analysis
WHERE event_time IS NULL OR TRIM(event_time) = ''

UNION ALL

SELECT
    'Invalid timestamps',
    COUNT(*)
FROM events_analysis
WHERE event_time IS NOT NULL
  AND datetime(event_time) IS NULL

UNION ALL

SELECT
    'Literal NA case identifiers',
    COUNT(*)
FROM events_analysis
WHERE case_id = 'NA';

SELECT
    activity,
    COUNT(*) AS event_count,
    COUNT(DISTINCT case_id) AS cases_with_activity
FROM events_analysis
GROUP BY activity
ORDER BY event_count DESC;