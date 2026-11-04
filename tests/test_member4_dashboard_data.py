"""Unit tests for Member 4 Dashboard Data Loader and KPI Cards."""

import unittest
from pathlib import Path
import json
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_DIR = PROJECT_ROOT / "dashboard"

class TestMember4DashboardData(unittest.TestCase):
    """Test suite verifying Member 4 dashboard KPI aggregations and data files."""

    @classmethod
    def setUpClass(cls):
        cls.kpi_path = DASHBOARD_DIR / "dashboard_kpi_cards.csv"
        cls.archetype_path = DASHBOARD_DIR / "dashboard_archetype_metrics.csv"
        cls.summary_path = DASHBOARD_DIR / "dashboard_summary.json"

    def test_dashboard_files_exist(self):
        """Verify all dashboard export files exist."""
        self.assertTrue(self.kpi_path.exists(), f"Missing {self.kpi_path}")
        self.assertTrue(self.archetype_path.exists(), f"Missing {self.archetype_path}")
        self.assertTrue(self.summary_path.exists(), f"Missing {self.summary_path}")

    def test_kpi_cards_schema_and_metrics(self):
        """Verify headline KPI cards schema and non-empty metrics."""
        df = pd.read_csv(self.kpi_path)
        expected_cols = {"kpi_name", "metric_value", "category", "target_benchmark"}
        self.assertTrue(expected_cols.issubset(set(df.columns)), f"Columns mismatch: {df.columns}")
        self.assertGreaterEqual(len(df), 6, "Expected at least 6 executive KPI cards")

        kpi_names = set(df["kpi_name"])
        self.assertIn("Total Patient Encounters", kpi_names)
        self.assertIn("Total Clinical Transitions", kpi_names)
        self.assertIn("Unplanned ER Readmission Rate", kpi_names)

    def test_care_archetypes_breakdown(self):
        """Verify that all 3 clinical care archetypes sum up to 1,050 patients."""
        df = pd.read_csv(self.archetype_path)
        self.assertEqual(len(df), 3, "Expected 3 Care Archetypes")

        total_pts = df["patient_count"].sum()
        self.assertEqual(total_pts, 1050, f"Expected 1,050 patients, found {total_pts}")

        # Check positive stay durations
        self.assertTrue((df["median_stay_days"] >= 0).all())
        self.assertTrue((df["readmission_rate_pct"] >= 0).all())

    def test_summary_json_integrity(self):
        """Verify JSON summary integrity and author signature."""
        with open(self.summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)

        self.assertIn("headline_kpis", summary)
        self.assertIn("care_archetypes", summary)
        self.assertEqual(len(summary["care_archetypes"]), 3)

if __name__ == "__main__":
    unittest.main()
