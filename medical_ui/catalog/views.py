from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .forms import ModelDiscoveryForm


def _load_medical_script() -> Any:
    script_path = Path(__file__).resolve().parents[2] / "Docker" / "download_medical_models.py"
    spec = importlib.util.spec_from_file_location("medical_downloader", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def index(request: HttpRequest) -> HttpResponse:
    manifest = []
    error = None
    form = ModelDiscoveryForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        module = _load_medical_script()
        keywords = form.cleaned_data["keywords"].split()
        limit = form.cleaned_data["limit_per_keyword"]
        output_dir = Path(form.cleaned_data["output_dir"])
        download = form.cleaned_data["download"]
        all_files = form.cleaned_data["all_files"]
        token = form.cleaned_data.get("token") or None

        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            discovered = module.discover_models(keywords, limit, token=token)

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
        except Exception as exc:  # noqa: BLE001 - surface UI error cleanly
            error = str(exc)

    context = {
        "form": form,
        "manifest": manifest,
        "error": error,
    }
    return render(request, "catalog/index.html", context)
