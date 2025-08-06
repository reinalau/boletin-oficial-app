#!/usr/bin/env python3
"""
Script de diagnóstico para tests del LLM service
"""

import os
import sys
from dotenv import load_dotenv

def diagnose_llm_test_environment():
    """Diagnóstico completo del entorno para tests de LLM"""
    
    print("🔍 Diagnóstico del Entorno para Tests de LLM")
    print("=" * 50)
    
    # 1. Verificar carga de .env
    print("\n1️⃣ Verificando archivo .env...")
    if os.path.exists('.env'):
        print("✅ Archivo .env encontrado")
        load_dotenv()
        print("✅ Variables cargadas desde .env")
    else:
        print("❌ Archivo .env no encontrado")
        return False
    
    # 2. Verificar API key de Google
    print("\n2️⃣ Verificando Google API Key...")
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        if api_key == 'your-gemini-api-key-here':
            print("❌ GOOGLE_API_KEY tiene valor de placeholder")
            print("   Necesitas configurar tu API key real de Gemini")
            return False
        else:
            print(f"✅ GOOGLE_API_KEY configurada: {api_key[:10]}...{api_key[-5:]}")
    else:
        print("❌ GOOGLE_API_KEY no configurada")
        return False
    
    # 3. Verificar dependencias
    print("\n3️⃣ Verificando dependencias...")
    
    try:
        import pytest
        print(f"✅ pytest: {pytest.__version__}")
    except ImportError as e:
        print(f"❌ pytest no instalado: {e}")
        return False
    
    try:
        import langchain
        print(f"✅ langchain: {langchain.__version__}")
    except ImportError as e:
        print(f"❌ langchain no instalado: {e}")
        return False
    
    try:
        import langchain_google_genai
        print("✅ langchain_google_genai disponible")
    except ImportError as e:
        print(f"❌ langchain_google_genai no instalado: {e}")
        return False
    
    try:
        import google.generativeai as genai
        print("✅ google.generativeai disponible")
    except ImportError as e:
        print(f"❌ google.generativeai no instalado: {e}")
        return False
    
    # 4. Verificar importación del servicio
    print("\n4️⃣ Verificando importación del LLM service...")
    try:
        from services.llm_service import LLMAnalysisService
        print("✅ LLMAnalysisService importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando LLMAnalysisService: {e}")
        return False
    
    # 5. Probar inicialización del servicio
    print("\n5️⃣ Probando inicialización del servicio...")
    try:
        service = LLMAnalysisService()
        print("✅ LLMAnalysisService inicializado correctamente")
        print(f"   Modelo configurado: gemini-2.5-flash")
    except Exception as e:
        print(f"❌ Error inicializando LLMAnalysisService: {e}")
        print(f"   Tipo de error: {type(e).__name__}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False
    
    # 6. Probar conexión básica a Gemini (opcional)
    print("\n6️⃣ Probando conexión básica a Gemini...")
    try:
        # Test muy simple para verificar conectividad
        test_response = service.llm.invoke([{"role": "user", "content": "Responde solo 'OK'"}])
        if hasattr(test_response, 'content'):
            print("✅ Conexión a Gemini API exitosa")
            print(f"   Respuesta de prueba: {test_response.content[:50]}")
        else:
            print("⚠️  Respuesta inesperada de Gemini API")
    except Exception as e:
        print(f"❌ Error conectando a Gemini API: {e}")
        print(f"   Tipo de error: {type(e).__name__}")
        
        # Sugerencias específicas según el tipo de error
        if "API_KEY" in str(e).upper():
            print("   💡 Problema con API key - verifica que sea válida")
        elif "QUOTA" in str(e).upper():
            print("   💡 Problema de cuota - verifica límites de API")
        elif "PERMISSION" in str(e).upper():
            print("   💡 Problema de permisos - verifica configuración de API")
        else:
            print("   💡 Error desconocido - verifica conectividad a internet")
        
        return False
    
    # 7. Verificar archivo de tests
    print("\n7️⃣ Verificando archivo de tests...")
    if os.path.exists('tests/test_llm_service.py'):
        print("✅ Archivo tests/test_llm_service.py encontrado")
        
        # Verificar que contiene la clase de tests reales
        with open('tests/test_llm_service.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'TestLLMAnalysisServiceRealAPI' in content:
                print("✅ Clase TestLLMAnalysisServiceRealAPI encontrada")
            else:
                print("❌ Clase TestLLMAnalysisServiceRealAPI no encontrada")
                return False
    else:
        print("❌ Archivo tests/test_llm_service.py no encontrado")
        return False
    
    print("\n🎉 ¡Todos los diagnósticos pasaron exitosamente!")
    print("   El entorno está listo para ejecutar tests reales de LLM")
    return True

def show_test_commands():
    """Mostrar comandos de test recomendados"""
    print("\n🧪 Comandos de test recomendados:")
    print("=" * 40)
    print("# Todos los tests reales:")
    print("pytest tests/test_llm_service.py::TestLLMAnalysisServiceRealAPI -v -s")
    print()
    print("# Solo test rápido:")
    print("pytest tests/test_llm_service.py::TestLLMAnalysisServiceRealAPI::test_analyze_normativa_real_api_short_content -v -s")
    print()
    print("# Solo tests de integración:")
    print("pytest tests/test_llm_service.py -m integration -v -s")
    print()
    print("# Test específico con output detallado:")
    print("pytest tests/test_llm_service.py::TestLLMAnalysisServiceRealAPI::test_analyze_normativa_real_api_full_content -v -s")

if __name__ == "__main__":
    success = diagnose_llm_test_environment()
    
    if success:
        show_test_commands()
        print("\n✅ RESULTADO: Entorno listo para tests de LLM")
        sys.exit(0)
    else:
        print("\n❌ RESULTADO: Hay problemas en el entorno")
        print("\n💡 Pasos para solucionar:")
        print("   1. Configurar GOOGLE_API_KEY en .env")
        print("   2. Instalar dependencias: pip install -r requirements.txt")
        print("   3. Verificar conectividad a internet")
        print("   4. Verificar cuota de Gemini API")
        sys.exit(1)