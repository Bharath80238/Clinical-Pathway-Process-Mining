"""Unit tests for CareFlow Final Defense Presentation Readiness and Slide Artifacts."""

import unittest
from pathlib import Path
import json
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures" / "process_maps"

class TestPresentationReadiness(unittest.TestCase):
    """Test suite verifying final presentation KPIs, slide schema, and visual artifacts."""

    @classmethod
    def setUpClass(cls):
        cls.json_path = REPORTS_DIR / "final_defense_slide_kpis.json"
        cls.csv_path = REPORTS_DIR / "final_defense_metrics_table.csv"
        cls.roadmap_path = FIGURES_DIR / "careflow_executive_milestone_roadmap.png"
        cls.guide_path = REPORTS_DIR / "final_defense_presentation_guide.md"

    def test_slide_artifacts_exist(self):
        """Verify existence of JSON slide bundle, CSV table, roadmap chart, and presentation guide."""
        self.assertTrue(self.json_path.exists(), f"Missing {self.json_path}")
        self.assertTrue(self.csv_path.exists(), f"Missing {self.csv_path}")
        self.assertTrue(self.roadmap_path.exists(), f"Missing {self.roadmap_path}")
        self.assertTrue(self.guide_path.exists(), f"Missing {self.guide_path}")

    def test_slide_kpis_json_structure(self):
        """Verify presentation JSON bundle contains exactly 6 structured slides."""
        with open(self.json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["total_slides"], 6)
        self.assertEqual(len(data["slides"]), 6)

        for s in data["slides"]:
            self.assertIn("slide_number", s)
            self.assertIn("slide_title", s)
            self.assertIn("key_takeaway", s)
            self.assertIn("metrics", s)
            self.assertEqual(len(s["metrics"]), 4, f"Slide {s['slide_number']} should have 4 metrics")

    def test_metrics_table_csv_completeness(self):
        """Verify flat metrics CSV contains all 24 quantitative metrics across 6 slides."""
        df = pd.read_csv(self.csv_path)
        self.assertEqual(len(df), 24, "Expected 24 metric rows (6 slides * 4 metrics)")

        expected_columns = {"slide_number", "slide_title", "key_takeaway", "metric_name", "metric_value", "visual_artifact"}
        self.assertTrue(expected_columns.issubset(set(df.columns)), f"Columns mismatch: {df.columns}")

    def test_roadmap_visual_artifact(self):
        """Verify CareFlow executive milestone roadmap diagram exists and is non-empty."""
        self.assertTrue(self.roadmap_path.exists(), f"Missing {self.roadmap_path}")
        file_size = self.roadmap_path.stat().st_size
        self.assertGreater(file_size, 10000, f"Roadmap chart too small ({file_size} bytes)")

if __name__ == "__main__":
    unittest.main()
