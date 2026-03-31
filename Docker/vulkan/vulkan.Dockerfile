FROM ubuntu:24.04

ENV HOST=0.0.0.0
ENV PORT=8008

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
      python3 python3-venv python3-pip python3-dev \
      git build-essential cmake ninja-build pkg-config \
      libopenblas-dev \
      vulkan-tools libvulkan-dev glslc && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

RUN pip install --upgrade --no-cache-dir pip wheel setuptools && \
    pip install --no-cache-dir \
      fastapi uvicorn sse-starlette \
      pydantic-settings starlette-context

ENV CMAKE_ARGS="-DGGML_VULKAN=ON"
ENV GGML_VULKAN=1
RUN pip install --no-cache-dir --verbose "llama-cpp-python>=0.3.19,<0.4"

EXPOSE 8008
CMD ["python3", "-m", "llama_cpp.server", "--config_file", "config-vulkan.json"]
