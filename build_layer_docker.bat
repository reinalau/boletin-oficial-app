@echo off
REM Build Lambda Layer using Docker for Linux compatibility
setlocal enabledelayedexpansion

echo 🐳 Building Lambda Layer with Docker...

REM Check if Docker is available
docker --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ Docker is not available. Please install Docker Desktop.
    exit /b 1
)

REM Clean up
if exist layer_package rmdir /s /q layer_package
if exist lambda_layer.zip del lambda_layer.zip

echo Creating layer structure...
mkdir layer_package

REM Create a temporary script for Docker
echo mkdir -p /workspace/layer_package/python > temp_docker_script.sh
echo pip install -r /workspace/requirements_prod.txt -t /workspace/layer_package/python --no-cache-dir --disable-pip-version-check >> temp_docker_script.sh
echo find /workspace/layer_package/python -name "*.pyc" -delete >> temp_docker_script.sh
echo find /workspace/layer_package/python -name "__pycache__" -type d -exec rm -rf {} + 2^>/dev/null ^|^| true >> temp_docker_script.sh

echo Installing dependencies in Linux container...
docker run --rm -v "%cd%":/workspace -w /workspace python:3.11-slim bash /workspace/temp_docker_script.sh

if !errorlevel! neq 0 (
    echo ❌ Docker build failed
    del temp_docker_script.sh 2>nul
    exit /b 1
)

REM Clean up temp script
del temp_docker_script.sh 2>nul

REM Create layer ZIP
echo Creating ZIP package...
powershell -Command "Compress-Archive -Path 'layer_package\*' -DestinationPath 'lambda_layer.zip' -Force"

REM Check result
if exist lambda_layer.zip (
    for %%A in (lambda_layer.zip) do set SIZE=%%~zA
    echo ✅ Layer created: lambda_layer.zip (!SIZE! bytes)
    
    REM Cleanup
    rmdir /s /q layer_package
    
    echo 🎉 Linux-compatible layer build completed!
    exit /b 0
) else (
    echo ❌ Failed to create layer
    exit /b 1
)