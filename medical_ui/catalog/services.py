from __future__ import annotations

import importlib.util
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock
from typing import Any
from urllib.error import HTTPError, URLError

from django.conf import settings

BASE_OUTPUT_ROOT = settings.BASE_DIR / "model_downloads"
BASE_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)


@dataclass
class DiscoveryJob:
    job_id: str
    status: str = "queued"
    manifest: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None


JOBS: dict[str, DiscoveryJob] = {}
JOBS_LOCK = Lock()
EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="medical-discovery")


def _load_medical_script() -> Any:
    script_path = settings.BASE_DIR / "Docker" / "download_medical_models.py"
    spec = importlib.util.spec_from_file_location("medical_downloader", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sanitize_output_dir(user_value: str) -> Path:
    requested = Path(user_value.strip() or "models")
    if requested.is_absolute():
        raise ValueError("output_dir must be relative")

    resolved = (BASE_OUTPUT_ROOT / requested).resolve()
    base_resolved = BASE_OUTPUT_ROOT.resolve()
    if not str(resolved).startswith(str(base_resolved)):
        raise ValueError("output_dir must stay inside the allowed download directory")

    return resolved


def get_job(job_id: str) -> DiscoveryJob | None:
    with JOBS_LOCK:
        return JOBS.get(job_id)


def _run_discovery(job_id: str, *, keywords: list[str], limit: int, output_dir: Path, download: bool, all_files: bool, token: str | None) -> None:
    job = get_job(job_id)
    if job is None:
        return

    job.status = "running"

    try:
        module = _load_medical_script()
        output_dir.mkdir(parents=True, exist_ok=True)
        discovered = module.discover_models(keywords, limit, token=token)

        manifest: list[dict[str, Any]] = []
        for model_id, model in sorted(discovered.items()):
            tags = model.get("tags", []) if isinstance(model.get("tags", []), list) else []
            if not module.is_medical_model(model_id, tags, keywords):
                continue

            gguf_files = module.extract_gguf_files(model)
            if not gguf_files:
                continue

            selected_files = gguf_files if all_files else module.pick_preferred_file(gguf_files)

            if download:
                for file_name in selected_files:
                    module.download_file(model_id, file_name, output_dir, token=token)

            manifest.append(
                {
                    "id": model_id,
                    "downloads": model.get("downloads", 0),
                    "likes": model.get("likes", 0),
                    "selected_files": selected_files,
                }
            )

        job.manifest = manifest
        job.status = "done"
    except (HTTPError, URLError, ValueError, OSError, RuntimeError) as exc:
        job.status = "failed"
        job.error = str(exc)


def enqueue_discovery(*, keywords: list[str], limit: int, output_dir: str, download: bool, all_files: bool, token: str | None) -> DiscoveryJob:
    safe_output_dir = sanitize_output_dir(output_dir)

    job = DiscoveryJob(job_id=uuid.uuid4().hex)
    with JOBS_LOCK:
        JOBS[job.job_id] = job

    EXECUTOR.submit(
        _run_discovery,
        job.job_id,
        keywords=keywords,
        limit=limit,
        output_dir=safe_output_dir,
        download=download,
        all_files=all_files,
        token=token,
    )
    return job
