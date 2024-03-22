@echo off
REM Docker volume name
set "volume_name=llm_volume"

REM Check if the volume already exists
docker volume inspect %volume_name% >nul 2>&1
if errorlevel 1 (
    REM Volume does not exist, create it
    docker volume create %volume_name%
    echo Volume '%volume_name%' created.
) else (
    echo Volume '%volume_name%' already exists.
)

REM Get the mount path of the volume
for /f "tokens=*" %%a in ('docker volume inspect --format "{{.Mountpoint}}" %volume_name%') do set "volume_path=%%a"

REM Function to download and save a model
:download_and_save_model
set "repository=%1"
set "model_name=%2"
set "file_name=%3"
set "save_path=%4"

echo Downloading model %model_name% into %save_path%...

pushd %save_path%
if not exist %repository% mkdir %repository%
cd %repository%
if not exist %model_name% mkdir %model_name%
cd %model_name%

curl -O "https://huggingface.co/%repository%/%model_name%/resolve/main/%file_name%"

popd

if %errorlevel% equ 0 (
    echo Model '%model_name%' downloaded successfully into '%save_path%'.
) else (
    echo Error downloading model '%model_name%'.
)
exit /b
REM Get models from the JSON file
for /f "tokens=*" %%x in ('type cuda\config-cuda.json') do set "models_json=%%x"
echo %models_json% | jq -c ".models[]" | findstr /r /c:"[^ ]" > models.txt

REM Download and save each model into the Docker volume
for /f "delims=" %%m in (models.txt) do (
    echo %%m | jq -r ".model | split(\"/\") | .[1]" > repository.txt
    echo %%m | jq -r ".model | split(\"/\") | .[2]" > model_name.txt
    echo %%m | jq -r ".model | split(\"/\") | .[3]" > file_name.txt

    set /p repository=<repository.txt
    set /p model_name=<model_name.txt
    set /p file_name=<file_name.txt

    del repository.txt
    del model_name.txt
    del file_name.txt

    call :download_and_save_model "%repository%" "%model_name%" "%file_name%" "%volume_path%"
)

del models.txt
