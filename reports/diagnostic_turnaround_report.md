# Laboratory Turnaround Time (TAT) & Diagnostic Queueing Dynamics Report

**Project**: CareFlow: Clinical Pathway Process Mining  
**Module**: Laboratory Turnaround & Diagnostic Workload Analysis  
**Author**: Amit Prajapati (Member 3 — Process Mining Analyst)  
**Date**: October 29, 2026  
**Artifact References**: `reports/diagnostic_turnaround_metrics.csv`, `reports/diagnostic_turnaround_summary.json`, `reports/figures/process_maps/diagnostic_turnaround_distribution.png`

---

## 1. Executive Summary

In clinical sepsis management, immediate diagnostic confirmation is the primary prerequisite for initiating targeted antimicrobial therapy and hemodynamic stabilization. In the CareFlow event log (1,050 patients, 15,213 events), **Central Diagnostic Laboratory (B)** executes **8,110 events**, representing **53.31% of all hospital operational events**.

This report evaluates the **Turnaround Time (TAT)**—defined as the elapsed interval from Emergency Department triage registration to verified laboratory result availability—for the three primary biomarker assays: C-Reactive Protein (`CRP`), `Leucocytes`, and `LacticAcid`.

---

## 2. Quantitative Turnaround Time Benchmarks

| Diagnostic Assay | Total Patients Tested | Total Lab Events | Median TAT (min) | Mean TAT (min) | 25th %ile (min) | 75th %ile (min) | 90th %ile (min) | IQR (min) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **C-Reactive Protein (`CRP`)** | 1,007 | 3,262 | **24.30** | 30.56 | 17.50 | 34.20 | 46.60 | 16.70 |
| **Leucocytes Count (`Leucocytes`)** | 1,012 | 3,382 | **24.41** | 30.65 | 17.52 | 34.25 | 46.64 | 16.73 |
| **Lactic Acid (`LacticAcid`)** | 860 | 1,466 | **24.97** | 31.84 | 18.00 | 35.10 | 49.55 | 17.10 |

### Key Benchmark Takeaways
1. **High Consistency Across Assays**: Median turnaround times across all three key biomarkers are clustered tightly around **24.3 to 25.0 minutes**.
2. **Co-Collection Pattern**: `CRP` and `Leucocytes` display nearly identical interquartile intervals ($IQR \approx 16.7$ min), reflecting routine batch phlebotomy collection in the Emergency Ward.
3. **90th Percentile Tails**: 10% of patient blood draws encounter prolonged turnaround times ranging from **46.6 to 49.6 minutes**, predominantly during peak ER intake hours.

---

## 3. SLA Compliance & Queueing Distribution

| Diagnostic Assay | $\le \mathbf{30}$ min Compliance (%) | $\le \mathbf{60}$ min Compliance (%) | $\le \mathbf{120}$ min Compliance (%) | Exceeding 60 min (%) |
| :--- | :---: | :---: | :---: | :---: |
| **CRP** | 68.42% | **95.16%** | 99.40% | 4.84% |
| **Leucocytes** | 68.18% | **95.14%** | 99.41% | 4.86% |
| **Lactic Acid** | 66.86% | **93.77%** | 99.07% | 6.23% |

- Over **66% of initial diagnostic panels** return results within 30 minutes.
- **93.8% – 95.2%** achieve the clinical guideline threshold of $\le 60$ minutes.
- However, 6.23% of Lactic Acid orders exceed the 60-minute window, creating a downstream bottleneck for critical resuscitation decisions.

---

## 4. Repetitive Diagnostic Testing (Lab Rework Burden)

A notable discovery from our rework detector (`src/rework_analysis.py`) and confirmed in this module is the extensive re-testing frequency throughout inpatient stays:

```
Assay Repetition Overview:
  • CRP:        68.72% of patients undergo repeat testing (avg 3.24 tests/patient)
  • Leucocytes: 66.90% of patients undergo repeat testing (avg 3.34 tests/patient)
  • LacticAcid: 20.00% of patients undergo repeat testing (avg 1.70 tests/patient)
```

- **Serial Inflammatory Tracking**: 68.7% of patients have serial `CRP` and `Leucocytes` drawn to monitor antibiotic responsiveness and clinical deterioration in Inpatient Wards (`Admission NC`).
- **Lactic Acid Clearance**: 20% of severe sepsis patients receive repeat lactic acid draws to assess tissue hypoperfusion resolution (lactic acid clearance kinetics).

---

## 5. Correlation with Sepsis Golden Hour SLA Bottlenecks

In our previous bottleneck analysis (`src/bottleneck_analysis.py`), we identified that **15.2% of sepsis patients exceeded the 60-minute Golden Hour SLA** for IV Antibiotics administration.

By cross-referencing diagnostic timestamps with antibiotic initiation:
1. **Confirmatory Delay**: In 12.8% of cases, `IV Antibiotics` was initiated *strictly after* laboratory result verification rather than immediately following clinical suspicion at triage.
2. **Turnaround Variance Impact**: For patients whose Lactic Acid TAT fell into the 90th percentile tail ($> 45$ min), the median time to IV Antibiotics expanded from 38.0 minutes to **64.5 minutes**, directly driving SLA breach.

---

## 6. Strategic Process Mining Recommendations

1. **Implement Bedside Point-of-Care Testing (POCT) for Lactic Acid**:
   - Introducing handheld arterial/venous blood gas analyzers in the Emergency Ward can compress Lactic Acid TAT from **24.97 minutes to $< 5.0$ minutes**, eliminating the Central Lab queueing tail.
2. **Decouple Empiric Antibiotic Delivery from Lab Verification**:
   - Update Emergency Department protocol so that broad-spectrum IV Antibiotics are delivered immediately post-blood culture draw, without waiting for automated leukocyte or CRP counters.
3. **Consolidated Serial Lab Orders**:
   - Implement standardized rounding order sets in `Admission NC` to prevent fragmented single-tube draws and reduce departmental handoffs between Ward and Laboratory (currently exceeding 1,550 handoffs).
