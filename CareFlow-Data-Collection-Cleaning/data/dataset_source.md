# Dataset Source

## Project

CareFlow: Clinical Pathway Process Mining

## Dataset

- Dataset name: Sepsis Cases Event Log
- Source: https://huggingface.co/datasets/kondratevakate/sepsis-cases-event-log
- Original filename: `events.parquet`
- Initial observed size: 15,214 rows and 32 columns

## Inspection Tools

- Python 3.12
- pandas
- pyarrow (Parquet reader)
- `src/inspect_dataset.py` (read-only inspection)

## Verification Status

The local `events.parquet` file was accessible and read successfully. Its observed size was 15,214 rows by 32 columns. The dataset's upstream identity and provenance have not been independently verified.

**The dataset licence and reuse conditions still need verification. This project does not claim that the dataset is approved for reuse.**
