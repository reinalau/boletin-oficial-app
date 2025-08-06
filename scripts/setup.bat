@echo off
REM Setup script para Boletín Oficial Telegram App
REM Este script ayuda a configurar el proyecto después de clonar el repositorio

setlocal enabledelayedexpansion

echo.
echo 🚀 Setup Script - Boletín Oficial Telegram App
echo ===============================================
echo.

REM Verificar que estamos en la raíz del proyecto
if not exist "lambda_function.py" (
    echo ❌ Error: Este script debe ejecutarse desde la raíz del proyecto
    echo    Asegúrate de estar en la carpeta que contiene lambda_function.py
    pause
    exit /b 1
)

echo 📋 Verificando estructura del proyecto...

REM Verificar archivos importantes
set FILES_OK=true

if not exist "scripts\iac\terraform.tfvars.example" (
    echo ❌ scripts\iac\terraform.tfvars.example no encontrado
    set FILES_OK=false
)

if not exist "scripts\iac\main.tf" (
    echo ❌ scripts\iac\main.tf no encontrado
    set FILES_OK=false
)

if not exist "requirements.txt" (
    echo ❌ requirements.txt no encontrado
    set FILES_OK=false
)

if "%FILES_OK%"=="false" (
    echo.
    echo ❌ Estructura del proyecto incompleta
    echo    Por favor, verifica que todos los archivos estén presentes
    pause
    exit /b 1
)

echo ✅ Estructura del proyecto verificada

echo.
echo 🔧 Configurando archivos de Terraform...

REM Verificar si terraform.tfvars ya existe
if exist "scripts\iac\terraform.tfvars" (
    echo ⚠️  scripts\iac\terraform.tfvars ya existe
    echo.
    set /p OVERWRITE="¿Deseas sobrescribirlo? (y/N): "
    if /i not "!OVERWRITE!"=="y" (
        echo ℹ️  Manteniendo archivo existente
        goto :skip_tfvars
    )
)

REM Copiar archivo de ejemplo
copy "scripts\iac\terraform.tfvars.example" "scripts\iac\terraform.tfvars" >nul
if !errorlevel! equ 0 (
    echo ✅ Archivo scripts\iac\terraform.tfvars creado desde plantilla
) else (
    echo ❌ Error al crear scripts\iac\terraform.tfvars
    pause
    exit /b 1
)

:skip_tfvars

echo.
echo 📝 Verificando prerrequisitos...

REM Verificar Python
python --version >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=2" %%a in ('python --version 2^>^&1') do set PYTHON_VERSION=%%a
    echo ✅ Python: !PYTHON_VERSION!
) else (
    echo ❌ Python no encontrado
    echo    Instalar desde: https://www.python.org/downloads/
    set PREREQ_MISSING=true
)

REM Verificar pip
pip --version >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ pip disponible
) else (
    echo ❌ pip no encontrado
    set PREREQ_MISSING=true
)

REM Verificar Terraform
terraform version >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=2" %%a in ('terraform version ^| findstr "Terraform"') do set TF_VERSION=%%a
    echo ✅ Terraform: !TF_VERSION!
) else (
    echo ❌ Terraform no encontrado
    echo    Instalar desde: https://www.terraform.io/downloads.html
    set PREREQ_MISSING=true
)

REM Verificar AWS CLI (opcional)
aws --version >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ AWS CLI disponible
) else (
    echo ⚠️  AWS CLI no encontrado (opcional)
    echo    Instalar desde: https://aws.amazon.com/cli/
)

if "%PREREQ_MISSING%"=="true" (
    echo.
    echo ❌ Faltan prerrequisitos importantes
    echo    Por favor, instala los componentes faltantes antes de continuar
    pause
    exit /b 1
)

echo.
echo 🔑 Configuración de credenciales...
echo.
echo Para completar la configuración, necesitas:
echo.
echo 1. 📝 Editar scripts\iac\terraform.tfvars con tus credenciales:
echo    - Google Gemini API Key
echo    - MongoDB Atlas Connection String
echo    - Configuraciones de AWS
echo.
echo 2. 🔐 Configurar credenciales de AWS:
echo    - Variables de entorno (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
echo    - O usar: aws configure
echo    - O configurar AWS_PROFILE
echo.

set /p EDIT_NOW="¿Deseas abrir scripts\iac\terraform.tfvars para editarlo ahora? (y/N): "
if /i "!EDIT_NOW!"=="y" (
    echo ℹ️  Abriendo editor...
    start notepad "scripts\iac\terraform.tfvars"
    echo.
    echo ⚠️  IMPORTANTE: Completa TODOS los valores marcados como REQUERIDOS
    echo    Especialmente:
    echo    - google_api_key
    echo    - mongodb_connection_string
    echo.
    pause
)

echo.
echo 🧪 ¿Deseas instalar las dependencias de Python ahora?
set /p INSTALL_DEPS="Esto ejecutará: pip install -r requirements.txt (y/N): "
if /i "!INSTALL_DEPS!"=="y" (
    echo.
    echo 📦 Instalando dependencias de Python...
    pip install -r requirements.txt
    if !errorlevel! equ 0 (
        echo ✅ Dependencias instaladas correctamente
    ) else (
        echo ❌ Error al instalar dependencias
        echo    Intenta manualmente: pip install -r requirements.txt
    )
)

echo.
echo 🎉 Setup completado!
echo.
echo 📋 Próximos pasos:
echo.
echo 1. ✅ Verificar que scripts\iac\terraform.tfvars esté completo
echo 2. ✅ Configurar credenciales de AWS
echo 3. 🚀 Ejecutar despliegue: deploy.bat
echo 4. 🧪 Probar API: python test_api.py [URL]
echo.
echo 📚 Documentación disponible:
echo    - README.md - Documentación general
echo    - DEPLOYMENT_GUIDE.md - Guía de despliegue detallada
echo    - TROUBLESHOOTING.md - Solución de problemas
echo    - API_DOCUMENTATION.md - Documentación de API
echo.

echo ⚠️  RECORDATORIO DE SEGURIDAD:
echo    - NUNCA commitear scripts\iac\terraform.tfvars al repositorio
echo    - Mantener credenciales seguras y rotarlas regularmente
echo    - Revisar .gitignore para archivos sensibles
echo.

pause
endlocal