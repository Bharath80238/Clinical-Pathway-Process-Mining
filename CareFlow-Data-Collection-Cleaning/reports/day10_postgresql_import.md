# Day 10 - PostgreSQL Dataset Import and Validation

## Objective

Import the CareFlow event-log dataset into PostgreSQL and validate the imported data using SQL queries.

## Work Completed

- Connected Python to PostgreSQL 18.
- Created the `public.events` table with 32 columns.
- Compared dataset column names and order with the database table.
- Imported the original Parquet dataset into PostgreSQL.
- Verified the imported data using SQL queries.
- Analyzed event counts for individual activities.

## Validation Results

| Check                 | Result |
| --------------------- | -----: |
| Dataset rows imported | 15,214 |
| Database columns      |     32 |
| Unique cases          |  1,050 |
| Unique activities     |     16 |
| Missing timestamps    |      0 |

## Activity Analysis

The SQL activity-count query showed that `Leucocytes` and `CRP` were among the most frequently recorded activities in the dataset.

## Data Safety

The original `events.parquet` file was preserved without modification. The dataset was imported into a separate PostgreSQL table.

## Outcome

The dataset was successfully imported into PostgreSQL, and the main row-count and data-quality validation checks matched the expected results.
