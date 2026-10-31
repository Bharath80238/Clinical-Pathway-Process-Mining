"""Unit tests for Readmission Risk Factor and Clinical Root-Cause Mining."""

import unittest
from pathlib import Path
import json
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures" / "process_maps"

class TestReadmissionRisk(unittest.TestCase):
    """Test suite verifying readmission risk metrics, odds ratios, and diagnostic charts."""

    @classmethod
    def setUpClass(cls):
        cls.csv_path = REPORTS_DIR / "readmission_risk_factors.csv"
        cls.json_path = REPORTS_DIR / "readmission_risk_summary.json"
        cls.chart_path = FIGURES_DIR / "readmission_risk_factors.png"

    def test_csv_structure_and_predictors(self):
        """Verify CSV exists and contains required statistical predictor columns."""
        self.assertTrue(self.csv_path.exists(), f"Missing {self.csv_path}")
        df = pd.read_csv(self.csv_path)

        expected_columns = {
            "predictor_feature",
            "predictor_name",
            "clinical_category",
            "exposed_count",
            "exposed_prevalence_pct",
            "readmissions_exposed",
            "readmission_rate_exposed_pct",
            "unexposed_count",
            "readmissions_unexposed",
            "readmission_rate_unexposed_pct",
            "relative_risk",
            "risk_difference_pct",
            "odds_ratio",
            "ci_95_lower",
            "ci_95_upper",
        }
        self.assertTrue(expected_columns.issubset(set(df.columns)), f"Columns mismatch: {df.columns}")
        self.assertGreaterEqual(len(df), 5, "Expected at least 5 clinical predictors")

    def test_baseline_readmission_integrity(self):
        """Verify baseline readmissions match hospital ground truth (294 / 1050 = 28.0%)."""
        self.assertTrue(self.json_path.exists(), f"Missing {self.json_path}")
        with open(self.json_path, "r", encoding="utf-8") as f:
            summary = json.load(f)

        self.assertEqual(summary["total_cohort_patients"], 1050)
        self.assertEqual(summary["total_readmission_cases"], 294)
        self.assertEqual(summary["baseline_readmission_rate_pct"], 28.0)
        self.assertGreater(summary["primary_odds_ratio"], 1.0)

    def test_odds_ratio_bounds_and_confidence_intervals(self):
        """Verify all odds ratios are positive and bounded by 95% confidence intervals."""
        df = pd.read_csv(self.csv_path)
        for _, row in df.iterrows():
            or_val = row["odds_ratio"]
            ci_low = row["ci_95_lower"]
            ci_high = row["ci_95_upper"]

            self.assertGreater(or_val, 0.0, f"Odds ratio should be positive for {row['predictor_name']}")
            self.assertLessEqual(ci_low, or_val, f"ci_lower > odds_ratio for {row['predictor_name']}")
            self.assertLessEqual(or_val, ci_high, f"odds_ratio > ci_upper for {row['predictor_name']}")

    def test_readmission_rate_bounds(self):
        """Verify all exposed and unexposed readmission percentages lie in [0.0, 100.0]."""
        df = pd.read_csv(self.csv_path)
        exp_rates = df["readmission_rate_exposed_pct"]
        unexp_rates = df["readmission_rate_unexposed_pct"]

        self.assertTrue((exp_rates >= 0.0).all())
        self.assertTrue((exp_rates <= 100.0).all())
        self.assertTrue((unexp_rates >= 0.0).all())
        self.assertTrue((unexp_rates <= 100.0).all())

    def test_visualization_artifact(self):
        """Verify readmission risk factor chart is generated and non-empty."""
        self.assertTrue(self.chart_path.exists(), f"Missing {self.chart_path}")
        file_size = self.chart_path.stat().st_size
        self.assertGreater(file_size, 10000, f"Chart file too small ({file_size} bytes)")

if __name__ == "__main__":
    unittest.main()
