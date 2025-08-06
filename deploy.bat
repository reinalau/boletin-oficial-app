@echo off
REM Deployment script for Boletin Oficial Telegram App (Windows version)
REM This script handles the complete deployment process using Terraform

setlocal enabledelayedexpansion

REM Configuration
set TERRAFORM_DIR=scripts\iac
set TFVARS_FILE=scripts\iac\terraform.tfvars
set TFVARS_EXAMPLE=scripts\iac\terraform.tfvars.example
set LAMBDA_ZIP=lambda_deployment.zip
set BUILD_SCRIPT=build.bat

echo.
echo 🚀 Starting deployment process...
echo ===============================================

REM Function to check prerequisites
:check_prerequisites
echo.
echo 🔍 Checking prerequisites...

REM Check if Terraform is installed
terraform version >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ Terraform is not installed. Please install Terraform first.
    echo ℹ️  Visit: https://www.terraform.io/downloads.html
    exit /b 1
)

REM Get Terraform version
for /f "tokens=2 delims= " %%a in ('terraform version ^| findstr "Terraform"') do set TERRAFORM_VERSION=%%a
echo ✅ Terraform version: !TERRAFORM_VERSION!

REM Check if AWS CLI is installed
aws --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ⚠️  AWS CLI is not installed. Make sure AWS credentials are configured.
    echo ℹ️  You can configure credentials using environment variables or IAM roles.
) else (
    echo ✅ AWS CLI is available
)

REM Check if Python is available for building
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ Python 3 is not installed. Required for building Lambda package.
    exit /b 1
)

echo ✅ Prerequisites check completed
goto :eof

REM Function to validate environment variables
:validate_environment
echo.
echo 🔧 Validating environment variables...

REM Check if terraform.tfvars exists
if not exist "%TFVARS_FILE%" (
    echo ❌ %TFVARS_FILE% not found!
    echo ℹ️  Please copy %TFVARS_EXAMPLE% to %TFVARS_FILE% and fill in your values.
    
    if exist "%TFVARS_EXAMPLE%" (
        echo ℹ️  Example file found. Copying to %TFVARS_FILE%...
        copy "%TFVARS_EXAMPLE%" "%TFVARS_FILE%" >nul
        echo ⚠️  Please edit %TFVARS_FILE% with your actual values before continuing.
        pause
        exit /b 1
    ) else (
        echo ❌ Example file %TFVARS_EXAMPLE% not found!
        exit /b 1
    )
)

REM Check for placeholder values in sensitive variables
findstr /c:"your-.*-here" /c:"example" /c:"changeme" "%TFVARS_FILE%" >nul
if !errorlevel! equ 0 (
    echo ❌ Please update placeholder values in %TFVARS_FILE%
    echo ℹ️  Found placeholder values that need to be replaced with actual values.
    pause
    exit /b 1
)

REM Check AWS credentials
if "%AWS_ACCESS_KEY_ID%"=="" if "%AWS_PROFILE%"=="" (
    echo ⚠️  No AWS credentials found in environment variables.
    echo ℹ️  Make sure you have configured AWS credentials via:
    echo ℹ️    - AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables
    echo ℹ️    - AWS_PROFILE environment variable
    echo ℹ️    - IAM role (if running on EC2)
    echo ℹ️    - AWS CLI configuration (~/.aws/credentials)
)

echo ✅ Environment validation completed
goto :eof

REM Function to build Lambda package
:build_lambda_package
echo.
echo 📦 Building Lambda deployment package...

REM Check if build script exists
if not exist "%BUILD_SCRIPT%" (
    echo ❌ Build script %BUILD_SCRIPT% not found!
    exit /b 1
)

REM Run build script
echo ℹ️  Running build script...
call "%BUILD_SCRIPT%"
if !errorlevel! neq 0 (
    echo ❌ Failed to build Lambda package
    exit /b 1
)

echo ✅ Lambda package built successfully

REM Verify package exists
if not exist "%LAMBDA_ZIP%" (
    echo ❌ Lambda deployment package %LAMBDA_ZIP% not found after build
    exit /b 1
)

REM Get package size
for %%A in ("%LAMBDA_ZIP%") do set PACKAGE_SIZE=%%~zA
echo ✅ Package size: !PACKAGE_SIZE! bytes

goto :eof

REM Function to initialize Terraform
:terraform_init
echo.
echo 🏗️  Initializing Terraform...

cd "%TERRAFORM_DIR%"

REM Initialize Terraform
terraform init -upgrade
if !errorlevel! neq 0 (
    echo ❌ Terraform initialization failed
    exit /b 1
)

echo ✅ Terraform initialized successfully
cd ..
goto :eof

REM Function to validate Terraform configuration
:terraform_validate
echo.
echo ✅ Validating Terraform configuration...

cd "%TERRAFORM_DIR%"

REM Validate Terraform configuration
terraform validate
if !errorlevel! neq 0 (
    echo ❌ Terraform configuration validation failed
    exit /b 1
)

echo ✅ Terraform configuration is valid
cd ..
goto :eof

REM Function to plan Terraform deployment
:terraform_plan
echo.
echo 📋 Planning Terraform deployment...

cd "%TERRAFORM_DIR%"

REM Create Terraform plan
terraform plan -var-file="%TFVARS_FILE%" -out=tfplan
if !errorlevel! neq 0 (
    echo ❌ Terraform planning failed
    exit /b 1
)

echo ✅ Terraform plan created successfully
echo ℹ️  Review the plan above before proceeding with deployment.
cd ..
goto :eof

REM Function to apply Terraform configuration
:terraform_apply
echo.
echo 🚀 Applying Terraform configuration...

cd "%TERRAFORM_DIR%"

REM Apply Terraform plan
terraform apply tfplan
if !errorlevel! neq 0 (
    echo ❌ Terraform deployment failed
    exit /b 1
)

echo ✅ Terraform deployment completed successfully

REM Clean up plan file
if exist tfplan del /q tfplan

cd ..
goto :eof

REM Function to show deployment outputs
:show_outputs
echo.
echo 📊 Deployment outputs:

cd "%TERRAFORM_DIR%"

REM Show Terraform outputs
terraform output

echo.
echo 🎉 Deployment completed successfully!
echo.
echo 📋 Important information:

REM Get API Gateway URL
for /f "delims=" %%i in ('terraform output -raw api_gateway_url 2^>nul') do set API_URL=%%i
for /f "delims=" %%i in ('terraform output -raw analyze_endpoint_url 2^>nul') do set ANALYZE_URL=%%i

if not "%API_URL%"=="" (
    echo   📡 API Gateway URL: %API_URL%
)

if not "%ANALYZE_URL%"=="" (
    echo   🔍 Analyze Endpoint: %ANALYZE_URL%
)

echo.
echo ⚠️  Next steps:
echo   1. Test your API using the test script: python test_api.py
echo   2. Configure your Telegram Mini App to use the API endpoint
echo   3. Monitor logs in AWS CloudWatch
echo.

cd ..
goto :eof

REM Function to show help
:show_help
echo Usage: %0 [OPTIONS]
echo.
echo Deploy the Boletin Oficial Telegram App infrastructure using Terraform
echo.
echo Options:
echo   /h, /help          Show this help message
echo   /p, /plan-only     Only run terraform plan, don't apply
echo   /s, /skip-build    Skip building Lambda package (use existing)
echo   /f, /force         Skip confirmation prompts
echo.
echo Examples:
echo   %0                 # Full deployment
echo   %0 /plan-only      # Only show what would be deployed
echo   %0 /skip-build     # Deploy without rebuilding Lambda package
echo.
goto :eof

REM Parse command line arguments
set PLAN_ONLY=false
set SKIP_BUILD=false
set FORCE=false

:parse_args
if "%1"=="" goto main
if /i "%1"=="/h" goto show_help
if /i "%1"=="/help" goto show_help
if /i "%1"=="/p" set PLAN_ONLY=true
if /i "%1"=="/plan-only" set PLAN_ONLY=true
if /i "%1"=="/s" set SKIP_BUILD=true
if /i "%1"=="/skip-build" set SKIP_BUILD=true
if /i "%1"=="/f" set FORCE=true
if /i "%1"=="/force" set FORCE=true
shift
goto parse_args

REM Main execution
:main
echo.
echo 🏗️  Boletin Oficial Telegram App Deployment
echo ==============================================

REM Execute deployment steps
call :check_prerequisites
call :validate_environment

if "%SKIP_BUILD%"=="false" (
    call :build_lambda_package
) else (
    echo ⚠️  Skipping Lambda package build
    if not exist "%LAMBDA_ZIP%" (
        echo ❌ Lambda package %LAMBDA_ZIP% not found. Cannot skip build.
        exit /b 1
    )
)

call :terraform_init
call :terraform_validate
call :terraform_plan

if "%PLAN_ONLY%"=="true" (
    echo ℹ️  Plan-only mode. Stopping before apply.
    cd "%TERRAFORM_DIR%"
    if exist tfplan del /q tfplan
    cd ..
    goto end
)

REM Confirmation prompt (unless forced)
if "%FORCE%"=="false" (
    echo.
    echo ⚠️  Ready to deploy infrastructure to AWS.
    echo    This will create resources that may incur costs.
    echo.
    set /p CONFIRM="Do you want to proceed with the deployment? (y/N): "
    if /i not "!CONFIRM!"=="y" (
        echo ℹ️  Deployment cancelled by user.
        cd "%TERRAFORM_DIR%"
        if exist tfplan del /q tfplan
        cd ..
        goto end
    )
)

call :terraform_apply
call :show_outputs

:end
endlocal
pause