ARG CUDA_IMAGE=13.0.2-devel-ubuntu24.04
FROM nvidia/cuda:${CUDA_IMAGE}

# Variables d'environnement de base
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0

# Répertoire de travail
WORKDIR /app

# Dépendances système
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        git build-essential \
        python3 python3-pip python3-venv \
        gcc wget \
        ocl-icd-opencl-dev opencl-headers clinfo \
        libclblast-dev libopenblas-dev \
    && mkdir -p /etc/OpenCL/vendors \
    && echo "libnvidia-opencl.so.1" > /etc/OpenCL/vendors/nvidia.icd \
    && rm -rf /var/lib/apt/lists/*

# Copie du code
COPY . .

# Variables pour la build CUDA de llama-cpp
ENV CUDA_DOCKER_ARCH=all \
    GGML_CUDA=1 \
    CMAKE_ARGS="-DGGML_CUDA=on" \
    FORCE_CMAKE=1

# Installation des dépendances Python
RUN python3 -m pip install --upgrade --no-cache-dir pip && \
    pip install --no-cache-dir \
        pytest cmake scikit-build setuptools \
        fastapi uvicorn sse-starlette \
        pydantic-settings starlette-context && \
    pip install --no-cache-dir llama-cpp-python

# Port du serveur (optionnel mais pratique pour la doc)
EXPOSE 8000

# Démarrage du serveur llama-cpp
CMD ["python3", "-m", "llama_cpp.server", "--config_file", "config-cuda.json"]
