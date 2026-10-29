# SQL-Based Process Analysis

## Objective

Analyze clinical event sequences and time gaps between consecutive events using PostgreSQL.

## Work Completed

- Ordered events by case ID and timestamp.
- Numbered events within each case using ROW_NUMBER().
- Examined the first five activities in each case to explore process variations.
- Used LEAD() to identify the next activity and its timestamp.
- Calculated time gaps between consecutive events.

## SQL Concepts Used

- Common Table Expressions (CTEs)
- ROW_NUMBER()
- LEAD()
- STRING_AGG()
- GROUP BY and ORDER BY
- Timestamp subtraction

## Observations

The queries were designed to examine activity sequences, identify common patterns, and find event pairs with the longest recorded time gaps.

The query results should be reviewed before reporting specific patterns or bottlenecks.

## Interpretation Note

A long gap between recorded events does not automatically indicate a clinical bottleneck. Further investigation is needed to understand the reason for each gap.

## Outcome

Completed initial SQL-based process sequence and event-gap analysis for the CareFlow event-log dataset.
