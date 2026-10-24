# CareFlow â€” Clinical Pathway Process Mining
## Project Overview
CareFlow is a healthcare data analytics project that explores clinical event logs to understand recorded activities, case timelines, repeated activities, and intervals between events. It uses Python, SQLite, SQL, and Streamlit to analyze and visualize the available data.
The analysis is exploratory. Long intervals and repeated activities are investigated as patterns, not automatically interpreted as clinical delays, inefficiency, or poor quality of care.
## Objectives
- Assess the quality and consistency of the source data.
- Compare the Excel and Parquet source files.
- Prepare a reproducible analysis dataset.
- Analyze case counts, activity frequencies, event sequences, and event intervals.
- Calculate descriptive metrics supported by the available fields.
- Visualize findings through a Streamlit dashboard.
- Document assumptions, limitations, and recommendations.
## Technologies
- Python
- Pandas and NumPy
- SQLite and SQL
- Matplotlib and Streamlit
- Git and GitHub
## Dataset
The project uses a clinical event-log dataset containing recorded activities, timestamps, case identifiers, organizational information, and clinical measurements.
**Dataset source:**
https://huggingface.co/datasets/kondratevakate/sepsis-cases-event-log
The local source files are expected at:
- `data/raw/events.xlsx`
- `data/raw/events.parquet`
Original source files and the generated database are excluded from Git. Obtain the dataset from its source and place the required files in the expected locations before running the project.
## Project Structure
```text
Clinical-Pathway-Process-Mining/
â”œâ”€â”€ app.py
â”œâ”€â”€ requirements.txt
â”œâ”€â”€ README.md
â”œâ”€â”€ data/
â”‚   â”œâ”€â”€ raw/
â”‚   â””â”€â”€ processed/
â”‚       â””â”€â”€ careflow.db       # Generated locally
â”œâ”€â”€ reports/
â”‚   â”œâ”€â”€ analysis_findings.md
â”‚   â”œâ”€â”€ data_quality_report.md
â”‚   â””â”€â”€ figures/
â”œâ”€â”€ sql/
â”‚   â””â”€â”€ analysis_queries.sql
â””â”€â”€ src/
    â”œâ”€â”€ data_quality.py
    â”œâ”€â”€ prepare_data.py
    â”œâ”€â”€ run_sql.py
    â””â”€â”€ visualize_pathways.py
```
## Setup
Run the following commands from the project root in PowerShell.
1. Create and activate a virtual environment if one does not already exist:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
2. Install the project dependencies:
```powershell
python -m pip install -r requirements.txt
```
3. Ensure the required source files are available under `data/raw/`.
## Execution
Run the scripts in this order.
### 1. Validate source data
```powershell
python src\data_quality.py
```
This checks the Excel and Parquet source files for consistency and summarizes key data-quality characteristics.
### 2. Prepare the analysis database
```powershell
python src\prepare_data.py
```
This creates or refreshes `data/processed/careflow.db`, preserving the raw event table and preparing the analysis table.
### 3. Execute SQL analysis
```powershell
python src\run_sql.py
```
This executes the SQL statements in `sql/analysis_queries.sql` and prints query results and validation errors.
### 4. Generate visualizations
```powershell
python src\visualize_pathways.py
```
### 5. Launch the dashboard
```powershell
python -m streamlit run app.py
```
Use the local URL printed by Streamlit to open the dashboard in your browser.
## Current Analysis Snapshot
The validated analysis table contains:
- **15,213** event records
- **1,050** distinct case-ID values
- **16** distinct activities
- **0** exact duplicate rows in the analysis table
The raw source contains 15,214 rows, including one exact duplicate removed during preparation.
Laboratory measurements have substantial missingness. The data-quality report documents missing-value counts and percentages for Leucocytes, CRP, and LacticAcid.
Case duration is calculated as the time between the first and last recorded event associated with a case ID. It is an event-log span and must not automatically be interpreted as hospital length of stay.
The literal case ID `NA` appears in 24 records. Its meaning has not been verified, so its effect on case-level statistics remains a documented limitation.
For detailed results and caveats, see:
- `reports/data_quality_report.md`
- `reports/analysis_findings.md`
## Completed Work
- Excel-versus-Parquet source validation
- Data-quality assessment and documentation
- Data preparation and SQLite database creation
- SQL analysis of activity frequencies, case timelines, inter-event intervals, and repeated activities
- Exploratory visualizations
- Streamlit dashboard implementation
## Remaining Work
- Review and validate common ordered activity sequences.
- Check the effect of ambiguous case identifiers on case-level metrics.
- Cross-check dashboard KPIs against independent SQL calculations.
- Finalize validated findings, recommendations, and limitations.
- Prepare the final project presentation and demonstration.
## Limitations
- Clinical measurement fields contain substantial missing data.
- A case ID may not necessarily represent one continuous encounter.
- Long intervals do not independently establish clinical delays.
- Repeated activities do not necessarily indicate unnecessary care.
- The data does not independently establish clinical causation or care quality.
- Results should be interpreted in the context of the source data and its limitations.
## Version Control
Use Git to track meaningful changes to code, SQL queries, reports, and documentation. Keep original datasets, generated databases, virtual environments, and secrets out of commits.
## Project Status
**Status:** Exploratory analysis and dashboard implemented; validation and final reporting remain in progress.
