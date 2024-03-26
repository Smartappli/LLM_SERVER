# Windows

Install Docker Desktop 

Install jq 

Install curl

Install gît

```bash
gît clone 
```

```bash
cd LLM_SERVER
```

```bash
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

