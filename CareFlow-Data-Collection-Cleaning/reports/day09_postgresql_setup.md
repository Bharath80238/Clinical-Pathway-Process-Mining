# Day 9: PostgreSQL setup

## Dataset and schema

The original `events.parquet` is in the workspace folder beside
`CareFlow-Data-Collection-Cleaning`. It was read for inspection only; it was not
copied, changed, or imported.

The dataset has 15,214 rows and 32 columns. Its Parquet schema was inspected
with the existing Python environment (`pandas` and `pyarrow`). The SQL
definition in `src\create_events_table.sql` uses:

- `TEXT` for Parquet string columns
- `BOOLEAN` for Parquet boolean columns
- `DOUBLE PRECISION` for Parquet double columns
- `TIMESTAMPTZ` for the UTC timestamp column

Columns are nullable to allow the dataset's missing values. Names containing
colons are preserved and quoted in SQL. There is no primary key because the
event data does not provide a verified unique row identifier.

## PostgreSQL availability

The computer has PostgreSQL 16 and 18 services running, and `psql.exe` is
present for both installations. The project does not document a PostgreSQL
host, port, database, username, or password, and no project database setup was
found. No connection was attempted, and the dataset has not been imported.

Do not guess which service or connection settings to use. If PostgreSQL is
already configured in pgAdmin, check its registered server's connection
properties for the host, port, and maintenance database, and confirm which
database role you are allowed to use. The saved password may not be viewable;
use the password provided by the installer or project administrator, or ask
them to create/provide a role. Because two PostgreSQL services are running,
confirm which service and port are intended before connecting. Do not put the
password in this project.

If no server is registered in pgAdmin, check Windows Services (`services.msc`)
for the PostgreSQL 16 and 18 service properties and ask the person who
installed them which instance to use and how its database and role were set
up. You will need a reachable host, port, database, role, and that role's
password. If you cannot identify these, stop and ask the administrator rather
than trying guessed credentials.

## Import method for Windows

A practical beginner workflow is to export a temporary CSV with Python and
load it from the `psql` client using `\copy`. This avoids server-side file
access requirements. The Parquet file stays unchanged. Do not commit the CSV:
it is a second copy of the dataset.

1. Open PowerShell in the workspace folder, the folder containing both
   `events.parquet` and `CareFlow-Data-Collection-Cleaning`.
2. Export a working CSV with the existing Python environment:

   ```powershell
   python -c "import pandas as pd; pd.read_parquet(r'.\events.parquet').to_csv(r'.\events.csv', index=False)"
   ```

   This creates `events.csv` next to the Parquet file. It does not overwrite
   the Parquet file. Keep the CSV private and remove it yourself when no longer
   needed and after deciding whether you need to retain the import copy.
3. Connect with the `psql.exe` belonging to the confirmed PostgreSQL instance.
   Use the host, port, database, and username supplied by pgAdmin or the
   administrator; do not guess values. Enter the password only at the
   password prompt. Do not put it in a command, script, or project file.
4. In `psql`, create the empty table by running the project SQL file from the
   workspace folder:

   ```text
   \i CareFlow-Data-Collection-Cleaning/src/create_events_table.sql
   ```

   Run this only in the intended database. It creates a new table named
   `events`; if that table already exists, stop and confirm with the database
   owner rather than dropping or replacing it.
5. Load the CSV from the same `psql` session, with the current directory still
   set to the workspace folder:

   ```text
   \copy events FROM 'events.csv' WITH (FORMAT csv, HEADER true)
   ```

   The CSV header is skipped, and the remaining fields follow the original
   column order. Check that the command reports the expected number of copied
   rows (15,214), then verify with `SELECT count(*) FROM events;` and a small
   read-only sample query before treating the import as complete.

These are planned steps only. No table was created and no data was imported
during Day 9 setup.
