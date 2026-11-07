# Process Variant Distribution and Complexity Analysis

## 1. Objective

The objective of this analysis is to study the distribution and complexity of different process variants in the CareFlow healthcare event log.

## 2. Analysis Performed

- Ranked process variants based on the number of cases.
- Calculated the percentage of cases following each variant.
- Measured cumulative case coverage.
- Compared the average number of activities across variants.
- Analyzed average case duration for different process variants.

## 3. SQL Concepts Used

- Common Table Expressions (CTEs)
- ROW_NUMBER()
- STRING_AGG()
- COUNT() and AVG()
- Window functions
- Cumulative percentage calculations

## 4. Business Importance

This analysis helps understand how cases are distributed across different recorded workflows. It also helps identify common process patterns and variations in activity complexity and recorded duration.

## 5. Conclusion

Process variant distribution analysis provides a deeper understanding of workflow diversity. The results can support further investigation into common pathways, unusual variations, and process performance.

## 6. Results Status

SQL analysis prepared. Actual findings and numerical observations will be added after reviewing the query results.

**Note:** Case duration represents the time between the first and last recorded events, not necessarily the actual hospital stay. Event ordering for identical timestamps also requires validation.
