import json
from pathlib import Path
import unittest


class TestDockerConfigs(unittest.TestCase):
    def _load_config(self, path: str):
        config_path = Path(path)
        self.assertTrue(config_path.exists(), f"Missing config file: {path}")

        with config_path.open("r", encoding="utf-8") as config_file:
            data = json.load(config_file)

        self.assertIn("models", data)
        self.assertIsInstance(data["models"], list)
        self.assertGreater(len(data["models"]), 0, "models list should not be empty")

        for model in data["models"]:
            self.assertIsInstance(model, dict)
            self.assertIn("model_alias", model)
            self.assertIsInstance(model["model_alias"], str)
            self.assertNotEqual(model["model_alias"].strip(), "")

    def test_cpu_config_has_models(self):
        self._load_config("Docker/cpu/config-cpu.json")

    def test_cuda_config_has_models(self):
        self._load_config("Docker/cuda/config-cuda.json")


if __name__ == "__main__":
    unittest.main()
