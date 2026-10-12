# Data Dictionary

Column names and data types below were observed by reading the local `events.parquet` file. Meanings have not been inferred; consult the dataset's source documentation and domain experts before assigning them. Validation status describes only what was observed locally, not whether a value is clinically correct.

| Column name                 | Data type           | Meaning      | Notes or validation status                                                     |
| --------------------------- | ------------------- | ------------ | ------------------------------------------------------------------------------ |
| `case:concept:name`         | object              | Not verified | Type observed; meaning and values need validation.                             |
| `InfectionSuspected`        | object              | Not verified | Type observed; meaning and values need validation.                             |
| `org:group`                 | object              | Not verified | Type observed; meaning and values need validation.                             |
| `DiagnosticBlood`           | object              | Not verified | Type observed; meaning and values need validation.                             |
| `DisfuncOrg`                | object              | Not verified | Type observed; meaning and values need validation.                             |
| `SIRSCritTachypnea`         | object              | Not verified | Type observed; meaning and values need validation.                             |
| `Hypotensie`                | object              | Not verified | Type observed; meaning and values need validation.                             |
| `SIRSCritHeartRate`         | object              | Not verified | Type observed; meaning and values need validation.                             |
| `Infusion`                  | object              | Not verified | Type observed; meaning and values need validation.                             |
| `DiagnosticArtAstrup`       | object              | Not verified | Type observed; meaning and values need validation.                             |
| `concept:name`              | object              | Not verified | Type observed; meaning and values need validation.                             |
| `Age`                       | float64             | Not verified | Type observed; meaning, units, and values need validation.                     |
| `DiagnosticIC`              | object              | Not verified | Type observed; meaning and values need validation.                             |
| `DiagnosticSputum`          | object              | Not verified | Type observed; meaning and values need validation.                             |
| `DiagnosticLiquor`          | object              | Not verified | Type observed; meaning and values need validation.                             |
| `DiagnosticOther`           | object              | Not verified | Type observed; meaning and values need validation.                             |
| `SIRSCriteria2OrMore`       | object              | Not verified | Type observed; meaning and values need validation.                             |
| `DiagnosticXthorax`         | object              | Not verified | Type observed; meaning and values need validation.                             |
| `SIRSCritTemperature`       | object              | Not verified | Type observed; meaning and values need validation.                             |
| `DiagnosticUrinaryCulture`  | object              | Not verified | Type observed; meaning and values need validation.                             |
| `SIRSCritLeucos`            | object              | Not verified | Type observed; meaning and values need validation.                             |
| `Oligurie`                  | object              | Not verified | Type observed; meaning and values need validation.                             |
| `DiagnosticLacticAcid`      | object              | Not verified | Type observed; meaning and values need validation.                             |
| `lifecycle:transition`      | object              | Not verified | Type observed; meaning and values need validation.                             |
| `Diagnose`                  | object              | Not verified | Type observed; meaning and values need validation.                             |
| `Hypoxie`                   | object              | Not verified | Type observed; meaning and values need validation.                             |
| `DiagnosticUrinarySediment` | object              | Not verified | Type observed; meaning and values need validation.                             |
| `DiagnosticECG`             | object              | Not verified | Type observed; meaning and values need validation.                             |
| `Leucocytes`                | float64             | Not verified | Type observed; meaning, units, and values need validation.                     |
| `CRP`                       | float64             | Not verified | Type observed; meaning, units, and values need validation.                     |
| `LacticAcid`                | float64             | Not verified | Type observed; meaning, units, and values need validation.                     |
| `time:timestamp`            | datetime64[ns, UTC] | Not verified | Timezone-aware dtype observed; timestamp meaning and ordering need validation. |
