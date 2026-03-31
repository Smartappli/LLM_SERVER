# LLM_SERVER

A production-ready **llama-cpp-python** server packaged with Docker images for multiple compute backends:

- **CPU** (OpenBLAS)
- **CUDA** (NVIDIA GPU)
- **XPU** (Intel SYCL, experimental)
- **ROCm** (AMD GPU, experimental)
- **Vulkan** (cross-vendor GPU, experimental)
- **OpenCL** (cross-vendor GPU, experimental)

This repository includes:

- prebuilt-oriented Dockerfiles for each backend;
- multi-model runtime configurations (`config-cpu.json`, `config-cuda.json`, `config-xpu.json`, `config-rocm.json`, `config-vulkan.json`, `config-opencl.json`);
- a configuration-structure validation test suite.

---

## 1) Prerequisites

### Common tools

- [Docker Desktop](https://www.docker.com/get-started/) (Windows/macOS) or Docker Engine (Linux)
- Git
- Python 3.10+ (for local tests)

### Windows-specific

- [Chocolatey](https://chocolatey.org/install)

Quick install (PowerShell/CMD as Administrator):

```bash
choco install git jq curl -y
```

### Ubuntu 24.04+

```bash
sudo apt update
sudo apt install -y wget jq git
```

---

## 2) Clone the repository

```bash
git clone https://github.com/Smartappli/LLM_SERVER.git
cd LLM_SERVER
```

---

## 3) Create the Docker volume for models

Run from the `Docker/` directory:

### Windows

```bash
cd Docker
create_docker_volume.bat
```

### Linux

```bash
cd Docker
chmod +x create_docker_volume.sh
./create_docker_volume.sh
```

---

## 4) Build Docker images

> Run the following commands from the `Docker/` directory.

### CPU image

```bash
cd cpu
docker build -t smartappli/llama-cpp-python-server-cpu:1.0 -f cpu.Dockerfile ..
```

### CUDA image (NVIDIA GPU)

```bash
cd ../cuda
docker build -t smartappli/llama-cpp-python-server-cuda:1.0 -f cuda.Dockerfile ..
```

### XPU image (Intel, experimental)

```bash
cd ../xpu
docker build -t smartappli/llama-cpp-python-server-xpu:1.0 -f xpu.Dockerfile ..
```

### ROCm image (AMD, experimental)

```bash
cd ../rocm
docker build -t smartappli/llama-cpp-python-server-rocm:1.0 -f rocm.Dockerfile ..
```

### Vulkan image (experimental)

```bash
cd ../vulkan
docker build -t smartappli/llama-cpp-python-server-vulkan:1.0 -f vulkan.Dockerfile ..
```

### OpenCL image (experimental)

```bash
cd ../opencl
docker build -t smartappli/llama-cpp-python-server-opencl:1.0 -f opencl.Dockerfile ..
```

---

## 5) Run the server

All containers mount the `LLM_SERVER` Docker volume to `/models`.

### Start CPU

```bash
docker run --rm -p 8008:8008 -v LLM_SERVER:/models smartappli/llama-cpp-python-server-cpu:1.0
```

### Start CUDA (NVIDIA GPU)

```bash
docker run --rm --gpus all -p 8008:8008 -v LLM_SERVER:/models smartappli/llama-cpp-python-server-cuda:1.0
```

### Start XPU (Intel, experimental)

```bash
docker run --rm -p 8008:8008 -v LLM_SERVER:/models smartappli/llama-cpp-python-server-xpu:1.0
```

### Start ROCm (AMD, experimental)

```bash
docker run --rm -p 8008:8008 -v LLM_SERVER:/models smartappli/llama-cpp-python-server-rocm:1.0
```

### Start Vulkan (experimental)

```bash
docker run --rm -p 8008:8008 -v LLM_SERVER:/models smartappli/llama-cpp-python-server-vulkan:1.0
```

### Start OpenCL (experimental)

```bash
docker run --rm -p 8008:8008 -v LLM_SERVER:/models smartappli/llama-cpp-python-server-opencl:1.0
```

OpenAI-compatible endpoint:

- `http://localhost:8008/v1`

---

## 6) Validate the project

### 6.1 Configuration unit tests

Run from repository root:

```bash
python -m unittest -v tests/test_configs.py
```

### 6.2 Request smoke test

`Docker/main.py` sends a request to the local server:

```bash
python Docker/main.py
```

> Ensure the server is already running at `http://localhost:8008/v1`.

---

## 7) Install local Python dependencies

```bash
pip install -r requirements.txt
```

---

## 8) Troubleshooting

- **Port already in use**: update `-p 8008:8008` (for example `-p 8010:8008`).
- **NVIDIA GPU not detected**: verify Docker setup + NVIDIA Container Toolkit, then test with `docker run --gpus all ...`.
- **Intel XPU not detected**: verify Intel GPU drivers on host and device access in Docker.
- **ROCm not detected**: verify AMD ROCm drivers on host and device permissions (`/dev/kfd`, `/dev/dri`).
- **Vulkan not detected**: verify host Vulkan stack (`vulkaninfo`) and GPU device access.
- **OpenCL not detected**: verify vendor OpenCL runtime and visibility using `clinfo`.
- **Models not found**: verify the `LLM_SERVER` volume contains the expected model files.

---

## 9) Useful project structure

- `Docker/cpu/cpu.Dockerfile`: CPU image
- `Docker/cuda/cuda.Dockerfile`: CUDA image
- `Docker/cpu/config-cpu.json`: CPU multi-model configuration
- `Docker/cuda/config-cuda.json`: CUDA multi-model configuration
- `Docker/xpu/xpu.Dockerfile`: Intel XPU image (experimental)
- `Docker/xpu/config-xpu.json`: XPU multi-model configuration
- `Docker/rocm/rocm.Dockerfile`: AMD ROCm image (experimental)
- `Docker/rocm/config-rocm.json`: ROCm multi-model configuration
- `Docker/vulkan/vulkan.Dockerfile`: Vulkan image (experimental)
- `Docker/vulkan/config-vulkan.json`: Vulkan multi-model configuration
- `Docker/opencl/opencl.Dockerfile`: OpenCL image (experimental)
- `Docker/opencl/config-opencl.json`: OpenCL multi-model configuration
- `tests/test_configs.py`: configuration unit tests
- `Docker/main.py`: request smoke-test script


## 10) Download medical Hugging Face models (GGUF / llama-cpp-python)

A helper script is available to discover medical GGUF models from Hugging Face and optionally download them:

```bash
python Docker/download_medical_models.py --output-dir models
```

Download selected files (preferred quantization per model):

```bash
python Docker/download_medical_models.py --download --output-dir models
```

Download **all** GGUF files for each discovered medical model:

```bash
python Docker/download_medical_models.py --download --all-files --output-dir models
```

> You can pass a Hugging Face token with `--token <HF_TOKEN>` or the `HF_TOKEN` environment variable for gated/private models.


## 11) Django 6 interface (no Bash required)

A web interface is available to discover and download medical GGUF models from Hugging Face:

```bash
python -m pip install -r requirements.txt
uv run --with-requirements requirements.txt granian --interface asgi --host 0.0.0.0 --port 8010 medical_ui.asgi:application --app-dir medical_ui
```

Open:

- `http://localhost:8010/` (served by ASGI/granian)

From the form you can:

- set medical keywords;
- choose search limit;
- enable/disable downloads;
- choose one preferred GGUF file or all files;
- provide a Hugging Face token for gated repositories.


Security-oriented Django settings are environment-driven:

```bash
export DJANGO_ENV=prod
export DJANGO_DEBUG=false
export DJANGO_SECRET_KEY="replace-with-a-long-random-secret"
export DJANGO_ALLOWED_HOSTS="your-domain.com,api.your-domain.com"
```

For local development, defaults remain developer-friendly (`DJANGO_ENV=dev`).
