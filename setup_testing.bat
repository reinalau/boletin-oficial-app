@echo off
REM Script para configurar y probar MongoDB

echo 🔧 Setup y Test de MongoDB
echo ===========================

echo.
echo Este script te ayuda a configurar y probar MongoDB.
echo.

REM Verificar si existe .env
if exist ".env" (
    echo ✅ Archivo .env encontrado
    echo ℹ️  El script test_real_mongodb.py lo cargará automáticamente
) else (
    echo ⚠️  Archivo .env no encontrado
    echo.
    set /p CREATE_ENV="¿Deseas crear un archivo .env desde .env.example? (y/N): "
    if /i "!CREATE_ENV!"=="y" (
        if exist ".env.example" (
            copy .env.example .env >nul
            echo ✅ Archivo .env creado desde .env.example
            echo.
            echo ⚠️  IMPORTANTE: Edita el archivo .env con tus credenciales reales:
            echo    - MONGODB_CONNECTION_STRING
            echo    - GOOGLE_API_KEY
            echo.
            echo ℹ️  Abriendo .env para editar...
            start notepad .env
            pause
        ) else (
            echo ❌ .env.example no encontrado
        )
    )
)

echo.
echo 🧪 Probando conexión a MongoDB...
echo ================================

REM Ejecutar test de conexión real
pytest tests/test_database_service.py -v

echo.
echo 🧪 Probando conexión a MongoDB...
echo ================================


pause