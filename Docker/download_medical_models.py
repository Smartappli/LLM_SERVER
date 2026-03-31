#!/usr/bin/env python3
"""Discover and optionally download medical GGUF models from Hugging Face.

Compatibility target: llama-cpp-python (GGUF files).
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Iterable
from urllib.parse import quote
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

HF_API_BASE = "https://huggingface.co/api/models"
HF_WEB_BASE = "https://huggingface.co"
DEFAULT_KEYWORDS = ["medical", "biomed", "biomedical", "clinical", "health"]


def _request_json(url: str, token: str | None = None) -> list[dict] | dict:
    headers = {"User-Agent": "llm-server-medical-model-fetcher/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(url, headers=headers)
    with urlopen(request) as response:  # noqa: S310 - controlled URL constant
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def discover_models(keywords: Iterable[str], limit_per_keyword: int, token: str | None = None) -> dict[str, dict]:
    discovered: dict[str, dict] = {}

    for keyword in keywords:
        search = quote(keyword)
        url = f"{HF_API_BASE}?search={search}&full=true&limit={limit_per_keyword}"
        try:
            models = _request_json(url, token=token)
        except (HTTPError, URLError) as exc:
            print(f"Warning: could not query keyword '{keyword}': {exc}")
            continue

        if not isinstance(models, list):
            continue

        for model in models:
            model_id = model.get("id")
            if not isinstance(model_id, str):
                continue

            discovered[model_id] = model

    return discovered


def extract_gguf_files(model: dict) -> list[str]:
    siblings = model.get("siblings", [])
    if not isinstance(siblings, list):
        return []

    gguf_files = []
    for sibling in siblings:
        if not isinstance(sibling, dict):
            continue
        file_name = sibling.get("rfilename")
        if isinstance(file_name, str) and file_name.lower().endswith(".gguf"):
            gguf_files.append(file_name)

    return sorted(gguf_files)


def is_medical_model(model_id: str, tags: Iterable[str], keywords: Iterable[str]) -> bool:
    haystack = f"{model_id} {' '.join(tags)}".lower()
    return any(keyword.lower() in haystack for keyword in keywords)


def download_file(model_id: str, file_name: str, output_dir: Path, token: str | None = None) -> Path:
    model_dir = output_dir / model_id
    model_dir.mkdir(parents=True, exist_ok=True)
    destination = model_dir / file_name

    if destination.exists():
        return destination

    file_url = f"{HF_WEB_BASE}/{model_id}/resolve/main/{quote(file_name)}?download=true"
    headers = {"User-Agent": "llm-server-medical-model-fetcher/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(file_url, headers=headers)
    with urlopen(request) as response:  # noqa: S310 - controlled URL constant
        destination.write_bytes(response.read())

    return destination


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


def pick_preferred_file(files: list[str]) -> list[str]:
    if not files:
        return []

    priorities = ["q4_k_m", "q4_k_s", "q5_k_m", "q8_0", "f16"]
    lowered = {name.lower(): name for name in files}
    for p in priorities:
        for lower_name, original in lowered.items():
            if p in lower_name:
                return [original]

    return [files[0]]


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    discovered = discover_models(args.keywords, args.limit_per_keyword, token=args.token)

    manifest: list[dict] = []
    for model_id, model in sorted(discovered.items()):
        tags = model.get("tags", [])
        if not isinstance(tags, list):
            tags = []

        if not is_medical_model(model_id, tags, args.keywords):
            continue

        gguf_files = extract_gguf_files(model)
        if not gguf_files:
            continue

        selected_files = gguf_files if args.all_files else pick_preferred_file(gguf_files)

        item = {
            "id": model_id,
            "downloads": model.get("downloads", 0),
            "likes": model.get("likes", 0),
            "gguf_files": gguf_files,
            "selected_files": selected_files,
        }
        manifest.append(item)

        print(f"- {model_id} ({len(gguf_files)} GGUF)")
        for file_name in selected_files:
            print(f"  -> {file_name}")
            if args.download:
                try:
                    destination = download_file(model_id, file_name, args.output_dir, token=args.token)
                    print(f"     downloaded: {destination}")
                except (HTTPError, URLError) as exc:
                    print(f"     warning: failed download ({exc})")

    manifest_path = args.output_dir / "medical_gguf_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nManifest written: {manifest_path}")
    print(f"Medical GGUF models found: {len(manifest)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
