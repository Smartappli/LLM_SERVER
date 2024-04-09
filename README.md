# Windows

Install [Docker Desktop](https://www.docker.com/get-started/)

Install [Chocolatey](https://chocolatey.org/install)

Open a command prompt: Ctrl + R

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

Clone the repository
```bash
gît clone https://github.com/Smartappli/LLM_SERVER.git
```

Launch Docker Desktop

Docker volume creation
```bash
cd LLM_SERVER
cd Docker
create_docker_volume.bat
```

Build Docker image for Llama CPP Python Server - CPU with OpenBlast
```bash
cd cpu
docker build -t smartappli/llama-cpp-python-server-cpu:1.0 .
```

Build Docker image for Llama CPP Python Server - CUDA with OpenBlast
```bash
cd ..
cd cuda
docker build -t smartappli/llama-cpp-python-server-cuda:1.0 .
```


# Ubuntu 22.04

Install Wget, jq, and git
```bash
apt install update
apt install wget jq git 
```


Docker volume creation
```bash
cd Docker
sudo chmod +x create_docker_volume.sh
sudo ./create_docker_volume.sh
```

Build Docker image for Llama CPP Python Server - CPU with OpenBlast
```bash
cd ./Docker/cpu
docker build -t smartappli/llama-cpp-python-server-cpu:1.0 .
```

Build Docker image for Llama CPP Python Server - CUDA with OpenBlast
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

