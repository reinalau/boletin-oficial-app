@echo off
REM Terraform wrapper script para facilitar comandos desde la carpeta iac
REM Uso: tf.bat [comando terraform] [argumentos]

setlocal enabledelayedexpansion

REM Verificar que estamos en la carpeta correcta
if not exist "main.tf" (
    echo ❌ Error: Este script debe ejecutarse desde scripts\iac\
    echo    O usar los scripts de despliegue desde la raíz del proyecto
    exit /b 1
)

REM Verificar que terraform.tfvars existe
if not exist "terraform.tfvars" (
    echo ❌ Error: terraform.tfvars no encontrado
    echo.
    echo 💡 Para crear el archivo de configuración:
    echo    copy terraform.tfvars.example terraform.tfvars
    echo    notepad terraform.tfvars
    echo.
    exit /b 1
)

REM Verificar que lambda_deployment.zip existe (para comandos que lo necesitan)
if /i "%1"=="plan" goto check_zip
if /i "%1"=="apply" goto check_zip
goto skip_zip_check

:check_zip
if not exist "..\..\lambda_deployment.zip" (
    echo ❌ Error: lambda_deployment.zip no encontrado
    echo.
    echo 💡 Para crear el paquete Lambda:
    echo    cd ..\..
    echo    build.bat
    echo    cd scripts\iac
    echo.
    exit /b 1
)

:skip_zip_check

REM Si no se proporciona comando, mostrar ayuda
if "%1"=="" goto show_help

REM Comandos especiales con configuración automática
if /i "%1"=="init" (
    echo 🏗️  Inicializando Terraform...
    terraform init -upgrade
    goto end
)

if /i "%1"=="plan" (
    echo 📋 Planificando cambios...
    terraform plan -var-file="terraform.tfvars"
    goto end
)

if /i "%1"=="apply" (
    echo 🚀 Aplicando cambios...
    terraform apply -var-file="terraform.tfvars"
    goto end
)

if /i "%1"=="destroy" (
    echo 🗑️  Destruyendo recursos...
    echo ⚠️  CUIDADO: Esto eliminará TODOS los recursos de AWS
    set /p CONFIRM="¿Estás seguro? Escribe 'yes' para confirmar: "
    if /i not "!CONFIRM!"=="yes" (
        echo ℹ️  Operación cancelada
        goto end
    )
    terraform destroy -var-file="terraform.tfvars"
    goto end
)

if /i "%1"=="output" (
    echo 📊 Mostrando outputs...
    terraform output
    goto end
)

if /i "%1"=="show" (
    echo 📋 Mostrando estado actual...
    terraform show
    goto end
)

if /i "%1"=="validate" (
    echo ✅ Validando configuración...
    terraform validate
    goto end
)

if /i "%1"=="refresh" (
    echo 🔄 Refrescando estado...
    terraform refresh -var-file="terraform.tfvars"
    goto end
)

if /i "%1"=="fmt" (
    echo 🎨 Formateando archivos...
    terraform fmt
    goto end
)

REM Para otros comandos, pasar directamente a terraform
echo 🔧 Ejecutando: terraform %*
terraform %*
goto end

:show_help
echo.
echo 🛠️  Terraform Wrapper Script
echo ============================
echo.
echo Uso: tf.bat [comando] [argumentos]
echo.
echo Comandos disponibles:
echo.
echo   📋 Comandos básicos:
echo     init      - Inicializar Terraform
echo     plan      - Planificar cambios
echo     apply     - Aplicar cambios
echo     destroy   - Destruir recursos (con confirmación)
echo     output    - Mostrar outputs
echo     show      - Mostrar estado actual
echo     validate  - Validar configuración
echo     refresh   - Refrescar estado
echo     fmt       - Formatear archivos .tf
echo.
echo   🔧 Comandos avanzados:
echo     state list                    - Listar recursos en el estado
echo     state show [recurso]          - Mostrar detalles de un recurso
echo     import [recurso] [id]         - Importar recurso existente
echo     taint [recurso]               - Marcar recurso para recrear
echo     untaint [recurso]             - Desmarcar recurso
echo.
echo   📊 Comandos de información:
echo     version                       - Versión de Terraform
echo     providers                     - Listar providers
echo     workspace list                - Listar workspaces
echo.
echo Ejemplos:
echo   tf init                         # Inicializar
echo   tf plan                         # Ver cambios planeados
echo   tf apply                        # Aplicar cambios
echo   tf output api_gateway_url       # Ver URL del API Gateway
echo   tf state list                   # Ver todos los recursos
echo   tf destroy                      # Eliminar todo (con confirmación)
echo.
echo 📁 Archivos importantes:
echo   terraform.tfvars               # Tu configuración (SENSIBLE)
echo   terraform.tfvars.example       # Plantilla de configuración
echo   main.tf                        # Configuración principal
echo   variables.tf                   # Definición de variables
echo   outputs.tf                     # Outputs del despliegue
echo.
echo 💡 Consejos:
echo   - Siempre ejecutar 'tf plan' antes de 'tf apply'
echo   - Hacer backup del estado antes de cambios importantes
echo   - Usar 'tf validate' para verificar sintaxis
echo   - Revisar outputs con 'tf output' después del despliegue
echo.

:end
endlocal