Ubuntu 22.04

'''
cd Docker
sudo chmod +x create_docker_violume.sh
sudo ./create_docker_violume.sh

cd cpu
docker build -t smartappli/llama-cpp-python-server-cpu:1.0 .

cd ..
cd cuda
docker build -t smartappli/llama-cpp-python-server-cuda:1.0 .

docker run -v LLM_SERVER:/models smartappli/llama-cpp-python-server-cpu

or

docker run -v LLM_SERVER:/models smartappli/llama-cpp-python-server-cuda
'''
