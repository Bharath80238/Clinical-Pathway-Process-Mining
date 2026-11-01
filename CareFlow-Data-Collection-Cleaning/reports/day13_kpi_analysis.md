# KPI and Process Analysis

## Objective

Analyze the CareFlow event-log dataset using SQL to understand case volumes, activity frequencies, case durations, and transitions between activities.

## Work Completed

- Calculated the number of events in each case.
- Analyzed event counts for different activities.
- Calculated the time span between the first and last events in each case.
- Identified frequently occurring activity transitions.
- Prepared SQL analysis to calculate time gaps between consecutive events.
- Created an overall KPI summary query.

## Key Findings

- The dataset contains 15,214 records in the initial inspection.
- The analysis identified 1,050 unique cases and 16 distinct activities.
- The most frequent transition observed was Leucocytes to CRP, with 1,607 occurrences.
- The CRP to Leucocytes transition occurred 1,572 times.
- The longest recorded case time span in the inspected results was 422.32 days.

## Tools Used

- PostgreSQL
- pgAdmin
- SQL window functions and aggregate functions

## Conclusion

This analysis helped me understand case volumes, activity patterns, and recorded time spans. The results provide a foundation for further pathway analysis and investigation of potential bottlenecks. Additional validation is required before drawing conclusions about clinical delays.
