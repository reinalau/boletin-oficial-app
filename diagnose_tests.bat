@echo off
REM Script de diagnóstico completo para problemas de testing

echo 🔍 Diagnóstico del entorno de testing
echo =====================================

echo.
echo 📋 Información del sistema:
python --version
pip --version

echo.
echo 📦 Paquetes instalados relacionados con testing:
pip list | findstr /i "pytest\|mock"

echo.
echo 🔍 Verificando importaciones:
python -c "
import sys
print('Python executable:', sys.executable)
print('Python path:')
for p in sys.path:
    print('  -', p)
print()

try:
    import pytest
    print('✅ pytest importado correctamente')
    print('   Versión:', pytest.__version__)
    print('   Ubicación:', pytest.__file__)
except Exception as e:
    print('❌ Error importando pytest:', e)

try:
    from pytest import FixtureDef
    print('✅ FixtureDef importado correctamente')
except Exception as e:
    print('❌ Error importando FixtureDef:', e)

try:
    import pytest_mock
    print('✅ pytest_mock importado correctamente')
    print('   Versión:', pytest_mock.__version__)
except Exception as e:
    print('❌ Error importando pytest_mock:', e)

try:
    import mongomock
    print('✅ mongomock importado correctamente')
    print('   Versión:', mongomock.__version__)
except Exception as e:
    print('❌ Error importando mongomock:', e)
"

echo.
echo 🧪 Intentando ejecutar pytest básico:
pytest --version

echo.
echo 📁 Verificando estructura de archivos de test:
if exist "tests\test_database_service.py" (
    echo ✅ tests\test_database_service.py encontrado
) else (
    echo ❌ tests\test_database_service.py NO encontrado
)

if exist "tests\__init__.py" (
    echo ✅ tests\__init__.py encontrado
) else (
    echo ❌ tests\__init__.py NO encontrado
)

echo.
echo 🔧 Configuración de pytest:
if exist "pytest.ini" (
    echo ✅ pytest.ini encontrado
    echo Contenido:
    type pytest.ini
) else (
    echo ❌ pytest.ini NO encontrado
)

pause