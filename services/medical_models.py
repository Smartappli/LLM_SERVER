from __future__ import annotations

import hashlib
import json
import socket
import tempfile
import time
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

HF_API_BASE = "https://huggingface.co/api/models"
HF_WEB_BASE = "https://huggingface.co"
DEFAULT_KEYWORDS = ["medical", "biomed", "biomedical", "clinical", "health"]
TRANSIENT_HTTP_CODES = {429, 500, 502, 503, 504}
DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_RETRIES = 3


def _validate_allowed_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ValueError(f"Unsupported URL scheme: {parsed.scheme}")
    if parsed.hostname not in {"huggingface.co", "www.huggingface.co"}:
        raise ValueError(f"Unsupported URL host: {parsed.hostname}")


def _safe_urlopen(request: Request, timeout: int):
    _validate_allowed_url(request.full_url)
    return urlopen(request, timeout=timeout)


def _request_json(url: str, token: str | None = None, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> list[dict] | dict:
    headers = {"User-Agent": "llm-server-medical-model-fetcher/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(url, headers=headers)
    with _safe_urlopen(request, timeout=timeout) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def _should_retry_http(code: int) -> bool:
    return code in TRANSIENT_HTTP_CODES


def _request_json_with_retry(
    url: str,
    token: str | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    retries: int = DEFAULT_RETRIES,
) -> list[dict] | dict:
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            return _request_json(url, token=token, timeout=timeout)
        except HTTPError as exc:
            last_exc = exc
            if _should_retry_http(exc.code) and attempt < retries - 1:
                time.sleep(2**attempt)
                continue
            raise
        except (URLError, TimeoutError, socket.timeout) as exc:
            last_exc = exc
            if attempt < retries - 1:
                time.sleep(2**attempt)
                continue
            raise

    if last_exc:
        raise RuntimeError(str(last_exc))
    raise RuntimeError("Unknown request failure")


def discover_models(
    keywords: Iterable[str],
    limit_per_keyword: int,
    token: str | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    retries: int = DEFAULT_RETRIES,
) -> dict[str, dict]:
    discovered: dict[str, dict] = {}

    for keyword in keywords:
        search = quote(keyword)
        url = f"{HF_API_BASE}?search={search}&full=true&limit={limit_per_keyword}"
        try:
            models = _request_json_with_retry(url, token=token, timeout=timeout, retries=retries)
        except (HTTPError, URLError, TimeoutError, socket.timeout):
            continue

        if not isinstance(models, list):
            continue

        for model in models:
            model_id = model.get("id")
            if isinstance(model_id, str):
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


def _build_request(url: str, token: str | None) -> Request:
    headers = {"User-Agent": "llm-server-medical-model-fetcher/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return Request(url, headers=headers)


def download_file(
    model_id: str,
    file_name: str,
    output_dir: Path,
    token: str | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    retries: int = DEFAULT_RETRIES,
) -> Path:
    model_dir = output_dir / model_id
    model_dir.mkdir(parents=True, exist_ok=True)
    destination = model_dir / file_name

    if destination.exists():
        return destination

    file_url = f"{HF_WEB_BASE}/{model_id}/resolve/main/{quote(file_name)}?download=true"

    for attempt in range(retries):
        temp_path = None
        try:
            request = _build_request(file_url, token)
            with _safe_urlopen(request, timeout=timeout) as response:
                expected_size = response.headers.get("Content-Length")

                hasher = hashlib.sha256()
                total_bytes = 0
                with tempfile.NamedTemporaryFile(delete=False, dir=model_dir, suffix=".part") as tmp_file:
                    temp_path = Path(tmp_file.name)
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        tmp_file.write(chunk)
                        hasher.update(chunk)
                        total_bytes += len(chunk)

                if total_bytes <= 0:
                    raise RuntimeError(f"Downloaded file is empty: {file_url}")
                if expected_size and int(expected_size) != total_bytes:
                    raise RuntimeError(
                        f"Downloaded size mismatch for {file_url}: expected {expected_size}, got {total_bytes}"
                    )

                temp_path.replace(destination)
                _ = hasher.hexdigest()
                return destination
        except HTTPError as exc:
            if _should_retry_http(exc.code) and attempt < retries - 1:
                time.sleep(2**attempt)
                continue
            raise
        except (URLError, TimeoutError, socket.timeout) as exc:
            if attempt < retries - 1:
                time.sleep(2**attempt)
                continue
            raise exc
        finally:
            if temp_path and temp_path.exists() and temp_path != destination:
                temp_path.unlink(missing_ok=True)

    raise RuntimeError(f"Could not download file after {retries} retries: {file_url}")


def generate_manifest(
    *,
    keywords: list[str],
    limit: int,
    token: str | None,
    all_files: bool,
    download: bool,
    output_dir: Path,
) -> list[dict[str, Any]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    discovered = discover_models(keywords, limit, token=token)

    manifest: list[dict[str, Any]] = []
    for model_id, model in sorted(discovered.items()):
        tags = model.get("tags", []) if isinstance(model.get("tags", []), list) else []
        if not is_medical_model(model_id, tags, keywords):
            continue

        gguf_files = extract_gguf_files(model)
        if not gguf_files:
            continue

        selected_files = gguf_files if all_files else pick_preferred_file(gguf_files)

        if download:
            for file_name in selected_files:
                download_file(model_id, file_name, output_dir, token=token)

        manifest.append(
            {
                "id": model_id,
                "downloads": model.get("downloads", 0),
                "likes": model.get("likes", 0),
                "gguf_files": gguf_files,
                "selected_files": selected_files,
            }
        )

    return manifest
