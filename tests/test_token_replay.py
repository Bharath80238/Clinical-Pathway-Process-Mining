"""Unit tests for token-based replay simulation and Petri net conformance."""

import unittest
from pathlib import Path
import json
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures" / "process_maps"

class TestTokenReplay(unittest.TestCase):
    """Test suite verifying token-based replay metrics and invariants."""

    @classmethod
    def setUpClass(cls):
        cls.csv_path = REPORTS_DIR / "token_replay_case_fitness.csv"
        cls.json_path = REPORTS_DIR / "token_replay_summary.json"
        cls.chart_path = FIGURES_DIR / "token_fitness_distribution.png"

    def test_case_fitness_csv_structure(self):
        """Verify per-case token fitness CSV existence, row count, and schema."""
        self.assertTrue(self.csv_path.exists(), f"Missing {self.csv_path}")
        df = pd.read_csv(self.csv_path)

        # 1,050 patient cases in sepsis event log
        self.assertEqual(len(df), 1050, f"Expected 1050 cases, got {len(df)}")

        expected_columns = {
            "case_id",
            "trace_fitness",
            "trace_is_fit",
            "produced_tokens",
            "consumed_tokens",
            "missing_tokens",
            "remaining_tokens",
        }
        self.assertTrue(expected_columns.issubset(set(df.columns)), f"Columns mismatch: {df.columns}")

    def test_case_fitness_bounds(self):
        """Verify all trace fitness scores lie strictly in [0.0, 1.0]."""
        df = pd.read_csv(self.csv_path)
        fitness = df["trace_fitness"]

        self.assertTrue((fitness >= 0.0).all(), "Found negative fitness values")
        self.assertTrue((fitness <= 1.0).all(), "Found fitness values > 1.0")
        self.assertFalse(fitness.isna().any(), "Found NaN fitness values")

    def test_token_conservation_accounting(self):
        """Verify token production, consumption, and conservation invariants."""
        df = pd.read_csv(self.csv_path)

        # In a fully sound and fitting model, produced tokens equal consumed tokens
        total_p = df["produced_tokens"].sum()
        total_c = df["consumed_tokens"].sum()
        total_m = df["missing_tokens"].sum()
        total_r = df["remaining_tokens"].sum()

        self.assertGreater(total_p, 0, "Produced tokens must be positive")
        self.assertEqual(total_p, total_c, f"Produced {total_p} does not match Consumed {total_c}")
        self.assertEqual(total_m, 0, f"Expected 0 missing tokens, got {total_m}")
        self.assertEqual(total_r, 0, f"Expected 0 remaining tokens, got {total_r}")

    def test_summary_json_integrity(self):
        """Verify summary JSON metrics match case-level aggregations."""
        self.assertTrue(self.json_path.exists(), f"Missing {self.json_path}")
        with open(self.json_path, "r", encoding="utf-8") as f:
            summary = json.load(f)

        self.assertEqual(summary["total_evaluated_traces"], 1050)
        self.assertEqual(summary["perfectly_fit_traces"], 1050)
        self.assertEqual(summary["perfectly_fit_share_pct"], 100.0)
        self.assertAlmostEqual(summary["mean_trace_fitness"], 1.0, places=4)
        self.assertEqual(summary["total_missing_tokens"], 0)
        self.assertEqual(summary["total_remaining_tokens"], 0)

    def test_visualization_artifact(self):
        """Verify diagnostic token fitness chart is generated and non-empty."""
        self.assertTrue(self.chart_path.exists(), f"Missing {self.chart_path}")
        file_size = self.chart_path.stat().st_size
        self.assertGreater(file_size, 10000, f"Chart file too small ({file_size} bytes)")

if __name__ == "__main__":
    unittest.main()
