"""Unit tests for inter-ward patient transfer latency analyzer."""

import unittest
from pathlib import Path
import json
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures" / "process_maps"

class TestInterWardTransfers(unittest.TestCase):
    """Test suite verifying inter-ward transfer metrics, data integrity, and plots."""

    @classmethod
    def setUpClass(cls):
        cls.csv_path = REPORTS_DIR / "inter_ward_transfer_metrics.csv"
        cls.json_path = REPORTS_DIR / "inter_ward_transfers_summary.json"
        cls.chart_path = FIGURES_DIR / "inter_ward_transfer_delays.png"

    def test_transfer_metrics_csv_structure(self):
        """Verify CSV existence and required schema."""
        self.assertTrue(self.csv_path.exists(), f"Missing {self.csv_path}")
        df = pd.read_csv(self.csv_path)

        expected_columns = {
            "source_activity",
            "target_activity",
            "transfer_label",
            "transition_count",
            "median_duration_hours",
            "mean_duration_hours",
            "p25_duration_hours",
            "p75_duration_hours",
            "p90_duration_hours",
            "max_duration_hours",
        }
        self.assertTrue(expected_columns.issubset(set(df.columns)), f"Columns mismatch: {df.columns}")
        self.assertGreater(len(df), 0, "Transfer metrics CSV should not be empty")

    def test_transfer_latencies_non_negative(self):
        """Verify all durations and percentiles are non-negative."""
        df = pd.read_csv(self.csv_path)
        for col in ["median_duration_hours", "mean_duration_hours", "p25_duration_hours", "p75_duration_hours", "p90_duration_hours"]:
            self.assertTrue((df[col] >= 0.0).all(), f"Found negative values in {col}")

    def test_transfer_summary_json_integrity(self):
        """Verify summary JSON metrics match clinical cohort cohorts."""
        self.assertTrue(self.json_path.exists(), f"Missing {self.json_path}")
        with open(self.json_path, "r", encoding="utf-8") as f:
            summary = json.load(f)

        self.assertEqual(summary["total_evaluated_cases"], 1050)
        self.assertEqual(summary["ward_admission_cases"], 800)
        self.assertEqual(summary["ward_admission_pct"], 76.19)
        self.assertEqual(summary["icu_admission_cases"], 110)
        self.assertEqual(summary["icu_admission_pct"], 10.48)
        self.assertEqual(summary["multi_ward_transfer_cases"], 100)
        self.assertEqual(summary["multi_ward_transfer_pct"], 9.52)
        self.assertEqual(summary["total_readmission_cases"], 294)
        self.assertEqual(summary["readmission_rate_pct"], 28.0)

    def test_visualization_artifact(self):
        """Verify inter-ward transfer chart is generated and non-empty."""
        self.assertTrue(self.chart_path.exists(), f"Missing {self.chart_path}")
        file_size = self.chart_path.stat().st_size
        self.assertGreater(file_size, 10000, f"Chart file too small ({file_size} bytes)")

if __name__ == "__main__":
    unittest.main()
