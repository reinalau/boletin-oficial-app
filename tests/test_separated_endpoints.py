#!/usr/bin/env python3
"""
Script de prueba para los endpoints separados del Boletín Oficial
Prueba tanto el análisis del boletín como las opiniones de expertos por separado
"""

import json
import requests
import sys
from datetime import datetime, timedelta

def test_separated_endpoints(base_url):
    """
    Prueba los endpoints separados
    
    Args:
        base_url: URL base de la API Lambda
    """
    print("🧪 Iniciando pruebas de endpoints separados...")
    print(f"📡 URL base: {base_url}")
    print("-" * 60)
    
    # Fecha de prueba (ayer para asegurar que existe contenido)
    test_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Test 1: Análisis del boletín solamente
    print("🔍 Test 1: Análisis del boletín")
    print(f"📅 Fecha: {test_date}")
    
    boletin_payload = {
        "action": "analyze_boletin",
        "fecha": test_date,
        "forzar_reanalisis": False
    }
    
    try:
        print("📤 Enviando solicitud de análisis del boletín...")
        response = requests.post(
            base_url,
            headers=headers,
            json=boletin_payload,
            timeout=120
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                analysis_data = data.get('data', {})
                print("✅ Análisis del boletín exitoso")
                print(f"📅 Fecha analizada: {analysis_data.get('fecha')}")
                print(f"📝 Resumen: {analysis_data.get('analisis', {}).get('resumen', 'N/A')[:100]}...")
                print(f"🔢 Cambios principales: {len(analysis_data.get('analisis', {}).get('cambios_principales', []))}")
                print(f"🏷️ Áreas afectadas: {analysis_data.get('analisis', {}).get('areas_afectadas', [])}")
                print(f"💾 Desde caché: {analysis_data.get('metadatos', {}).get('desde_cache', False)}")
                
                # Verificar que no hay opiniones de expertos
                expert_opinions = analysis_data.get('opiniones_expertos', [])
                print(f"👥 Opiniones de expertos: {len(expert_opinions)} (debería ser 0)")
                
                if len(expert_opinions) == 0:
                    print("✅ Correcto: No hay opiniones de expertos en el análisis del boletín")
                else:
                    print("⚠️ Advertencia: Se encontraron opiniones de expertos en el análisis del boletín")
                
            else:
                print(f"❌ Error en análisis del boletín: {data.get('message')}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"📄 Respuesta: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Error en análisis del boletín: {str(e)}")
        return False
    
    print("-" * 60)
    
    # Test 2: Opiniones de expertos
    print("👥 Test 2: Opiniones de expertos")
    print(f"📅 Fecha: {test_date}")
    
    experts_payload = {
        "action": "get_expert_opinions",
        "fecha": test_date
    }
    
    try:
        print("📤 Enviando solicitud de opiniones de expertos...")
        response = requests.post(
            base_url,
            headers=headers,
            json=experts_payload,
            timeout=120
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                expert_data = data.get('data', {})
                print("✅ Análisis de opiniones de expertos exitoso")
                print(f"📅 Fecha: {expert_data.get('fecha')}")
                
                opinions = expert_data.get('opiniones_expertos', [])
                print(f"👥 Opiniones encontradas: {len(opinions)}")
                print(f"💾 Desde caché: {expert_data.get('metadatos', {}).get('desde_cache', False)}")
                
                # Mostrar algunas opiniones
                for i, opinion in enumerate(opinions[:3]):  # Mostrar máximo 3
                    print(f"  📰 Opinión {i+1}:")
                    print(f"    🏢 Medio: {opinion.get('medio', 'N/A')}")
                    print(f"    👤 Autor: {opinion.get('autor', 'N/A')}")
                    print(f"    📝 Resumen: {opinion.get('opinion_resumen', 'N/A')[:100]}...")
                    print(f"    📅 Fecha: {opinion.get('fecha_publicacion', 'N/A')}")
                    print(f"    ⭐ Relevancia: {opinion.get('relevancia', 'N/A')}")
                
                if len(opinions) > 3:
                    print(f"    ... y {len(opinions) - 3} opiniones más")
                
            else:
                print(f"❌ Error en opiniones de expertos: {data.get('message')}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"📄 Respuesta: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Error en opiniones de expertos: {str(e)}")
        return False
    
    print("-" * 60)
    
    # Test 3: Verificar que el análisis completo sigue funcionando (backward compatibility)
    print("🔄 Test 3: Análisis completo (backward compatibility)")
    print(f"📅 Fecha: {test_date}")
    
    full_payload = {
        "fecha": test_date,
        "forzar_reanalisis": False
    }
    
    try:
        print("📤 Enviando solicitud de análisis completo...")
        response = requests.post(
            base_url,
            headers=headers,
            json=full_payload,
            timeout=180
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                full_data = data.get('data', {})
                print("✅ Análisis completo exitoso")
                print(f"📅 Fecha: {full_data.get('fecha')}")
                print(f"📝 Tiene análisis: {'Sí' if full_data.get('analisis') else 'No'}")
                print(f"👥 Tiene opiniones: {'Sí' if full_data.get('opiniones_expertos') else 'No'}")
                print(f"💾 Desde caché: {full_data.get('metadatos', {}).get('desde_cache', False)}")
                
            else:
                print(f"❌ Error en análisis completo: {data.get('message')}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"📄 Respuesta: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Error en análisis completo: {str(e)}")
        return False
    
    print("-" * 60)
    print("🎉 Todas las pruebas completadas exitosamente!")
    return True

def main():
    """Función principal"""
    if len(sys.argv) != 2:
        print("Uso: python test_separated_endpoints.py <LAMBDA_URL>")
        print("Ejemplo: python test_separated_endpoints.py https://abc123.lambda-url.us-east-1.on.aws/")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print("🚀 Iniciando pruebas de endpoints separados del Boletín Oficial")
    print(f"⏰ Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    success = test_separated_endpoints(base_url)
    
    if success:
        print("\n✅ Todas las pruebas pasaron correctamente")
        sys.exit(0)
    else:
        print("\n❌ Algunas pruebas fallaron")
        sys.exit(1)

if __name__ == "__main__":
    main()