@echo off
REM Script para verificar que todo esté listo para el despliegue

setlocal enabledelayedexpansion

echo.
echo 🔍 Verificación de Setup para Despliegue
echo ========================================
echo.

set ERRORS=0

REM Verificar que estamos en la carpeta correcta
if not exist "main.tf" (
    echo ❌ Error: Ejecutar desde scripts\iac\
    set /a ERRORS+=1
    goto end_check
)

REM Verificar terraform.tfvars
if exist "terraform.tfvars" (
    echo ✅ terraform.tfvars encontrado
) else (
    echo ❌ terraform.tfvars no encontrado
    echo    💡 Debería haberse creado automáticamente
    set /a ERRORS+=1
)

REM Verificar lambda_deployment.zip
if exist "..\..\lambda_deployment.zip" (
    echo ✅ lambda_deployment.zip encontrado
    for %%A in ("..\..\lambda_deployment.zip") do set SIZE=%%~zA
    echo    📦 Tamaño: !SIZE! bytes
) else (
    echo ❌ lambda_deployment.zip no encontrado
    echo    💡 Ejecutar desde la raíz: build.bat
    set /a ERRORS+=1
)

REM Verificar Terraform
terraform version >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Terraform instalado
    terraform version | findstr "Terraform"
) else (
    echo ❌ Terraform no encontrado
    echo    💡 Instalar desde: https://terraform.io/downloads
    set /a ERRORS+=1
)

REM Verificar AWS CLI
aws --version >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ AWS CLI instalado
    aws --version
) else (
    echo ⚠️  AWS CLI no encontrado (opcional para este paso)
    echo    💡 Instalar para configurar parámetros automáticamente
)

REM Verificar configuración AWS
aws sts get-caller-identity >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ AWS CLI configurado
    aws sts get-caller-identity --query "Account" --output text 2>nul
) else (
    echo ⚠️  AWS CLI no configurado (opcional para este paso)
    echo    💡 Configurar con: aws configure
)

:end_check
echo.
if !ERRORS! equ 0 (
    echo 🎉 Todo listo para el despliegue!
    echo.
    echo 📋 Próximos pasos:
    echo    1. tf init    # Inicializar Terraform
    echo    2. tf plan    # Ver cambios planeados
    echo    3. tf apply   # Aplicar cambios
    echo.
    echo 💡 Comandos disponibles:
    echo    tf init      # Inicializar
    echo    tf plan      # Planificar
    echo    tf apply     # Desplegar
    echo    tf output    # Ver outputs
    echo    tf destroy   # Eliminar todo
) else (
    echo ❌ Se encontraron !ERRORS! errores
    echo    Corregir los errores antes de continuar
    echo.
)

endlocal
pause