import json
from pathlib import Path
import unittest


CONFIG_PATHS = [
    Path("Docker/cpu/config-cpu.json"),
    Path("Docker/cuda/config-cuda.json"),
    Path("Docker/xpu/config-xpu.json"),
    Path("Docker/rocm/config-rocm.json"),
    Path("Docker/vulkan/config-vulkan.json"),
    Path("Docker/opencl/config-opencl.json"),
]

REQUIRED_MODEL_FIELDS = {
    "model": str,
    "model_alias": str,
    "chat_format": str,
    "n_gpu_layers": int,
    "offload_kqv": bool,
    "n_batch": int,
    "n_ctx": int,
}


class TestDockerConfigs(unittest.TestCase):
    def _load_config(self, config_path: Path) -> dict:
        self.assertTrue(config_path.exists(), f"Missing config file: {config_path}")

        with config_path.open("r", encoding="utf-8") as config_file:
            data = json.load(config_file)

        self.assertIn("host", data, f"Missing host in {config_path}")
        self.assertIsInstance(data["host"], str)
        self.assertNotEqual(data["host"].strip(), "")

        self.assertIn("port", data, f"Missing port in {config_path}")
        self.assertIsInstance(data["port"], int)
        self.assertGreater(data["port"], 0)

        self.assertIn("models", data)
        self.assertIsInstance(data["models"], list)
        self.assertGreater(len(data["models"]), 0, "models list should not be empty")

        return data

    def test_all_configs_have_valid_models(self):
        for config_path in CONFIG_PATHS:
            with self.subTest(config=str(config_path)):
                data = self._load_config(config_path)
                aliases = set()

                for model in data["models"]:
                    self.assertIsInstance(model, dict)

                    for field, expected_type in REQUIRED_MODEL_FIELDS.items():
                        self.assertIn(field, model, f"Missing field '{field}' in {config_path}")
                        self.assertIsInstance(
                            model[field],
                            expected_type,
                            f"Field '{field}' should be {expected_type.__name__} in {config_path}",
                        )

                    self.assertEqual(model["model"], model["model"].strip())
                    self.assertEqual(model["model_alias"], model["model_alias"].strip())
                    self.assertNotIn(" ", model["model"], f"Unexpected space in model path for {config_path}")
                    self.assertGreater(model["n_batch"], 0)
                    self.assertGreater(model["n_ctx"], 0)

                    alias = model["model_alias"]
                    self.assertNotIn(alias, aliases, f"Duplicate alias '{alias}' in {config_path}")
                    aliases.add(alias)


if __name__ == "__main__":
    unittest.main()
