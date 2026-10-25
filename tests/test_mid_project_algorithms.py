"""Mid-Project Review Algorithmic Verification Test Suite
Author: Amit Prajapati (Member 3 - Process Mining Analyst)
Project: CareFlow: Clinical Pathway Process Mining
"""

import unittest
from pathlib import Path
import pandas as pd
import numpy as np

import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.heuristic_mining import compute_causal_dependency_matrix
from src.pathway_filter import (
    filter_by_activity_presence,
    filter_by_case_duration,
    filter_by_patient_cohort,
)

class TestMidProjectAlgorithms(unittest.TestCase):
    def setUp(self):
        """Build controlled clinical event log for algorithmic verification."""
        self.mock_events = pd.DataFrame([
            # Patient A: Regular completed pathway
            {"case_id": "P_A", "activity": "ER Registration", "event_time": pd.Timestamp("2024-01-01 10:00:00+00:00"), "age": 75, "infection_suspected": 1, "sirs_criteria_2_or_more": 1},
            {"case_id": "P_A", "activity": "ER Triage", "event_time": pd.Timestamp("2024-01-01 10:15:00+00:00"), "age": 75, "infection_suspected": 1, "sirs_criteria_2_or_more": 1},
            {"case_id": "P_A", "activity": "IV Antibiotics", "event_time": pd.Timestamp("2024-01-01 11:00:00+00:00"), "age": 75, "infection_suspected": 1, "sirs_criteria_2_or_more": 1},
            {"case_id": "P_A", "activity": "Admission NC", "event_time": pd.Timestamp("2024-01-01 14:00:00+00:00"), "age": 75, "infection_suspected": 1, "sirs_criteria_2_or_more": 1},
            {"case_id": "P_A", "activity": "Release A", "event_time": pd.Timestamp("2024-01-05 10:00:00+00:00"), "age": 75, "infection_suspected": 1, "sirs_criteria_2_or_more": 1},
            
            # Patient B: ICU Escalation
            {"case_id": "P_B", "activity": "ER Registration", "event_time": pd.Timestamp("2024-01-02 08:00:00+00:00"), "age": 55, "infection_suspected": 1, "sirs_criteria_2_or_more": 1},
            {"case_id": "P_B", "activity": "ER Triage", "event_time": pd.Timestamp("2024-01-02 08:10:00+00:00"), "age": 55, "infection_suspected": 1, "sirs_criteria_2_or_more": 1},
            {"case_id": "P_B", "activity": "Admission IC", "event_time": pd.Timestamp("2024-01-02 12:00:00+00:00"), "age": 55, "infection_suspected": 1, "sirs_criteria_2_or_more": 1},
            {"case_id": "P_B", "activity": "Release B", "event_time": pd.Timestamp("2024-01-20 18:00:00+00:00"), "age": 55, "infection_suspected": 1, "sirs_criteria_2_or_more": 1},
            
            # Patient C: Mild Outpatient (No antibiotics, no admission)
            {"case_id": "P_C", "activity": "ER Registration", "event_time": pd.Timestamp("2024-01-03 14:00:00+00:00"), "age": 30, "infection_suspected": 0, "sirs_criteria_2_or_more": 0},
            {"case_id": "P_C", "activity": "ER Triage", "event_time": pd.Timestamp("2024-01-03 14:20:00+00:00"), "age": 30, "infection_suspected": 0, "sirs_criteria_2_or_more": 0},
            {"case_id": "P_C", "activity": "Release A", "event_time": pd.Timestamp("2024-01-03 15:30:00+00:00"), "age": 30, "infection_suspected": 0, "sirs_criteria_2_or_more": 0},
        ])

    def test_causal_dependency_bounds(self):
        """Verify heuristic dependency values are strictly within [-1.0, 1.0]."""
        # Form PM4Py log
        import pm4py
        log = pm4py.format_dataframe(
            self.mock_events,
            case_id="case_id",
            activity_key="activity",
            timestamp_key="event_time",
        )
        dep_df, dfg, start_acts, end_acts = compute_causal_dependency_matrix(log)
        
        self.assertTrue((dep_df["dependency_score"] >= -1.0).all())
        self.assertTrue((dep_df["dependency_score"] <= 1.0).all())
        
        # ER Registration -> ER Triage should have high positive causal dependency
        reg_triage = dep_df[(dep_df["activity_from"] == "ER Registration") & (dep_df["activity_to"] == "ER Triage")]
        self.assertFalse(reg_triage.empty)
        self.assertGreater(reg_triage.iloc[0]["dependency_score"], 0.5)

    def test_activity_presence_filter(self):
        """Verify filtering by activity presence returns exact cases."""
        icu_sub = filter_by_activity_presence(self.mock_events, "Admission IC")
        self.assertEqual(icu_sub["case_id"].nunique(), 1)
        self.assertEqual(icu_sub["case_id"].iloc[0], "P_B")

    def test_case_duration_filter(self):
        """Verify case duration slicing logic."""
        # P_B has stay of 18 days (> 10 days)
        prolonged = filter_by_case_duration(self.mock_events, min_days=10.0)
        self.assertEqual(prolonged["case_id"].nunique(), 1)
        self.assertEqual(prolonged["case_id"].iloc[0], "P_B")
        
        # P_C has stay of 1.5 hours (< 1 day)
        short_stay = filter_by_case_duration(self.mock_events, max_days=1.0)
        self.assertEqual(short_stay["case_id"].nunique(), 1)
        self.assertEqual(short_stay["case_id"].iloc[0], "P_C")

    def test_patient_cohort_filter(self):
        """Verify multi-attribute patient slicing."""
        geriatric = filter_by_patient_cohort(self.mock_events, min_age=65)
        self.assertEqual(geriatric["case_id"].nunique(), 1)
        self.assertEqual(geriatric["case_id"].iloc[0], "P_A")

if __name__ == "__main__":
    unittest.main()
