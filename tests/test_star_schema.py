"""Unit tests for CareFlow Dimensional Star-Schema Data Warehouse Model."""

import unittest
from pathlib import Path
import json
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
STAR_DIR = REPORTS_DIR / "star_schema"
FIGURES_DIR = REPORTS_DIR / "figures" / "process_maps"

class TestStarSchema(unittest.TestCase):
    """Test suite verifying dimensional star-schema data integrity and referential constraints."""

    @classmethod
    def setUpClass(cls):
        cls.fact_path = STAR_DIR / "fact_clinical_events.csv"
        cls.dim_patient_path = STAR_DIR / "dim_patient_cohort.csv"
        cls.dim_act_path = STAR_DIR / "dim_activity.csv"
        cls.dim_dept_path = STAR_DIR / "dim_department.csv"
        cls.dim_time_path = STAR_DIR / "dim_time_bucket.csv"
        cls.json_path = REPORTS_DIR / "star_schema_summary.json"
        cls.diagram_path = FIGURES_DIR / "star_schema_entity_relationship.png"

    def test_star_schema_tables_exist(self):
        """Verify existence of fact and all four dimension table files."""
        self.assertTrue(self.fact_path.exists(), f"Missing {self.fact_path}")
        self.assertTrue(self.dim_patient_path.exists(), f"Missing {self.dim_patient_path}")
        self.assertTrue(self.dim_act_path.exists(), f"Missing {self.dim_act_path}")
        self.assertTrue(self.dim_dept_path.exists(), f"Missing {self.dim_dept_path}")
        self.assertTrue(self.dim_time_path.exists(), f"Missing {self.dim_time_path}")
        self.assertTrue(self.json_path.exists(), f"Missing {self.json_path}")

    def test_row_counts_and_completeness(self):
        """Verify row counts match full clinical population."""
        fact_df = pd.read_csv(self.fact_path)
        pat_df = pd.read_csv(self.dim_patient_path)
        act_df = pd.read_csv(self.dim_act_path)
        dept_df = pd.read_csv(self.dim_dept_path)
        time_df = pd.read_csv(self.dim_time_path)

        self.assertEqual(len(fact_df), 15213, "Fact table should contain 15,213 events")
        self.assertEqual(len(pat_df), 1050, "Patient cohort dim should contain 1,050 cases")
        self.assertEqual(len(act_df), 16, "Activity dim should contain 16 unique clinical activities")
        self.assertEqual(len(dept_df), 26, "Department dim should contain 26 organizational groups")
        self.assertEqual(len(time_df), 5, "Time bucket dim should contain 5 SLA tiers")

    def test_referential_integrity(self):
        """Verify 100% foreign key referential integrity with zero orphaned keys."""
        fact_df = pd.read_csv(self.fact_path)
        pat_df = pd.read_csv(self.dim_patient_path)
        act_df = pd.read_csv(self.dim_act_path)
        dept_df = pd.read_csv(self.dim_dept_path)
        time_df = pd.read_csv(self.dim_time_path)

        # Foreign Key check: patient_cohort_key
        valid_pat_keys = set(pat_df["patient_cohort_key"])
        fact_pat_keys = set(fact_df["patient_cohort_key"])
        self.assertTrue(fact_pat_keys.issubset(valid_pat_keys), "Found orphaned patient_cohort_key in fact")

        # Foreign Key check: activity_key
        valid_act_keys = set(act_df["activity_key"])
        fact_act_keys = set(fact_df["activity_key"])
        self.assertTrue(fact_act_keys.issubset(valid_act_keys), "Found orphaned activity_key in fact")

        # Foreign Key check: department_key
        valid_dept_keys = set(dept_df["department_key"])
        fact_dept_keys = set(fact_df["department_key"])
        self.assertTrue(fact_dept_keys.issubset(valid_dept_keys), "Found orphaned department_key in fact")

        # Foreign Key check: time_bucket_key
        valid_time_keys = set(time_df["time_bucket_key"])
        fact_time_keys = set(fact_df["time_bucket_key"])
        self.assertTrue(fact_time_keys.issubset(valid_time_keys), "Found orphaned time_bucket_key in fact")

    def test_fact_surrogate_key_uniqueness(self):
        """Verify event_surrogate_key is strictly unique and non-null."""
        fact_df = pd.read_csv(self.fact_path)
        keys = fact_df["event_surrogate_key"]
        self.assertFalse(keys.isna().any(), "Found NaN surrogate keys in fact table")
        self.assertEqual(len(keys), len(keys.unique()), "Found duplicate surrogate keys in fact table")

    def test_architecture_diagram_artifact(self):
        """Verify star-schema entity relationship diagram exists and is non-empty."""
        self.assertTrue(self.diagram_path.exists(), f"Missing {self.diagram_path}")
        file_size = self.diagram_path.stat().st_size
        self.assertGreater(file_size, 10000, f"Architecture diagram too small ({file_size} bytes)")

if __name__ == "__main__":
    unittest.main()
