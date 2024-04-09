# Windows

Install [Docker Desktop](https://www.docker.com/get-started/) 

Install [Chocolatey](https://chocolatey.org/)

Install jq
```bash
choco install jq -y
```

Install curl
```bash
choco install curl -y
```

Install gît
```bash
Choco install git -y
```

```bash
gît clone https://github.com/Smartappli/LLM_SERVER.git
```

```bash
cd LLM_SERVER
```


Docker volume creation

```bash
cd Docker
create_docker_volume.bat
```

# Ubuntu 22.04


Docker volume creation

```bash
cd Docker
sudo chmod +x create_docker_volume.sh
sudo ./create_docker_volume.sh
```

Llama CPP Python Server - CPU with OpenBlast building
```bash
cd ./Docker/cpu
docker build -t smartappli/llama-cpp-python-server-cpu:1.0 .
```

Llama CPP Python Server - CUDA with OpenBlast building
```bash
cd ./Docker/cuda
docker build -t smartappli/llama-cpp-python-server-cuda:1.0 .
```

Run Llama cpp python server CPU
```bash
docker run -v LLM_SERVER:/models smartappli/llama-cpp-python-server-cpu
```

or

Run Llama cpp python server GPU
```bash
docker run -v LLM_SERVER:/models smartappli/llama-cpp-python-server-cuda
```

install dépendances
```bash
pip install -r requirements.txt
```

