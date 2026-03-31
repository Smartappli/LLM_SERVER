from __future__ import annotations

import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock
from typing import Any
from urllib.error import HTTPError, URLError

from django.conf import settings

from services.medical_models import generate_manifest

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


def sanitize_output_dir(user_value: str) -> Path:
    requested = Path(user_value.strip() or "models")
    if requested.is_absolute():
        raise ValueError("output_dir must be relative")

    resolved = (BASE_OUTPUT_ROOT / requested).resolve()
    base_resolved = BASE_OUTPUT_ROOT.resolve()

    try:
        resolved.relative_to(base_resolved)
    except ValueError as exc:
        raise ValueError("output_dir must stay inside the allowed download directory") from exc

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
        manifest = generate_manifest(
            keywords=keywords,
            limit=limit,
            token=token,
            all_files=all_files,
            download=download,
            output_dir=output_dir,
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
