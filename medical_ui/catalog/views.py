from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .forms import ModelDiscoveryForm
from .services import enqueue_discovery, get_job


def index(request: HttpRequest) -> HttpResponse:
    form = ModelDiscoveryForm(request.POST or None)
    error = None
    manifest = []
    job_status = None
    job_id = request.GET.get("job")

    if request.method == "POST" and form.is_valid():
        keywords = form.cleaned_data["keywords"].split()
        limit = form.cleaned_data["limit_per_keyword"]
        output_dir = form.cleaned_data["output_dir"]
        download = form.cleaned_data["download"]
        all_files = form.cleaned_data["all_files"]
        token = form.cleaned_data.get("token") or None

        try:
            job = enqueue_discovery(
                keywords=keywords,
                limit=limit,
                output_dir=output_dir,
                download=download,
                all_files=all_files,
                token=token,
            )
            return redirect(f"/?job={job.job_id}")
        except ValueError as exc:
            error = str(exc)

    if job_id:
        job = get_job(job_id)
        if job is None:
            error = "Unknown job id"
        else:
            job_status = job.status
            manifest = job.manifest
            if job.error:
                error = job.error

    context = {
        "form": form,
        "manifest": manifest,
        "error": error,
        "job_id": job_id,
        "job_status": job_status,
    }
    return render(request, "catalog/index.html", context)
