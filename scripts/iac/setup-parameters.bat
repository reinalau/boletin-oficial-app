@echo off
REM Script para configurar parámetros en AWS Systems Manager Parameter Store
REM Este script ayuda a configurar las credenciales antes del despliegue

setlocal enabledelayedexpansion

echo.
echo 🔧 AWS Systems Manager Parameter Store Setup
echo =============================================
echo.
echo Este script te ayuda a configurar los parámetros necesarios
echo en AWS Systems Manager Parameter Store antes del despliegue.
echo.

REM Verificar que AWS CLI esté instalado
aws --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ AWS CLI no está instalado o no está en PATH
    echo.
    echo 💡 Para instalar AWS CLI:
    echo    https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
    echo.
    exit /b 1
)

REM Verificar configuración de AWS
aws sts get-caller-identity >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ AWS CLI no está configurado correctamente
    echo.
    echo 💡 Para configurar AWS CLI:
    echo    aws configure
    echo.
    exit /b 1
)

echo ✅ AWS CLI configurado correctamente
echo.

REM Configurar variables
set PROJECT_NAME=boletin-oficial-telegram-app
set ENVIRONMENT=prod
set PREFIX=/%PROJECT_NAME%/%ENVIRONMENT%

echo 📋 Configuración:
echo    Proyecto: %PROJECT_NAME%
echo    Entorno: %ENVIRONMENT%
echo    Prefijo: %PREFIX%
echo.

REM Función para crear parámetro
:create_parameter
set PARAM_NAME=%1
set PARAM_DESC=%2
set PARAM_TYPE=%3
set PARAM_VALUE=%4

echo 🔐 Creando parámetro: %PREFIX%/%PARAM_NAME%

aws ssm put-parameter ^
    --name "%PREFIX%/%PARAM_NAME%" ^
    --description "%PARAM_DESC%" ^
    --value "%PARAM_VALUE%" ^
    --type "%PARAM_TYPE%" ^
    --overwrite >nul 2>&1

if !errorlevel! equ 0 (
    echo ✅ Parámetro %PARAM_NAME% creado exitosamente
) else (
    echo ❌ Error creando parámetro %PARAM_NAME%
)

goto :eof

echo 🚀 Creando parámetros...
echo.

REM Solicitar credenciales al usuario
set /p GOOGLE_API_KEY="🔑 Ingresa tu Google API Key: "
if "%GOOGLE_API_KEY%"=="" (
    echo ❌ Google API Key es requerido
    exit /b 1
)

set /p MONGODB_CONNECTION="🔑 Ingresa tu MongoDB Connection String: "
if "%MONGODB_CONNECTION%"=="" (
    echo ❌ MongoDB Connection String es requerido
    exit /b 1
)

set /p MONGODB_DATABASE="📊 Ingresa el nombre de la base de datos MongoDB [BoletinOficial]: "
if "%MONGODB_DATABASE%"=="" set MONGODB_DATABASE=BoletinOficial

set /p MONGODB_COLLECTION="📊 Ingresa el nombre de la colección MongoDB [boletin-oficial]: "
if "%MONGODB_COLLECTION%"=="" set MONGODB_COLLECTION=boletin-oficial

echo.
echo 📝 Creando parámetros en AWS Systems Manager...

REM Crear parámetros
call :create_parameter "google-api-key" "Google API key for Gemini LLM" "SecureString" "%GOOGLE_API_KEY%"
call :create_parameter "mongodb-connection-string" "MongoDB Atlas connection string" "SecureString" "%MONGODB_CONNECTION%"
call :create_parameter "mongodb-database" "MongoDB database name" "String" "%MONGODB_DATABASE%"
call :create_parameter "mongodb-collection" "MongoDB collection name" "String" "%MONGODB_COLLECTION%"

echo.
echo 🎉 Configuración completada!
echo.
echo 📋 Parámetros creados:
echo    %PREFIX%/google-api-key
echo    %PREFIX%/mongodb-connection-string
echo    %PREFIX%/mongodb-database
echo    %PREFIX%/mongodb-collection
echo.
echo 💡 Próximos pasos:
echo    1. Ejecutar: tf apply
echo    2. Los parámetros se leerán automáticamente desde Parameter Store
echo.
echo 🔒 Seguridad:
echo    - Los parámetros SecureString están encriptados con KMS
echo    - Solo Lambda tiene permisos para leerlos
echo    - No hay costo adicional por usar Parameter Store
echo.

endlocal
pause