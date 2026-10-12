# Day 1: Initial Dataset Inspection

## Objective

To inspect the CareFlow event-log dataset and document its initial structure before data cleaning.

## Dataset Details

- Dataset: Sepsis Cases Event Log
- File: `events.parquet`
- Initial observed rows: 15,214
- Initial observed columns: 32
- Tools: Python, pandas, PyArrow and VS Code

## Initial Inspection

- Dataset loaded successfully using Python.
- Column names and data types were inspected.
- The first five records were reviewed.
- Missing values were checked.
- Exact duplicate rows were checked.

## Important Event-Log Fields

- `case:concept:name` — case identifier
- `concept:name` — activity name
- `time:timestamp` — event timestamp

## Pending Work

- Complete the data dictionary for all columns.
- Verify the dataset licence and reuse conditions.
- Review missing values and duplicate records before deciding on cleaning.
- Validate timestamps and case identifiers.

## Conclusion

Initial dataset inspection was performed. Further data-quality checks are required before cleaning the dataset.
