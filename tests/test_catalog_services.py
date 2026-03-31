import os
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "medical_ui"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medical_ui.settings")

import django


django.setup()

from catalog.services import BASE_OUTPUT_ROOT, sanitize_output_dir


class TestSanitizeOutputDir(unittest.TestCase):
    def test_rejects_absolute_path(self):
        with self.assertRaises(ValueError):
            sanitize_output_dir("/tmp/outside")

    def test_rejects_parent_escape(self):
        with self.assertRaises(ValueError):
            sanitize_output_dir("../../etc")

    def test_accepts_relative_path_under_base(self):
        target = sanitize_output_dir("models/run_1")
        expected = (BASE_OUTPUT_ROOT / "models" / "run_1").resolve()
        self.assertEqual(target, expected)

    def test_accepts_default_models_directory(self):
        target = sanitize_output_dir("  ")
        expected = (BASE_OUTPUT_ROOT / "models").resolve()
        self.assertEqual(target, expected)


if __name__ == "__main__":
    unittest.main()
