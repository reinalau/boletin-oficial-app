@echo off
REM Build Lambda function without dependencies (uses layer)
setlocal enabledelayedexpansion

echo 🚀 Building Lambda function (without dependencies)...

REM Clean up
if exist lambda_package rmdir /s /q lambda_package
if exist lambda_deployment.zip del lambda_deployment.zip

REM Create package directory
mkdir lambda_package

REM Copy only application files (no dependencies)
copy lambda_function.py lambda_package\
xcopy /e /i /q services lambda_package\services
xcopy /e /i /q utils lambda_package\utils

REM Remove cache files
cd lambda_package
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
cd ..

REM Create ZIP
powershell -Command "Compress-Archive -Path 'lambda_package\*' -DestinationPath 'lambda_deployment.zip' -Force"

REM Check result
if exist lambda_deployment.zip (
    for %%A in (lambda_deployment.zip) do set SIZE=%%~zA
    echo ✅ Lambda package created: lambda_deployment.zip (!SIZE! bytes)
    
    REM Cleanup
    rmdir /s /q lambda_package
    
    echo 🎉 Lambda build completed successfully!
    echo 📦 Ready to upload to AWS Lambda (with layer)
    exit /b 0
) else (
    echo ❌ Failed to create package
    exit /b 1
)