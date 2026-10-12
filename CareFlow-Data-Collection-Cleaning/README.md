# CareFlow: Data Collection and Cleaning

This repository area supports the CareFlow: Clinical Pathway Process Mining project. Its Day 1 task is to record the source and inspect the Sepsis Cases Event Log without changing the original dataset.

## Folder Structure

```text
CareFlow-Data-Collection-Cleaning/
|-- data/
|   |-- dataset_source.md
|   `-- data_dictionary.md
|-- reports/
|   `-- day01_initial_inspection.md
|-- src/
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

The dataset licence and reuse conditions still need verification. Do not assume the dataset is approved for reuse.
