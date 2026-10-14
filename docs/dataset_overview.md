# CareFlow — Dataset Overview

## 1. Project Information
- **Project:** CareFlow: Clinical Pathway Process Mining
- **Domain:** Healthcare Operations and Process Analytics
- **Role:** Member 4 — Data Analysis and Documentation

## 2. Dataset Description
The `events(1).xlsx` dataset contains timestamped hospital events. Each event represents an activity associated with a patient case. The dataset will be used to reconstruct patient journeys and investigate the time taken between hospital activities.

## 3. Dataset Statistics
- Event records: 15,214
- Unique patient cases: 1,049
- Distinct activities: 16
- Total columns: 32
- Missing case identifiers: 24
- Exact duplicate rows: 1

## 4. Important Columns
| Column | Purpose |
|---|---|
| `case:concept:name` | Identifies a patient case |
| `concept:name` | Identifies the hospital activity |
| `time:timestamp` | Records the event date and time |
| `lifecycle:transition` | Records the lifecycle stage |
| `org:group` | Identifies the organizational group |
| `Age` | Patient age attribute |
| `Diagnose` | Diagnosis attribute |

## 5. Initial Data Quality Findings
- Investigate records with missing case identifiers.
- Review the exact duplicate before deciding whether to remove it.
- Check missing values in the remaining columns.
- Validate timestamps and sort events chronologically within each case.

## 6. Analysis Objectives
- Reconstruct patient journeys.
- Calculate elapsed time between consecutive activities.
- Identify common activity sequences and repeated activities.
- Investigate unusually long case durations.
- Identify potential bottlenecks supported by the event data.

## 7. Tools
Python, Pandas, Jupyter Notebook, PM4Py, Excel, Git and GitHub.

## 8. Conclusion
This dataset provides the foundation for process-mining analysis of hospital workflows. Data quality checks and chronological event analysis will be performed before drawing conclusions about potential bottlenecks.