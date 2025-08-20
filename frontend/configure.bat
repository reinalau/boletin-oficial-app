@echo off
echo.
echo ============================================
echo   Configuracion del Frontend
echo ============================================
echo.

echo 🔧 Configurando frontend con URL de Lambda...

REM Cambiar al directorio de Terraform
cd /d "%~dp0..\scripts\iac"

echo 📡 Obteniendo URL de Lambda desde Terraform...

REM Obtener la URL de Lambda
for /f "tokens=*" %%i in ('terraform output -raw lambda_function_url 2^>nul') do set LAMBDA_URL=%%i

if "%LAMBDA_URL%"=="" (
    echo ❌ Error: No se pudo obtener la URL de Lambda desde Terraform
    echo.
    echo 💡 Soluciones posibles:
    echo   1. Ejecutar: terraform apply
    echo   2. Verificar que el despliegue sea exitoso
    echo   3. Configurar manualmente en index.html
    echo.
    pause
    exit /b 1
)

echo ✅ URL de Lambda obtenida: %LAMBDA_URL%

REM Volver al directorio frontend
cd /d "%~dp0"

echo 🔄 Actualizando configuración en index.html...

REM Crear un script temporal de PowerShell para reemplazar el contenido
echo $content = Get-Content 'index.html' -Raw > temp_replace.ps1
echo $content = $content -replace 'meta name="lambda-function-url" content="[^"]*"', 'meta name="lambda-function-url" content="%LAMBDA_URL%"' >> temp_replace.ps1
echo $content ^| Set-Content 'index.html' >> temp_replace.ps1

REM Ejecutar el script de PowerShell
powershell -ExecutionPolicy Bypass -File temp_replace.ps1

REM Limpiar archivo temporal
del temp_replace.ps1

echo 📝 Creando archivo .env...
echo LAMBDA_FUNCTION_URL=%LAMBDA_URL% > .env

echo.
echo 🎉 Configuración completada exitosamente!
echo.
echo 📋 Próximos pasos:
echo   1. Verificar que index.html tenga la URL correcta
echo   2. Desplegar el frontend a tu hosting (Vercel, Netlify, etc.)
echo   3. Probar la aplicación
echo.
pause