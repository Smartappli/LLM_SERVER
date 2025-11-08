ARG CUDA_IMAGE=13.0.2-devel-ubuntu24.04
FROM nvidia/cuda:${CUDA_IMAGE}

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0

WORKDIR /app

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        python3 python3-pip python3-dev \
        python3.12-venv \  # <<< IMPORTANT
        git build-essential \
        cmake ninja-build \
        gcc g++ wget \
        ocl-icd-opencl-dev opencl-headers clinfo \
        libclblast-dev libopenblas-dev \
    && mkdir -p /etc/OpenCL/vendors && \
    echo "libnvidia-opencl.so.1" > /etc/OpenCL/vendors/nvidia.icd && \
    rm -rf /var/lib/apt/lists/*

# Création du venv (maintenant possible)
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

# Copie du projet
COPY . .

# Vars pour la build CUDA
ENV CUDA_DOCKER_ARCH=all \
    GGML_CUDA=1 \
    FORCE_CMAKE=1 \
    CMAKE_ARGS="-DGGML_CUDA=on"

# Install deps Python dans le venv
RUN pip install --upgrade --no-cache-dir pip wheel && \
    pip install --no-cache-dir \
        pytest scikit-build setuptools \
        fastapi uvicorn sse-starlette \
        pydantic-settings starlette-context

# Install llama-cpp-python avec CUDA
RUN pip install --no-cache-dir "llama-cpp-python" --verbose

EXPOSE 8000

CMD ["python", "-m", "llama_cpp.server", "--config_file", "config-cuda.json"]
