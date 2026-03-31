#!/usr/bin/env python3
"""Discover and optionally download medical GGUF models from Hugging Face.

Compatibility target: llama-cpp-python (GGUF files).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from services.medical_models import DEFAULT_KEYWORDS, generate_manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Discover and optionally download Hugging Face medical GGUF models (llama-cpp-python compatible)."
    )
    parser.add_argument(
        "--keywords",
        nargs="+",
        default=DEFAULT_KEYWORDS,
        help="Keywords used to discover medical models.",
    )
    parser.add_argument(
        "--limit-per-keyword",
        type=int,
        default=100,
        help="Max models queried for each keyword.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("models"),
        help="Destination directory for downloads and manifest.",
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download matching GGUF files. If omitted, only discovery/manifest generation is performed.",
    )
    parser.add_argument(
        "--all-files",
        action="store_true",
        help="Download all GGUF files for each model. By default only one preferred file is downloaded.",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("HF_TOKEN"),
        help="Hugging Face token (or set HF_TOKEN env var).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        manifest = generate_manifest(
            keywords=args.keywords,
            limit=args.limit_per_keyword,
            token=args.token,
            all_files=args.all_files,
            download=args.download,
            output_dir=args.output_dir,
        )
    except (HTTPError, URLError, ValueError, OSError, RuntimeError) as exc:
        print(f"Error: {exc}")
        return 1

    for item in manifest:
        print(f"- {item['id']} ({len(item['gguf_files'])} GGUF)")
        for file_name in item["selected_files"]:
            print(f"  -> {file_name}")

    manifest_path = args.output_dir / "medical_gguf_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nManifest written: {manifest_path}")
    print(f"Medical GGUF models found: {len(manifest)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
