import tempfile
from pathlib import Path
import unittest
from unittest import mock

from services import medical_models


class TestMedicalModelsService(unittest.TestCase):
    def test_extract_gguf_files(self):
        model = {
            "siblings": [
                {"rfilename": "a.Q4_K_M.gguf"},
                {"rfilename": "README.md"},
                {"rfilename": "b.Q8_0.GGUF"},
            ]
        }
        self.assertEqual(medical_models.extract_gguf_files(model), ["a.Q4_K_M.gguf", "b.Q8_0.GGUF"])

    def test_pick_preferred_file_priority(self):
        files = ["model.Q8_0.gguf", "model.Q4_K_M.gguf"]
        self.assertEqual(medical_models.pick_preferred_file(files), ["model.Q4_K_M.gguf"])

    def test_download_file_rejects_model_id_path_traversal(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError):
                medical_models.download_file(
                    model_id="../escape",
                    file_name="model.gguf",
                    output_dir=Path(tmpdir),
                    token=None,
                )

    def test_download_file_rejects_file_name_path_traversal(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError):
                medical_models.download_file(
                    model_id="org/model",
                    file_name="../escape.gguf",
                    output_dir=Path(tmpdir),
                    token=None,
                )

    @mock.patch("services.medical_models.discover_models")
    @mock.patch("services.medical_models.download_file")
    def test_generate_manifest_with_download(self, download_mock, discover_mock):
        discover_mock.return_value = {
            "org/model-a": {
                "tags": ["medical"],
                "downloads": 100,
                "likes": 10,
                "siblings": [{"rfilename": "model-a.Q4_K_M.gguf"}],
            },
            "org/model-b": {
                "tags": ["finance"],
                "siblings": [{"rfilename": "model-b.Q4_K_M.gguf"}],
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = medical_models.generate_manifest(
                keywords=["medical"],
                limit=50,
                token=None,
                all_files=False,
                download=True,
                output_dir=Path(tmpdir),
            )

        self.assertEqual(len(manifest), 1)
        self.assertEqual(manifest[0]["id"], "org/model-a")
        download_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
