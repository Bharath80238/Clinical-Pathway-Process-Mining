"""Unit tests for CareFlow Clinical Decision Support System (CDSS)."""

import unittest
from pathlib import Path
import json
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures" / "process_maps"

class TestClinicalDecisionSupport(unittest.TestCase):
    """Test suite verifying CDSS scoring logic, risk tier classifications, and reports."""

    @classmethod
    def setUpClass(cls):
        cls.csv_path = REPORTS_DIR / "clinical_decision_recommendations.csv"
        cls.json_path = REPORTS_DIR / "clinical_decision_rules.json"
        cls.chart_path = FIGURES_DIR / "clinical_decision_support_matrix.png"

    def test_cdss_csv_structure_and_coverage(self):
        """Verify recommendations CSV exists and covers all 1,050 patients."""
        self.assertTrue(self.csv_path.exists(), f"Missing {self.csv_path}")
        df = pd.read_csv(self.csv_path)

        self.assertEqual(len(df), 1050, f"Expected 1,050 patients, found {len(df)}")
        expected_columns = {
            "case_id",
            "age",
            "infection_suspected",
            "sirs_criteria",
            "organ_dysfunction",
            "repeat_lab_orders",
            "spes_score",
            "risk_tier",
            "recommended_action",
            "sla_target",
            "recommended_bed_allocation",
            "actual_icu_admission",
            "actual_ward_admission",
            "actual_readmission",
            "total_stay_days",
            "event_count",
        }
        self.assertTrue(expected_columns.issubset(set(df.columns)), f"Columns mismatch: {df.columns}")

    def test_spes_score_bounds_and_distribution(self):
        """Verify SPES scores lie strictly within [0, 10] with no NaNs."""
        df = pd.read_csv(self.csv_path)
        scores = df["spes_score"]

        self.assertFalse(scores.isna().any(), "Found NaN SPES scores")
        self.assertTrue((scores >= 0).all(), "Found negative SPES scores")
        self.assertTrue((scores <= 10).all(), "Found SPES scores > 10")
        self.assertGreater(scores.mean(), 0.0)

    def test_risk_tier_classification_logic(self):
        """Verify deterministic score thresholds mapping to risk tiers."""
        df = pd.read_csv(self.csv_path)
        for _, row in df.iterrows():
            score = row["spes_score"]
            tier = row["risk_tier"]

            if score <= 2:
                self.assertIn("Low Risk", tier)
                self.assertIn("ER Observation", row["recommended_bed_allocation"])
            elif score <= 5:
                self.assertIn("Moderate Risk", tier)
                self.assertIn("Normal Care", row["recommended_bed_allocation"])
            else:
                self.assertIn("Critical Risk", tier)
                self.assertIn("Intensive Care", row["recommended_bed_allocation"])

    def test_cdss_summary_json_integrity(self):
        """Verify summary JSON metrics match ground truth population."""
        self.assertTrue(self.json_path.exists(), f"Missing {self.json_path}")
        with open(self.json_path, "r", encoding="utf-8") as f:
            summary = json.load(f)

        self.assertEqual(summary["total_evaluated_patients"], 1050)
        dist = summary["risk_tier_distribution"]
        total_counted = sum(d["count"] for d in dist.values())
        self.assertEqual(total_counted, 1050, f"Expected 1,050 sum, got {total_counted}")
        self.assertGreater(summary["high_risk_escalation_cases"], 0)

    def test_chart_artifact(self):
        """Verify CDSS decision support matrix chart is generated and non-empty."""
        self.assertTrue(self.chart_path.exists(), f"Missing {self.chart_path}")
        file_size = self.chart_path.stat().st_size
        self.assertGreater(file_size, 10000, f"Chart file too small ({file_size} bytes)")

if __name__ == "__main__":
    unittest.main()
