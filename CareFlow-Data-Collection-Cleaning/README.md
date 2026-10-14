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
|   `-- day03_missing_values_report.md
|-- src/
|   |-- data_dictionary.py
|   |-- missing_values_analysis.py
|   `-- inspect_dataset.py
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
