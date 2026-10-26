# Day 9: PostgreSQL schema

## Dataset inspection

The project virtual environment at `.venv\Scripts\python.exe` successfully
read `events.parquet` from the workspace folder beside
`CareFlow-Data-Collection-Cleaning`. The dataset has 15,214 rows and 32
columns. Sample values below are up to three distinct, non-missing values
observed in each column; they are examples, not a description of column
meaning.

## Columns and suggested types

| Column name | pandas dtype | Sample values | Suggested PostgreSQL type |
| --- | --- | --- | --- |
| `case:concept:name` | `str` | `A`, `B`, `C` | `TEXT` |
| `InfectionSuspected` | `object` | `True`, `False` | `BOOLEAN` |
| `org:group` | `str` | `A`, `B`, `C` | `TEXT` |
| `DiagnosticBlood` | `object` | `True`, `False` | `BOOLEAN` |
| `DisfuncOrg` | `object` | `True`, `False` | `BOOLEAN` |
| `SIRSCritTachypnea` | `object` | `True`, `False` | `BOOLEAN` |
| `Hypotensie` | `object` | `True`, `False` | `BOOLEAN` |
| `SIRSCritHeartRate` | `object` | `True`, `False` | `BOOLEAN` |
| `Infusion` | `object` | `True`, `False` | `BOOLEAN` |
| `DiagnosticArtAstrup` | `object` | `True`, `False` | `BOOLEAN` |
| `concept:name` | `str` | `ER Registration`, `Leucocytes`, `CRP` | `TEXT` |
| `Age` | `float64` | `85.0`, `45.0`, `55.0` | `DOUBLE PRECISION` |
| `DiagnosticIC` | `object` | `True`, `False` | `BOOLEAN` |
| `DiagnosticSputum` | `object` | `False`, `True` | `BOOLEAN` |
| `DiagnosticLiquor` | `object` | `False`, `True` | `BOOLEAN` |
| `DiagnosticOther` | `object` | `False`, `True` | `BOOLEAN` |
| `SIRSCriteria2OrMore` | `object` | `True`, `False` | `BOOLEAN` |
| `DiagnosticXthorax` | `object` | `True`, `False` | `BOOLEAN` |
| `SIRSCritTemperature` | `object` | `True`, `False` | `BOOLEAN` |
| `DiagnosticUrinaryCulture` | `object` | `True`, `False` | `BOOLEAN` |
| `SIRSCritLeucos` | `object` | `False`, `True` | `BOOLEAN` |
| `Oligurie` | `object` | `False`, `True` | `BOOLEAN` |
| `DiagnosticLacticAcid` | `object` | `True`, `False` | `BOOLEAN` |
| `lifecycle:transition` | `str` | `complete` | `TEXT` |
| `Diagnose` | `str` | `A`, `B`, `C` | `TEXT` |
| `Hypoxie` | `object` | `False`, `True` | `BOOLEAN` |
| `DiagnosticUrinarySediment` | `object` | `True`, `False` | `BOOLEAN` |
| `DiagnosticECG` | `object` | `True`, `False` | `BOOLEAN` |
| `Leucocytes` | `float64` | `9.6`, `8.7`, `10.7` | `DOUBLE PRECISION` |
| `CRP` | `float64` | `21.0`, `109.0`, `47.0` | `DOUBLE PRECISION` |
| `LacticAcid` | `float64` | `2.2`, `0.8`, `1.6` | `DOUBLE PRECISION` |
| `time:timestamp` | `datetime64[ns, UTC]` | `2014-10-22 11:15:41+00:00`, `2014-10-22 11:27:00+00:00`, `2014-10-22 11:33:37+00:00` | `TIMESTAMPTZ` |

## Type and column-name notes

The Parquet schema confirms string, boolean, double-precision, and
timezone-aware timestamp types. Several boolean columns have pandas dtype
`object`, but their Parquet type is `bool` and the observed non-missing values
are `True` and `False`; `BOOLEAN` is the corresponding PostgreSQL type.

PostgreSQL identifiers containing colons must be double-quoted wherever used,
for example `"case:concept:name"`, `"concept:name"`, and `"time:timestamp"`.
The quoted spelling preserves the source column names. `TIMESTAMPTZ` is
appropriate for the timestamp values, which are UTC-aware. These
recommendations follow the observed schema and do not infer column meanings.

This report records inspection and type recommendations only. No PostgreSQL
table was created, and the Parquet file was not modified.
