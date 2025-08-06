@echo off
REM Simple Lambda build script
setlocal enabledelayedexpansion

echo 🚀 Building Lambda package...

REM Clean up
if exist lambda_package rmdir /s /q lambda_package
if exist lambda_deployment.zip del lambda_deployment.zip

REM Create package directory
mkdir lambda_package

REM Install dependencies
echo Installing dependencies...
pip install -r requirements_prod.txt -t lambda_package --no-cache-dir --disable-pip-version-check

REM Copy application files
copy lambda_function.py lambda_package\
xcopy /e /i /q services lambda_package\services
xcopy /e /i /q utils lambda_package\utils

REM Remove Windows files
cd lambda_package
del /s /q *.pyd 2>nul
del /s /q *.dll 2>nul
del /s /q *.exe 2>nul
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
cd ..

REM Create ZIP
powershell -Command "Compress-Archive -Path 'lambda_package\*' -DestinationPath 'lambda_deployment.zip' -Force"

REM Check result
if exist lambda_deployment.zip (
    for %%A in (lambda_deployment.zip) do set SIZE=%%~zA
    echo ✅ Package created: lambda_deployment.zip (!SIZE! bytes)
    
    REM Cleanup
    rmdir /s /q lambda_package
    
    echo 🎉 Build completed successfully!
    echo 📦 Ready to upload to AWS Lambda
    exit /b 0
) else (
    echo ❌ Failed to create package
    exit /b 1
)