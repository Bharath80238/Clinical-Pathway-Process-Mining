# CareFlow — Initial Data Quality Report
## 1. Objective
Validate the source event log before using it for SQL analysis and clinical pathway process mining.
## 2. Source
- Dataset: Sepsis Cases Event Log
- Source: https://huggingface.co/datasets/kondratevakate/sepsis-cases-event-log
- Original publication: Mannhardt (2016), 4TU.ResearchData
## 3. Validation checks
Record the actual results for:
- Number of rows and columns
- Unique non-missing case identifiers
- Number of missing case identifiers
- Unique activities
- Missing or invalid timestamps
- Exact duplicate rows
- Timestamp range
- Differences between the Excel copy and original Parquet file
## 4. Findings
Describe only findings observed in the validation output. Separate confirmed source issues from possible Excel export or conversion issues.
## 5. Cleaning decisions
For every cleaning step, record:
- What was changed or excluded
- Number of affected rows
- Reason for the change
- Whether the original records were preserved
Do not assign missing case IDs without verification.
## 6. Limitations
Explain any unresolved data issues and how they may affect case-level KPIs or waiting-time calculations.
## 7. Conclusion
State whether the dataset is ready for analysis, ready with documented limitations, or requires further investigation.