# CareFlow: Data Collection and Cleaning

This repository area supports the CareFlow: Clinical Pathway Process Mining project. Its Day 1 task is to record the source and inspect the Sepsis Cases Event Log without changing the original dataset.

## Folder Structure

```text
CareFlow-Data-Collection-Cleaning/
|-- data/
|   |-- dataset_source.md
|   |-- data_dictionary.csv
|   `-- data_dictionary.md
|-- reports/
|   |-- day01_initial_inspection.md
|   |-- day03_missing_values_report.csv
|   |-- day03_missing_values_report.md
|   |-- day04_duplicate_analysis_report.md
|   |-- day05_timestamp_validation_report.csv
|   |-- day05_timestamp_validation_report.md
|   |-- day06_case_activity_validation.csv
|   |-- day06_case_activity_validation.md
|   |-- day07_data_quality_report.csv
|   `-- day07_data_quality_report.md
|-- src/
|   |-- case_activity_validation.py
|   |-- data_quality_checks.py
|   |-- data_dictionary.py
|   |-- duplicate_analysis.py
|   |-- missing_values_analysis.py
|   |-- inspect_dataset.py
|   `-- timestamp_validation.py
`-- README.md
```

The local `events.parquet` is currently in the containing VS Code workspace folder, beside this project directory. The inspection script checks this project root first and then that containing folder. It does not copy or modify the dataset.

## Prerequisites

- Python 3
- pandas
- pyarrow, for reading Parquet files

Install the packages from the VS Code PowerShell terminal:

```powershell
python -m pip install pandas pyarrow
```

## Run the Inspection

From the workspace folder, run:

```powershell
python .\CareFlow-Data-Collection-Cleaning\src\inspect_dataset.py
```

Or, from this project directory, run:

```powershell
python .\src\inspect_dataset.py
```

The script prints the dataset dimensions, column names and data types, first five records, missing-value counts, exact duplicate-row count, and types of key event-log fields. It performs inspection only; it does not remove duplicates, fill missing values, or otherwise clean the data.

## Create the Data Dictionary

From the workspace folder, run:

```powershell
python .\CareFlow-Data-Collection-Cleaning\src\data_dictionary.py
```

Or, from this project directory, run:

```powershell
python .\src\data_dictionary.py
```

The script reads `events.parquet` and creates `data\data_dictionary.csv` and `data\data_dictionary.md`. It searches the project folder first and then the containing workspace folder. If the dataset is missing, place the original file in either location and run the script again. It does not modify the dataset.

The dataset licence and reuse conditions still need verification. Do not assume the dataset is approved for reuse.

## Analyze Missing Values

From the workspace folder, run:

```powershell
python .\CareFlow-Data-Collection-Cleaning\src\missing_values_analysis.py
```

Or, from this project directory, run:

```powershell
python .\src\missing_values_analysis.py
```

The script reads `events.parquet` without changing it and creates
`reports\day03_missing_values_report.csv` and
`reports\day03_missing_values_report.md`.

## Analyze Duplicate Records

From the workspace folder, run:

```powershell
python .\CareFlow-Data-Collection-Cleaning\src\duplicate_analysis.py
```

The script checks for exact duplicate rows across all columns without changing
`events.parquet`. It writes `reports\day04_duplicate_analysis_report.md` and,
when duplicates are found, `reports\day04_duplicate_rows.csv`.

## Validate Timestamps

From the workspace folder, run:

```powershell
python .\CareFlow-Data-Collection-Cleaning\src\timestamp_validation.py
```

The script validates `time:timestamp` without changing the original dataset and
creates `reports\day05_timestamp_validation_report.csv` and
`reports\day05_timestamp_validation_report.md`.

## Validate Case IDs and Activity Names

From the workspace folder, run:

```powershell
python .\CareFlow-Data-Collection-Cleaning\src\case_activity_validation.py
```

The script checks `case:concept:name` and `concept:name` without changing the
original dataset. It reports missing values, empty or whitespace-only strings,
unique non-missing values, and the 10 most frequent non-empty activity names.
It creates `reports\day06_case_activity_validation.csv` and
`reports\day06_case_activity_validation.md`.

## Run the Data Quality Checks

From the workspace folder, run:

```powershell
python .\CareFlow-Data-Collection-Cleaning\src\data_quality_checks.py
```

The script reads the original `events.parquet` without changing it. It
summarizes row and column counts, exact duplicate rows, missing values in every
column, blank case/activity values, and timestamp validity. It creates
`reports\day07_data_quality_report.csv` with per-column details and
`reports\day07_data_quality_report.md` with a concise summary.
