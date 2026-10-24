# CareFlow — Data Dictionary

## 1. Introduction

This document describes the fields in the `events(1).xlsx` dataset used for the CareFlow: Clinical Pathway Process Mining project.

The dataset contains timestamped hospital events, patient case identifiers, clinical indicators, diagnostic activities, and laboratory measurements.

## 2. Event Identification and Process Fields

| Column | Description | Data Type | Purpose |
|---|---|---|---|
| `case:concept:name` | Patient case identifier | Text | Groups events belonging to a case |
| `concept:name` | Recorded hospital activity | Text | Reconstructs the process flow |
| `time:timestamp` | Date and time of an event | DateTime | Orders events and calculates elapsed time |
| `lifecycle:transition` | Lifecycle stage of an event | Text | Identifies the event's recorded stage |
| `org:group` | Organizational group associated with an event | Text | Supports analysis by group |

## 3. Patient and Diagnosis Fields

| Column | Description | Data Type | Purpose |
|---|---|---|---|
| `Age` | Recorded patient age | Numeric | Supports age-related analysis |
| `Diagnose` | Recorded diagnosis or diagnostic category | Text | Supports case-level analysis |

## 4. Clinical Indicator Fields

These fields represent recorded clinical indicators or conditions. Their exact coding and units should be verified against the dataset documentation.

| Column | Description | Data Type |
|---|---|---|
| `InfectionSuspected` | Indicator related to suspected infection | Numeric |
| `DisfuncOrg` | Indicator related to organ dysfunction | Numeric |
| `SIRSCritTachypnea` | Indicator related to the SIRS tachypnea criterion | Numeric |
| `Hypotensie` | Indicator related to hypotension | Numeric |
| `SIRSCritHeartRate` | Indicator related to the SIRS heart-rate criterion | Numeric |
| `SIRSCritTemperature` | Indicator related to the SIRS temperature criterion | Numeric |
| `SIRSCritLeucos` | Indicator related to the SIRS leukocyte criterion | Numeric |
| `SIRSCriteria2OrMore` | Indicator related to two or more SIRS criteria | Numeric |
| `Oligurie` | Indicator related to reduced urine output | Numeric |
| `Hypoxie` | Indicator related to hypoxia | Numeric |

## 5. Diagnostic Activity Fields

These fields indicate or describe diagnostic procedures and investigations recorded in the event data.

| Column | Description | Data Type |
|---|---|---|
| `DiagnosticBlood` | Blood diagnostic activity indicator | Numeric |
| `DiagnosticArtAstrup` | Arterial blood gas analysis indicator | Numeric |
| `DiagnosticIC` | Diagnostic activity identified by the IC code | Numeric |
| `DiagnosticSputum` | Sputum diagnostic activity indicator | Numeric |
| `DiagnosticLiquor` | Cerebrospinal fluid diagnostic activity indicator | Numeric |
| `DiagnosticOther` | Other diagnostic activity indicator | Numeric |
| `DiagnosticXthorax` | Chest X-ray diagnostic activity indicator | Numeric |
| `DiagnosticUrinaryCulture` | Urine culture diagnostic activity indicator | Numeric |
| `DiagnosticUrinarySediment` | Urinary sediment diagnostic activity indicator | Numeric |
| `DiagnosticLacticAcid` | Lactic acid diagnostic activity indicator | Numeric |
| `DiagnosticECG` | ECG diagnostic activity indicator | Numeric |

## 6. Treatment Field

| Column | Description | Data Type |
|---|---|---|
| `Infusion` | Indicator related to infusion activity | Numeric |

## 7. Laboratory Measurement Fields

| Column | Description | Data Type |
|---|---|---|
| `Leucocytes` | Recorded leucocyte measurement | Numeric |
| `CRP` | Recorded C-reactive protein measurement | Numeric |
| `LacticAcid` | Recorded lactic acid measurement | Numeric |

## 8. Data Quality Considerations

1. Check missing case identifiers before using records to reconstruct patient journeys.
2. Investigate duplicate event rows before removing them.
3. Verify whether numeric indicators use binary values, counts, or another coding scheme.
4. Check measurement units and permissible ranges before interpreting laboratory results.
5. Preserve the original dataset and perform cleaning on a separate working copy.
6. Do not assume that every blank value represents a negative clinical finding.
7. Sort events by case identifier and timestamp before calculating elapsed time.

## 9. How the Fields Support Process Mining

- **Case identifier:** Groups events into patient journeys.
- **Activity name:** Identifies each step in the hospital workflow.
- **Timestamp:** Establishes chronological order and elapsed time.
- **Clinical and diagnostic fields:** Provide additional context for exploring process variations.
- **Organizational group:** Helps investigate differences between groups.
- **Age and diagnosis:** Support additional case-level analysis where appropriate.

## 10. Conclusion

The data dictionary defines the meaning and intended use of the dataset's 32 columns. It provides a reference for data cleaning, exploratory analysis, patient journey reconstruction, and subsequent process-mining work.
