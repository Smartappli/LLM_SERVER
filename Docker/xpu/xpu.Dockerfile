ARG ONEAPI_IMAGE="latest"
FROM intel/oneapi-basekit:${ONEAPI_IMAGE}

# Serveur exposé hors container
ENV HOST=0.0.0.0
ENV PORT=8008

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
      python3 python3-venv python3-pip python3-dev \
      git build-essential cmake ninja-build pkg-config \
      libopenblas-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# Environnement Python isolé
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

# Dépendances Python
RUN pip install --upgrade --no-cache-dir pip wheel setuptools && \
    pip install --no-cache-dir \
      fastapi uvicorn sse-starlette \
      pydantic-settings starlette-context

# Build llama-cpp-python avec backend SYCL (XPU Intel)
ENV CMAKE_ARGS="-DGGML_SYCL=ON"
ENV GGML_SYCL=1
RUN pip install --no-cache-dir --verbose llama-cpp-python==0.3.19

EXPOSE 8008
CMD ["python3", "-m", "llama_cpp.server", "--config_file", "config-xpu.json"]
