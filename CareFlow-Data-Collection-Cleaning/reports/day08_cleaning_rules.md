# Day 8: Data Cleaning Rules

## Dataset and current findings

The Sepsis Cases Event Log has 15,214 rows and 32 columns. The event log contains 1,050 unique non-missing case IDs and 16 unique non-missing activity names.

The completed checks found:

- 377,893 missing values across 27 columns. Missingness is high in several columns: `Diagnose` has 14,417 missing values (94.76%); 23 other columns each have 14,164 missing values (93.10%). `Leucocytes`, `CRP`, and `LacticAcid` have 77.91%, 79.47%, and 90.44% missing values respectively.
- One exact duplicate row (0.01% of rows).
- No missing or invalid timestamps. All 15,214 timestamps are valid, from 2013-11-07 to 2015-06-05 (UTC).
- No missing, empty, or whitespace-only case IDs or activity names.

These are inspection findings. Cleaning has not been performed.

## Cleaning rules

### Missing values

- Keep missing values as missing unless the field's meaning and a reliable replacement are known.
- Do not replace missing values with zero, a mean, or a made-up label automatically. A missing value may mean that information was not recorded, not that its value was zero or false.
- Review columns with high missingness before using them. Do not remove a column or fill its values based only on a percentage threshold.
- If a later analysis needs an imputed value, document the reason and method, and keep a way to distinguish imputed values from observed ones.

### Exact duplicate rows

- The report found one exact duplicate row. Confirm it against the source and the event-log context before removing a repeated copy from a cleaned working dataset.
- Keep one copy only if it is confirmed to be an accidental duplicate. If it could represent a real repeated event, flag it for review instead.
- Record the number of removed rows and the rule used. Do not change the original dataset.

### Timestamps

- Current checks found no missing or invalid timestamps, so no timestamp repair is needed based on these reports.
- For any future missing or unparseable timestamp, flag the row for review. Do not guess a time or silently discard the row.
- Check timezone and timestamp format before any conversion. Preserve the original value and document conversions in a separate cleaned copy.

### Case IDs and activity names

- Current checks found no missing or blank case IDs (`case:concept:name`) or activity names (`concept:name`).
- If any are found in a later check, flag the row and verify it against the source. Do not invent an ID or activity name, and do not automatically delete the event.
- Treat whitespace-only values as empty. Trim or standardize names only when the intended value is clear, and retain a record of the original value.

## When to flag a record

Flag a record for review when the intended correction is uncertain, the value may be meaningful, or changing or deleting it could affect the event sequence or case history. Keep the original value, add a review note in the working copy or a separate issue list, and resolve it using the data source or a documented decision. Automatic changes should be limited to cases with a clear, tested rule.

## Keep the original data unchanged

Use the original `events.parquet` as a read-only source. Apply approved rules only to a separate cleaned copy, and retain a record of each change so results can be traced back to the source.

## PostgreSQL and SQL in the next stage

In the next stage, a copy of the dataset can be loaded into a PostgreSQL staging table for additional checks. SQL queries can count null or blank case IDs and activity names, identify duplicate rows, and check whether timestamp values can be parsed. These queries would support validation and produce rows for review; they do not mean that SQL validation or cleaning has already been done.
