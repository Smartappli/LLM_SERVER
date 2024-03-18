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

# Function to download and save a model
download_and_save_model() {
    local repository=$1
    local model_name=$2
    local file_name=$3
    local save_path=$4

    echo "Downloading model $model_name into $save_path..."

    cd "$save_path"
    if [ ! -d "$repository" ]; then
        mkdir "$repository"
    fi

    cd "$repository"
    if [ ! -d "$model_name" ]; then
        mkdir "$model_name"
    fi
    cd "$model_name"

    wget -N "https://huggingface.co/$repository/$model_name/resolve/main/$file_name"

    cd ../../..

    if [ $? -eq 0 ]; then
        echo "Model '$model_name' downloaded successfully into '$save_path'."
    else
        echo "Error downloading model '$model_name'."
    fi
}

# Get models from the JSON file
models_json=$(cat config.json)
models=$(jq -c '.models[]' <<< "$models_json")

# Download and save each model into the Docker volume
for model in $models; do
    repository=$(jq -r '.model | split("/") | .[1]' <<< "$model")
    model_name=$(jq -r '.model | split("/") | .[2]' <<< "$model")
    file_name=$(jq -r '.model | split("/") | .[3]' <<< "$model")
    download_and_save_model "$repository" "$model_name" "$file_name" "$volume_path"
done
