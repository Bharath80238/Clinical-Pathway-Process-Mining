# Data Dictionary

The Sepsis Cases Event Log records event data for cases. This dictionary lists column names and data types observed by reading the local `events.parquet` file with pandas. Meanings not supported by the existing project documentation are marked `To be verified`.

| Column name | Data type | Description |
| --- | --- | --- |
| `case:concept:name` | `object` | Case identifier |
| `InfectionSuspected` | `object` | To be verified |
| `org:group` | `object` | To be verified |
| `DiagnosticBlood` | `object` | To be verified |
| `DisfuncOrg` | `object` | To be verified |
| `SIRSCritTachypnea` | `object` | To be verified |
| `Hypotensie` | `object` | To be verified |
| `SIRSCritHeartRate` | `object` | To be verified |
| `Infusion` | `object` | To be verified |
| `DiagnosticArtAstrup` | `object` | To be verified |
| `concept:name` | `object` | Activity name |
| `Age` | `float64` | To be verified |
| `DiagnosticIC` | `object` | To be verified |
| `DiagnosticSputum` | `object` | To be verified |
| `DiagnosticLiquor` | `object` | To be verified |
| `DiagnosticOther` | `object` | To be verified |
| `SIRSCriteria2OrMore` | `object` | To be verified |
| `DiagnosticXthorax` | `object` | To be verified |
| `SIRSCritTemperature` | `object` | To be verified |
| `DiagnosticUrinaryCulture` | `object` | To be verified |
| `SIRSCritLeucos` | `object` | To be verified |
| `Oligurie` | `object` | To be verified |
| `DiagnosticLacticAcid` | `object` | To be verified |
| `lifecycle:transition` | `object` | To be verified |
| `Diagnose` | `object` | To be verified |
| `Hypoxie` | `object` | To be verified |
| `DiagnosticUrinarySediment` | `object` | To be verified |
| `DiagnosticECG` | `object` | To be verified |
| `Leucocytes` | `float64` | To be verified |
| `CRP` | `float64` | To be verified |
| `LacticAcid` | `float64` | To be verified |
| `time:timestamp` | `datetime64[ns, UTC]` | Event timestamp |
