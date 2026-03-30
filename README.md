# LLM_SERVER

Serveur **llama-cpp-python** empaqueté en Docker avec deux variantes :
- **CPU** (OpenBLAS)
- **GPU** (CUDA)
- **XPU** (Intel SYCL, expérimental)
- **ROCm** (AMD GPU, expérimental)
- **Vulkan** (multi-vendeur GPU, expérimental)
- **OpenCL** (multi-vendeur GPU, expérimental)

Le projet fournit :
- des images Docker prêtes à l’emploi ;
- des configurations multi-modèles (`config-cpu.json`, `config-cuda.json`, `config-xpu.json`, `config-rocm.json`, `config-vulkan.json`, `config-opencl.json`) ;
- un test de validation de structure des fichiers de config.

---

## 1) Prérequis

### Outils communs
- [Docker Desktop](https://www.docker.com/get-started/) (Windows/macOS) ou Docker Engine (Linux)
- Git
- Python 3.10+ (pour lancer les tests locaux)

### Spécifique Windows
- [Chocolatey](https://chocolatey.org/install)

Installation rapide (PowerShell/CMD administrateur) :

```bash
choco install git jq curl -y
```

### Spécifique Ubuntu 24.04+

```bash
sudo apt update
sudo apt install -y wget jq git
```

---

## 2) Cloner le dépôt

```bash
git clone https://github.com/Smartappli/LLM_SERVER.git
cd LLM_SERVER
```

---

## 3) Créer le volume Docker des modèles

Depuis le dossier `Docker/` :

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

## 4) Construire les images Docker

> Les commandes suivantes sont à exécuter depuis le dossier `Docker/`.

### Image CPU
```bash
cd cpu
docker build -t smartappli/llama-cpp-python-server-cpu:1.0 -f cpu.Dockerfile ..
```

### Image CUDA (GPU)
```bash
cd ../cuda
docker build -t smartappli/llama-cpp-python-server-cuda:1.0 -f cuda.Dockerfile ..
```

### Image XPU (Intel, expérimental)
```bash
cd ../xpu
docker build -t smartappli/llama-cpp-python-server-xpu:1.0 -f xpu.Dockerfile ..
```

### Image ROCm (AMD, expérimental)
```bash
cd ../rocm
docker build -t smartappli/llama-cpp-python-server-rocm:1.0 -f rocm.Dockerfile ..
```

### Image Vulkan (expérimental)
```bash
cd ../vulkan
docker build -t smartappli/llama-cpp-python-server-vulkan:1.0 -f vulkan.Dockerfile ..
```

### Image OpenCL (expérimental)
```bash
cd ../opencl
docker build -t smartappli/llama-cpp-python-server-opencl:1.0 -f opencl.Dockerfile ..
```

---

## 5) Lancer le serveur

Les conteneurs montent le volume `LLM_SERVER` sur `/models`.

### Démarrage CPU
```bash
docker run --rm -p 8008:8008 -v LLM_SERVER:/models smartappli/llama-cpp-python-server-cpu:1.0
```

### Démarrage GPU
```bash
docker run --rm --gpus all -p 8008:8008 -v LLM_SERVER:/models smartappli/llama-cpp-python-server-cuda:1.0
```

### Démarrage XPU (Intel, expérimental)
```bash
docker run --rm -p 8008:8008 -v LLM_SERVER:/models smartappli/llama-cpp-python-server-xpu:1.0
```

### Démarrage ROCm (AMD, expérimental)
```bash
docker run --rm -p 8008:8008 -v LLM_SERVER:/models smartappli/llama-cpp-python-server-rocm:1.0
```

### Démarrage Vulkan (expérimental)
```bash
docker run --rm -p 8008:8008 -v LLM_SERVER:/models smartappli/llama-cpp-python-server-vulkan:1.0
```

### Démarrage OpenCL (expérimental)
```bash
docker run --rm -p 8008:8008 -v LLM_SERVER:/models smartappli/llama-cpp-python-server-opencl:1.0
```

API compatible OpenAI disponible sur :
- `http://localhost:8008/v1`

---

## 6) Tester le projet

### 6.1 Test unitaire des fichiers de configuration

Depuis la racine du dépôt :

```bash
python -m unittest -v tests/test_configs.py
```

### 6.2 Test de requête (smoke test)

Le script `Docker/main.py` envoie une requête au serveur local :

```bash
python Docker/main.py
```

> Assurez-vous qu’un serveur est déjà lancé sur `http://localhost:8008/v1`.

---

## 7) Dépendances Python locales

```bash
pip install -r requirements.txt
```

---

## 8) Dépannage rapide

- **Port occupé** : changez le mapping `-p 8008:8008` (ex. `-p 8010:8008`).
- **GPU non détecté** : vérifiez Docker + NVIDIA Container Toolkit et testez `docker run --gpus all ...`.
- **XPU Intel non détecté** : vérifiez les drivers Intel GPU sur l'hôte et l'accès aux devices dans Docker.
- **ROCm non détecté** : vérifiez les drivers AMD ROCm sur l'hôte et les permissions devices (`/dev/kfd`, `/dev/dri`).
- **Vulkan non détecté** : vérifiez la stack Vulkan de l'hôte (`vulkaninfo`) et l'accès aux devices GPU.
- **OpenCL non détecté** : vérifiez le runtime OpenCL fournisseur et la visibilité via `clinfo`.
- **Modèles introuvables** : vérifiez que le volume `LLM_SERVER` contient bien les modèles attendus.

---

## 9) Arborescence utile

- `Docker/cpu/cpu.Dockerfile` : image CPU
- `Docker/cuda/cuda.Dockerfile` : image GPU
- `Docker/cpu/config-cpu.json` : config modèles CPU
- `Docker/cuda/config-cuda.json` : config modèles GPU
- `Docker/xpu/xpu.Dockerfile` : image XPU Intel (expérimentale)
- `Docker/xpu/config-xpu.json` : config modèles XPU
- `Docker/rocm/rocm.Dockerfile` : image ROCm AMD (expérimentale)
- `Docker/rocm/config-rocm.json` : config modèles ROCm
- `Docker/vulkan/vulkan.Dockerfile` : image Vulkan (expérimentale)
- `Docker/vulkan/config-vulkan.json` : config modèles Vulkan
- `Docker/opencl/opencl.Dockerfile` : image OpenCL (expérimentale)
- `Docker/opencl/config-opencl.json` : config modèles OpenCL
- `tests/test_configs.py` : tests unitaires sur les configs
- `Docker/main.py` : script de test de requête
