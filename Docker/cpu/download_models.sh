#!/bin/bash

# Docker volume name
volume_name="llm_volume"

# Check if the volume already exists
if ! docker volume inspect "$volume_name" > /dev/null 2>&1; then
    # Volume does not exist, create it
    docker volume create "$volume_name"
    echo "Volume '$volume_name' created."
else
    echo "Volume '$volume_name' already exists."
fi

# Get the mount path of the volume
volume_path=$(docker volume inspect --format='{{.Mountpoint}}' "$volume_name")

# Check if the "models" directory exists in the volume
if [ ! -d "$volume_path/models" ]; then
    # "models" directory does not exist, create it
    mkdir "$volume_path/models"
    echo "Directory 'models' created in volume '$volume_name'."
else
    echo "Directory 'models' already exists in volume '$volume_name'."
fi

# Function to download and save a model
download_and_save_model() {
    local repository=$1
    local model_alias=$2
    local file_name=$3
    local save_path=$4

    echo "Downloading model $model_alias into $save_path..."
    wget -O "$save_path/$model_alias.gguf" "$repository/$file_name"

    if [ $? -eq 0 ]; then
        echo "Model '$model_alias' downloaded successfully into '$save_path'."
    else
        echo "Error downloading model '$model_alias'."
    fi
}

# Get models from the JSON file
models_json=$(cat config-cpu.json)
models=$(echo "$models_json" | jq -c '.models[]')

# Download and save each model into the Docker volume
for model in $models; do
    repository=$(echo "$model" | jq -r '.model | split("/") | .[1]')
    model_alias=$(echo "$model" | jq -r '.model_alias')
    file_name=$(echo "$model" | jq -r '.model | split("/") | .[2]')
    download_and_save_model "$repository" "$model_alias" "$file_name" "$volume_path/models"
done
