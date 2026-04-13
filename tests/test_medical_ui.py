import os
import sys
from pathlib import Path
import unittest

try:
    import django
except ImportError:  # pragma: no cover
    django = None


@unittest.skipIf(django is None, "Django not installed")
class TestMedicalUi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        sys.path.insert(0, "medical_ui")
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medical_ui.settings")
        django.setup()

    def test_form_accepts_relative_output_dir(self):
        from catalog.forms import ModelDiscoveryForm

        form = ModelDiscoveryForm(
            data={
                "keywords": "medical",
                "limit_per_keyword": 10,
                "output_dir": "models",
                "download": False,
                "all_files": False,
            }
        )
        self.assertTrue(form.is_valid())

    def test_sanitize_output_dir_rejects_absolute_path(self):
        from catalog.services import sanitize_output_dir

        with self.assertRaises(ValueError):
            sanitize_output_dir(str(Path.home()))


if __name__ == "__main__":
    unittest.main()
