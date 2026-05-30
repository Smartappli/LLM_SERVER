#!/usr/bin/env python3
"""Split a multi-run SARIF log into one SARIF file per run.

GitHub code scanning rejects SARIF uploads that contain multiple runs with the
same tool/category. This helper keeps shared metadata and writes each run to an
individual file with a deterministic, unique runAutomationDetails.id.
"""

from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip()).strip("-._")
    return slug or "run"


def tool_name(run: dict[str, Any], index: int) -> str:
    driver = run.get("tool", {}).get("driver", {})
    return str(driver.get("name") or driver.get("semanticVersion") or f"run-{index + 1}")


def split_sarif(input_path: Path, output_dir: Path, category_prefix: str) -> list[Path]:
    sarif = json.loads(input_path.read_text(encoding="utf-8"))
    runs = sarif.get("runs")
    if not isinstance(runs, list) or not runs:
        raise ValueError(f"{input_path} does not contain any SARIF runs")

    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for index, run in enumerate(runs):
        run_copy = deepcopy(run)
        category = f"{category_prefix}/{index + 1}-{slugify(tool_name(run_copy, index))}"
        run_copy["automationDetails"] = {**run_copy.get("automationDetails", {}), "id": category}

        output = {**sarif, "runs": [run_copy]}
        destination = output_dir / f"{index + 1:03d}-{slugify(tool_name(run_copy, index))}.sarif"
        destination.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written.append(destination)

    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="SARIF file to split")
    parser.add_argument("output_dir", type=Path, help="Directory where split SARIF files are written")
    parser.add_argument("--category-prefix", default="codacy", help="Prefix for generated runAutomationDetails.id values")
    args = parser.parse_args()

    written = split_sarif(args.input, args.output_dir, args.category_prefix)
    for path in written:
        print(path)


if __name__ == "__main__":
    main()
