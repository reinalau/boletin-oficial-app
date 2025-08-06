#!/usr/bin/env python3
"""
Test del LLM service directo basado en geminiPrompt.py
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_llm_direct_service():
    """Prueba el LLM service directo"""
    
    print("🧪 Test LLM Service Direct")
    print("=" * 35)
    
    # Verificar API key
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY o GOOGLE_API_KEY no configurada")
        return False
    
    print(f"✅ API Key configurada: {api_key[:10]}...{api_key[-5:]}")
    print(f"✅ Modelo: {os.getenv('LANGCHAIN_MODEL', 'gemini-2.5-flash')}")
    
    # Importar servicio
    try:
        from services.llm_service_direct import LLMAnalysisServiceDirect
        print("✅ LLMAnalysisServiceDirect importado")
    except ImportError as e:
        print(f"❌ Error importando: {e}")
        return False
    
    # Inicializar servicio
    try:
        llm_service = LLMAnalysisServiceDirect()
        print("✅ Servicio inicializado")
    except Exception as e:
        print(f"❌ Error inicializando: {e}")
        import traceback
        print(traceback.format_exc())
        return False
    
    # Probar análisis (siempre usa fecha actual)
    print(f"\n🚀 Probando análisis con fecha actual...")
    print("⏳ Esto puede tomar 30-90 segundos con thinking habilitado...")
    
    try:
        test_date = "2025-08-04"
        result = llm_service.analyze_normativa(test_date)
        
        print("✅ Análisis completado!")
        print(f"📋 Tipo de resultado: {type(result)}")
        
        if isinstance(result, dict):
            print("\n📊 Resultados:")
            print("-" * 30)
            
            if 'resumen' in result:
                resumen = result['resumen']
                print(f"📝 Resumen: {resumen[:200]}...")
            
            if 'cambios_principales' in result:
                cambios = result['cambios_principales']
                print(f"📊 Cambios principales: {len(cambios)} identificados")
                
                for i, cambio in enumerate(cambios[:3]):  # Mostrar primeros 3
                    print(f"   {i+1}. {cambio.get('tipo', 'N/A')} {cambio.get('numero', 'N/A')}")
                    print(f"      {cambio.get('titulo', 'Sin título')[:80]}...")
            
            if 'areas_afectadas' in result:
                areas = result['areas_afectadas']
                print(f"🎯 Áreas afectadas: {', '.join(areas)}")
            
            if 'impacto_estimado' in result:
                impacto = result['impacto_estimado']
                print(f"💡 Impacto: {impacto[:150]}...")
            
            # Verificar si hay errores
            if result.get('error'):
                print(f"⚠️  Error en análisis: {result.get('error_message', 'Error desconocido')}")
                return False
            
            return True
        else:
            print(f"❌ Resultado inesperado: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error en análisis: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🧪 Test del LLM Service Direct")
    print("=" * 40)
    print("Este test usa el nuevo servicio basado en")
    print("geminiPrompt.py con thinking y Google Search.")
    print("Siempre analiza la fecha actual (01/08/2025).")
    
    success = test_llm_direct_service()
    
    if success:
        print("\n✅ RESULTADO: LLM Direct funcionando!")
        print("   El servicio puede analizar el Boletín Oficial")
        print("   usando thinking y Google Search")
    else:
        print("\n❌ RESULTADO: Problemas con LLM Direct")
        print("   Verifica la configuración de Gemini")
    
    print("\n💡 Próximo paso:")
    print("   Integrar en lambda_function.py")