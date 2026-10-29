"""Unit tests for Diagnostic Turnaround Time (TAT) and lab queueing analyzer."""

import unittest
from pathlib import Path
import json
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures" / "process_maps"

class TestDiagnosticTurnaround(unittest.TestCase):
    """Test suite verifying diagnostic turnaround metrics, SLA compliance, and charts."""

    @classmethod
    def setUpClass(cls):
        cls.csv_path = REPORTS_DIR / "diagnostic_turnaround_metrics.csv"
        cls.json_path = REPORTS_DIR / "diagnostic_turnaround_summary.json"
        cls.chart_path = FIGURES_DIR / "diagnostic_turnaround_distribution.png"

    def test_csv_structure_and_assays(self):
        """Verify CSV exists and contains CRP, LacticAcid, and Leucocytes."""
        self.assertTrue(self.csv_path.exists(), f"Missing {self.csv_path}")
        df = pd.read_csv(self.csv_path)

        expected_assays = {"CRP", "LacticAcid", "Leucocytes"}
        self.assertEqual(set(df["assay"]), expected_assays, "Assay mismatch")

        expected_columns = {
            "assay",
            "total_tested_cases",
            "total_test_events",
            "cases_with_repetition",
            "repetition_rate_pct",
            "median_tat_minutes",
            "mean_tat_minutes",
            "p25_tat_minutes",
            "p75_tat_minutes",
            "p90_tat_minutes",
            "iqr_tat_minutes",
            "pct_within_30min",
            "pct_within_60min",
            "pct_within_120min",
        }
        self.assertTrue(expected_columns.issubset(set(df.columns)), f"Columns mismatch: {df.columns}")

    def test_tat_percentile_monotonicity(self):
        """Verify p25 <= median <= p75 <= p90 and all TAT values are strictly positive."""
        df = pd.read_csv(self.csv_path)
        for _, row in df.iterrows():
            p25 = row["p25_tat_minutes"]
            median = row["median_tat_minutes"]
            p75 = row["p75_tat_minutes"]
            p90 = row["p90_tat_minutes"]

            self.assertGreater(p25, 0, f"p25 should be positive for {row['assay']}")
            self.assertLessEqual(p25, median, f"p25 > median for {row['assay']}")
            self.assertLessEqual(median, p75, f"median > p75 for {row['assay']}")
            self.assertLessEqual(p75, p90, f"p75 > p90 for {row['assay']}")

    def test_sla_compliance_monotonicity_and_bounds(self):
        """Verify pct_30m <= pct_60m <= pct_120m <= 100.0%."""
        df = pd.read_csv(self.csv_path)
        for _, row in df.iterrows():
            p30 = row["pct_within_30min"]
            p60 = row["pct_within_60min"]
            p120 = row["pct_within_120min"]

            self.assertGreaterEqual(p30, 0.0)
            self.assertLessEqual(p30, p60, f"30m SLA compliance greater than 60m for {row['assay']}")
            self.assertLessEqual(p60, p120, f"60m SLA compliance greater than 120m for {row['assay']}")
            self.assertLessEqual(p120, 100.0)

    def test_repetition_rate_bounds(self):
        """Verify repetition rates are within [0.0, 100.0]."""
        df = pd.read_csv(self.csv_path)
        rates = df["repetition_rate_pct"]
        self.assertTrue((rates >= 0.0).all())
        self.assertTrue((rates <= 100.0).all())

    def test_summary_json_integrity(self):
        """Verify summary JSON metrics match database ground truth."""
        self.assertTrue(self.json_path.exists(), f"Missing {self.json_path}")
        with open(self.json_path, "r", encoding="utf-8") as f:
            summary = json.load(f)

        self.assertEqual(summary["total_cohort_cases"], 1050)
        self.assertGreater(summary["total_laboratory_events"], 8000)
        self.assertGreater(summary["laboratory_share_of_all_events_pct"], 50.0)
        self.assertEqual(len(summary["assay_metrics"]), 3)

    def test_visualization_artifact(self):
        """Verify diagnostic turnaround chart is generated and non-empty."""
        self.assertTrue(self.chart_path.exists(), f"Missing {self.chart_path}")
        file_size = self.chart_path.stat().st_size
        self.assertGreater(file_size, 10000, f"Chart file too small ({file_size} bytes)")

if __name__ == "__main__":
    unittest.main()
