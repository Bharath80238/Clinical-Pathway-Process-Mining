# Unplanned Readmission Root-Cause & Clinical Risk Stratification Report

**Project**: CareFlow: Clinical Pathway Process Mining  
**Module**: Readmission Risk Mining & Clinical Root-Cause Stratification (`Return ER`)  
**Author**: Amit Prajapati (Member 3 — Process Mining Analyst)  
**Date**: October 31, 2026  
**Artifact References**: `reports/readmission_risk_factors.csv`, `reports/readmission_risk_summary.json`, `reports/figures/process_maps/readmission_risk_factors.png`

---

## 1. Executive Summary

Unplanned hospital readmissions impose severe physiological risk on recovering sepsis patients and place intense capacity strain on emergency triage and intensive care resources. 

In the CareFlow event log of **1,050 discrete sepsis patients**, **294 individuals (28.00%)** undergo an unplanned return to the Emergency Department (`Return ER`) following initial discharge.

This study mines the clinical, temporal, and pathway predictors associated with hospital return to identify patients at highest vulnerability and establish targeted transitional care interventions.

---

## 2. Statistical Risk Factor Hierarchy & Odds Ratios

The contingency table below summarizes the relative risk ($RR$), risk difference ($\Delta\%$), and Odds Ratios ($OR$) with 95% Confidence Intervals across clinical and operational features:

| Clinical Predictor Feature | Exposed Prevalence | Readmission Rate (Exposed) | Readmission Rate (Unexposed) | Relative Risk ($RR$) | Odds Ratio ($OR$) [95% CI] |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Normal Care Inpatient Stay (`Admission NC`)** | 76.19% (800) | **36.75%** | 0.00% | $\infty$ | **291.30** [18.10, 4687.71] |
| **Extended Length of Stay ($\ge 7$ Days)** | 42.38% (445) | **63.82%** | **1.65%** | **38.68** | **104.96** [54.56, 201.90] |
| **Repetitive Lab Testing ($\ge 2$ Blood Draws)** | 69.14% (726) | **37.40%** | **7.32%** | **5.11** | **7.57** [4.86, 11.77] |
| **Systemic Inflammatory Response (SIRS $\ge 2$)** | 81.33% (854) | **31.07%** | **14.72%** | **2.11** | **2.61** [1.72, 3.97] |
| **ICU Escalation (`Admission IC`)** | 10.48% (110) | **42.73%** | **26.28%** | **1.63** | **2.09** [1.40, 3.14] |
| **Geriatric Age Cohort (Age $\ge 65$)** | 72.86% (765) | **31.22%** | **19.73%** | **1.58** | **1.85** [1.33, 2.56] |
| **Sepsis Golden Hour SLA Delay ($> 60$ Min)** | 15.24% (160) | **31.61%** | **24.17%** | **1.31** | **1.45** [1.10, 1.90] |

---

## 3. Key Clinical Findings & Causal Insights

### 3.1. The Extended Length-of-Stay Inflection Threshold ($OR = 104.96$)
- Patients hospitalized for **$\ge 7$ days** exhibit an alarming **63.82% readmission rate**, compared to just **1.65%** for patients discharged within the first week ($RR = 38.68$).
- Prolonged hospitalization correlates with hospital-acquired deconditioning, secondary nosocomial infections, and severe baseline organ dysfunction (`disfunc_org`).

### 3.2. Repetitive Diagnostic Blood Draws as an Instability Biomarker ($OR = 7.57$)
- In our diagnostic turnaround module (`src/diagnostic_turnaround.py`), we identified high repeat testing rates in `CRP` (68.7%) and `Leucocytes` (66.9%).
- Patients requiring $\ge 2$ repeat blood draws have an **Odds Ratio of 7.57** for returning to the ER (37.4% vs 7.32%). Frequent blood sampling indicates fluctuating inflammatory markers and clinical uncertainty prior to discharge.

### 3.3. Post-ICU Vulnerability ($OR = 2.09$)
- While ICU patients represent only 10.48% of the total cohort, **42.73% of ICU survivors are readmitted to the ER**.
- In Care Archetype 3 (Critical ICU escalation), the readmission rate climbs to **72.5%** over long-term monitoring, highlighting severe post-intensive care syndrome.

### 3.4. Geriatric Vulnerability ($OR = 1.85$)
- Patients aged 65 and older experience a **31.22% readmission rate** compared to 19.73% in younger patients, driven by reduced physiological reserve and comorbid conditions.

---

## 4. Visual Diagnostic Representation

The multi-panel diagram generated in `reports/figures/process_maps/readmission_risk_factors.png` illustrates:
1. **Odds Ratio Forest Plot**: Highlights the massive risk multiplier associated with extended stay ($OR \approx 105$) and lab repeat testing ($OR \approx 7.6$) on a logarithmic scale.
2. **Exposed vs. Unexposed Readmission Rates**: Clearly demonstrates the elevated risk profiles for geriatric, SIRS, and ICU cohorts.

---

## 5. Concrete Hospital Intervention Strategies

Based on these mined findings, three targeted clinical pathways should be implemented:

1. **The "High-Risk Discharge" Protocol ($\ge 7$ Days or $\ge 2$ Repeat Labs)**:
   - Automatic multidisciplinary discharge review before issuing `Release A`.
   - Mandatory outpatient follow-up appointment scheduled within 72 hours of discharge.
2. **48-Hour Virtual Telehealth Check-In for ICU Step-Down Patients**:
   - Nurse-led phone triage at 48 hours post-release to verify oral antibiotic adherence and detect early respiratory or hemodynamic relapse before emergency re-presentation.
3. **Point-of-Care Discharge Biomarker Clearance**:
   - Ensure a downward trajectory in `CRP` and `LacticAcid` over 24 consecutive hours prior to final discharge to prevent premature release during ongoing occult infection.
