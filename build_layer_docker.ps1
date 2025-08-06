# Build Lambda Layer using Docker for Linux compatibility
Write-Host "🐳 Building Lambda Layer with Docker..." -ForegroundColor Green

# Check if Docker is available
try {
    docker --version | Out-Null
} catch {
    Write-Host "❌ Docker is not available. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Clean up
if (Test-Path "layer_package") { Remove-Item -Recurse -Force "layer_package" }
if (Test-Path "lambda_layer.zip") { Remove-Item -Force "lambda_layer.zip" }

Write-Host "Creating layer structure..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "layer_package" -Force | Out-Null

Write-Host "Installing dependencies in Linux container..." -ForegroundColor Yellow

# Run Docker command
$dockerCmd = @"
docker run --rm -v "${PWD}:/workspace" -w /workspace python:3.11-slim bash -c "
mkdir -p layer_package/python &&
pip install -r requirements_prod.txt -t layer_package/python --no-cache-dir --disable-pip-version-check &&
find layer_package/python -name '*.pyc' -delete &&
find layer_package/python -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
"
"@

Invoke-Expression $dockerCmd

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed" -ForegroundColor Red
    exit 1
}

Write-Host "Creating ZIP package..." -ForegroundColor Yellow
Compress-Archive -Path "layer_package\*" -DestinationPath "lambda_layer.zip" -Force

# Check result
if (Test-Path "lambda_layer.zip") {
    $size = (Get-Item "lambda_layer.zip").Length
    Write-Host "✅ Layer created: lambda_layer.zip ($size bytes)" -ForegroundColor Green
    
    # Cleanup
    Remove-Item -Recurse -Force "layer_package"
    
    Write-Host "🎉 Linux-compatible layer build completed!" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to create layer" -ForegroundColor Red
    exit 1
}