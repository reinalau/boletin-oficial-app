@echo off
REM Destroy infrastructure and clean up files
setlocal enabledelayedexpansion

echo 🗑️ Destroying infrastructure and cleaning up...

REM Step 1: Destroy Terraform infrastructure
echo.
echo 🏗️ Step 1: Destroying infrastructure...
cd scripts\iac

terraform destroy -var-file="terraform.tfvars" -auto-approve
if !errorlevel! neq 0 (
    echo ❌ Terraform destroy failed
    cd ..\..
    exit /b 1
)

cd ..\..

REM Step 2: Clean up build artifacts
echo.
echo 🧹 Step 2: Cleaning up build artifacts...

if exist lambda_deployment.zip (
    del lambda_deployment.zip
    echo   - Removed lambda_deployment.zip
)

if exist lambda_layer.zip (
    del lambda_layer.zip
    echo   - Removed lambda_layer.zip
)

if exist lambda_package (
    rmdir /s /q lambda_package
    echo   - Removed lambda_package directory
)

if exist layer_package (
    rmdir /s /q layer_package
    echo   - Removed layer_package directory
)

echo.
echo 🎉 Cleanup completed successfully!
echo   - Infrastructure destroyed
echo   - Build artifacts removed
echo.

exit /b 0