"""Automated Unit Tests for Process Log Validation and Trace Metrics
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

from src.validate_process_log import (
    validate_event_log_health,
    categorize_case_completeness,
    resolve_simultaneous_events,
)
from src.trace_metrics import compute_trace_metrics

class TestProcessValidation(unittest.TestCase):
    def setUp(self):
        """Create mock clinical event log with edge cases for testing."""
        self.mock_events = pd.DataFrame([
            # Case 1: Standard completed encounter
            {"case_id": "P1", "activity": "ER Registration", "event_time": pd.Timestamp("2024-01-01 10:00:00+00:00")},
            {"case_id": "P1", "activity": "ER Triage", "event_time": pd.Timestamp("2024-01-01 10:15:00+00:00")},
            {"case_id": "P1", "activity": "CRP", "event_time": pd.Timestamp("2024-01-01 10:30:00+00:00")},
            {"case_id": "P1", "activity": "Leucocytes", "event_time": pd.Timestamp("2024-01-01 10:30:00+00:00")},  # Simultaneous
            {"case_id": "P1", "activity": "Release A", "event_time": pd.Timestamp("2024-01-02 12:00:00+00:00")},
            # Case 2: Readmitted encounter
            {"case_id": "P2", "activity": "ER Registration", "event_time": pd.Timestamp("2024-01-03 08:00:00+00:00")},
            {"case_id": "P2", "activity": "ER Triage", "event_time": pd.Timestamp("2024-01-03 08:10:00+00:00")},
            {"case_id": "P2", "activity": "Release B", "event_time": pd.Timestamp("2024-01-03 20:00:00+00:00")},
            {"case_id": "P2", "activity": "Return ER", "event_time": pd.Timestamp("2024-01-10 14:00:00+00:00")},
            # Case 3: Truncated encounter
            {"case_id": "P3", "activity": "ER Registration", "event_time": pd.Timestamp("2024-01-05 11:00:00+00:00")},
            {"case_id": "P3", "activity": "Admission NC", "event_time": pd.Timestamp("2024-01-05 15:00:00+00:00")},
        ])

    def test_log_health_check(self):
        report = validate_event_log_health(self.mock_events)
        self.assertEqual(report["total_cases"], 3)
        self.assertEqual(report["total_records"], 11)
        self.assertEqual(report["null_case_ids"], 0)
        self.assertEqual(report["chronological_inversions"], 0)
        self.assertEqual(report["cases_starting_er_reg"], 3)

    def test_simultaneous_event_resolution(self):
        resolved = resolve_simultaneous_events(self.mock_events)
        # Verify no duplicate timestamps remain
        dups = (resolved["resolved_event_time"] == resolved.groupby("case_id")["resolved_event_time"].shift(1)).sum()
        self.assertEqual(dups, 0)
        # Verify CRP comes before Leucocytes according to clinical priority
        p1_acts = resolved[resolved["case_id"] == "P1"]["activity"].tolist()
        self.assertLess(p1_acts.index("CRP"), p1_acts.index("Leucocytes"))

    def test_case_completeness_categorization(self):
        outcomes_df, summary = categorize_case_completeness(self.mock_events)
        status_map = dict(zip(outcomes_df["case_id"], outcomes_df["lifecycle_status"]))
        self.assertEqual(status_map["P1"], "Completed Normal Encounter")
        self.assertEqual(status_map["P2"], "Readmission Encounter")
        self.assertEqual(status_map["P3"], "Truncated / Open Encounter")

    def test_trace_metrics_computation(self):
        case_summary, stats = compute_trace_metrics(self.mock_events)
        self.assertEqual(stats["case_count"], 3)
        self.assertEqual(stats["trace_length"]["min"], 2)
        self.assertEqual(stats["trace_length"]["max"], 5)
        # P1 duration is 26 hours = 1.08 days
        p1_row = case_summary[case_summary["case_id"] == "P1"].iloc[0]
        self.assertAlmostEqual(p1_row["duration_hours"], 26.0, places=1)

if __name__ == "__main__":
    unittest.main()
