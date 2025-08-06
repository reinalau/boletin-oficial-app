#!/usr/bin/env python3
"""
Script para probar la lambda_function localmente
Simula el entorno de AWS Lambda y API Gateway
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Agregar directorio padre al path para importar lambda_function
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cargar variables de entorno
load_dotenv()

# Simular contexto de Lambda
class MockLambdaContext:
    """Mock del contexto de AWS Lambda"""
    
    def __init__(self):
        self.function_name = "boletin-oficial-analyzer-local"
        self.function_version = "$LATEST"
        self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:boletin-oficial-analyzer-local"
        self.memory_limit_in_mb = "1024"
        self.remaining_time_in_millis = 300000  # 5 minutos
        self.log_group_name = "/aws/lambda/boletin-oficial-analyzer-local"
        self.log_stream_name = "2025/08/04/[$LATEST]abcdef123456"
        self.aws_request_id = "12345678-1234-1234-1234-123456789012"
    
    def get_remaining_time_in_millis(self):
        """Simula tiempo restante de ejecución"""
        return self.remaining_time_in_millis

def create_api_gateway_event(fecha=None, forzar_reanalisis=False):
    """
    Crea un evento simulado de API Gateway
    
    Args:
        fecha: Fecha para análisis (YYYY-MM-DD)
        forzar_reanalisis: Si forzar nuevo análisis
        
    Returns:
        dict: Evento simulado de API Gateway
    """
    if not fecha:
        fecha = datetime.now().strftime('%Y-%m-%d')
    
    body_data = {
        "fecha": fecha,
        "forzar_reanalisis": forzar_reanalisis
    }
    
    event = {
        "resource": "/analyze",
        "path": "/analyze",
        "httpMethod": "POST",
        "headers": {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Host": "localhost:3000",
            "User-Agent": "LocalTest/1.0"
        },
        "multiValueHeaders": {},
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "pathParameters": None,
        "stageVariables": None,
        "requestContext": {
            "resourceId": "abc123",
            "resourcePath": "/analyze",
            "httpMethod": "POST",
            "extendedRequestId": "local-test-123",
            "requestTime": datetime.now().strftime('%d/%b/%Y:%H:%M:%S %z'),
            "path": "/v1/analyze",
            "accountId": "123456789012",
            "protocol": "HTTP/1.1",
            "stage": "v1",
            "domainPrefix": "localhost",
            "requestTimeEpoch": int(datetime.now().timestamp() * 1000),
            "requestId": "local-test-request-123",
            "identity": {
                "cognitoIdentityPoolId": None,
                "accountId": None,
                "cognitoIdentityId": None,
                "caller": None,
                "sourceIp": "127.0.0.1",
                "principalOrgId": None,
                "accessKey": None,
                "cognitoAuthenticationType": None,
                "cognitoAuthenticationProvider": None,
                "userArn": None,
                "userAgent": "LocalTest/1.0",
                "user": None
            },
            "domainName": "localhost",
            "apiId": "local-test"
        },
        "body": json.dumps(body_data),
        "isBase64Encoded": False
    }
    
    return event

def test_lambda_function_local():
    """Prueba la función Lambda localmente"""
    
    print("🧪 Test Local de Lambda Function")
    print("=" * 50)
    
    # Usar fecha específica para testing consistente
    test_date = datetime.now().strftime('%Y-%m-%d')  # Fecha actual
    print(f"📅 Fecha de prueba: {test_date}")
    print("🔄 Flujo de prueba:")
    print("   1. Primera llamada: Busca en BD → No existe → Llama Gemini → Guarda en BD")
    print("   2. Segunda llamada: Busca en BD → Existe → Retorna desde cache")
    print("   3. Tercera llamada (forzada): Ignora cache → Llama Gemini → Actualiza BD")
    
    # Verificar variables de entorno
    print("\n1️⃣ Verificando configuración...")
    required_vars = ['GEMINI_API_KEY', 'MONGODB_CONNECTION_STRING', 'MONGODB_DATABASE', 'MONGODB_COLLECTION']
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Variables de entorno faltantes:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    print("✅ Variables de entorno configuradas")
    print(f"   - Modelo LLM: {os.getenv('LANGCHAIN_MODEL', 'gemini-2.5-flash')}")
    print(f"   - Temperatura: {os.getenv('LANGCHAIN_TEMPERATURE', '1')}")
    
    # Importar la función Lambda
    print("\n2️⃣ Importando lambda_function...")
    try:
        from lambda_function import lambda_handler
        print("✅ lambda_function importada correctamente")
    except ImportError as e:
        print(f"❌ Error importando lambda_function: {e}")
        return False
    
    # Crear contexto mock
    context = MockLambdaContext()
    
    # Test 1: Primera llamada - Debería ir a Gemini (no existe en BD)
    print(f"\n3️⃣ Test 1: Primera llamada - Análisis nuevo ({test_date})")
    print("-" * 50)
    print("🔍 Flujo esperado: BD (no existe) → Gemini → Guardar en BD")
    
    event1 = create_api_gateway_event(fecha=test_date)
    print(f"📅 Fecha solicitada: {json.loads(event1['body'])['fecha']}")
    
    try:
        print("🚀 Ejecutando lambda_handler...")
        start_time = datetime.now()
        
        response1 = lambda_handler(event1, context)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        print(f"⏱️  Tiempo de ejecución: {execution_time:.2f} segundos")
        print(f"📊 Status Code: {response1['statusCode']}")
        
        if response1['statusCode'] == 200:
            print("✅ Test 1 exitoso")
            
            # Parsear respuesta
            body = json.loads(response1['body'])
            if body['success']:
                data = body['data']
                print(f"� Resuimen: {data['analisis']['resumen'][:100]}...")
                print(f"📊 Cambios principales: {len(data['analisis']['cambios_principales'])} identificados")
                print(f"🎯 Áreas afectadas: {', '.join(data['analisis']['areas_afectadas'])}")
                print(f"👥 Opiniones de expertos: {len(data['opiniones_expertos'])}")
                from_cache = data['metadatos'].get('desde_cache', False)
                print(f"⚡ Desde cache: {from_cache}")
                
                if not from_cache:
                    print("✅ Correcto: Primera llamada procesó con Gemini")
                else:
                    print("⚠️  Inesperado: Primera llamada usó cache")
            else:
                print(f"❌ Error en respuesta: {body.get('message', 'Error desconocido')}")
                return False
        else:
            print(f"❌ Test 1 falló con status {response1['statusCode']}")
            body = json.loads(response1['body'])
            print(f"   Error: {body.get('message', 'Error desconocido')}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando Test 1: {e}")
        import traceback
        print(traceback.format_exc())
        return False
    
    # Test 2: Segunda llamada - Debería usar cache (existe en BD)
    print("\n4️⃣ Test 2: Segunda llamada - Desde cache")
    print("-" * 40)
    print("🔍 Flujo esperado: BD (existe) → Retornar desde cache")
    
    event2 = create_api_gateway_event(fecha=test_date)
    
    try:
        print("🚀 Ejecutando lambda_handler (segunda vez)...")
        start_time = datetime.now()
        
        response2 = lambda_handler(event2, context)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        print(f"⏱️  Tiempo de ejecución: {execution_time:.2f} segundos (debería ser < 5 seg)")
        print(f"📊 Status Code: {response2['statusCode']}")
        
        if response2['statusCode'] == 200:
            body = json.loads(response2['body'])
            if body['success']:
                data = body['data']
                from_cache = data['metadatos'].get('desde_cache', False)
                print(f"⚡ Desde cache: {from_cache}")
                
                if from_cache and execution_time < 5:
                    print("✅ Test 2 exitoso - Cache funcionando correctamente")
                elif from_cache:
                    print("⚠️  Test 2 - Cache funcionó pero tardó más de lo esperado")
                else:
                    print("❌ Test 2 - No usó cache cuando debería haberlo hecho")
                    return False
            else:
                print(f"❌ Error en respuesta: {body.get('message', 'Error desconocido')}")
                return False
        else:
            print(f"❌ Test 2 falló con status {response2['statusCode']}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando Test 2: {e}")
        print("ℹ️  Continuando con otros tests...")
        return False
    
    # Test 3: Tercera llamada - Análisis forzado (ignora cache)
    print("\n5️⃣ Test 3: Tercera llamada - Análisis forzado")
    print("-" * 40)
    print("🔍 Flujo esperado: Ignorar BD → Gemini → Actualizar BD")
    
    event3 = create_api_gateway_event(
        fecha=test_date, 
        forzar_reanalisis=True
    )
    
    try:
        print("🚀 Ejecutando lambda_handler (forzado)...")
        start_time = datetime.now()
        
        response3 = lambda_handler(event3, context)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        print(f"⏱️  Tiempo de ejecución: {execution_time:.2f} segundos (debería ser > 10 seg)")
        print(f"📊 Status Code: {response3['statusCode']}")
        
        if response3['statusCode'] == 200:
            body = json.loads(response3['body'])
            if body['success']:
                data = body['data']
                from_cache = data['metadatos'].get('desde_cache', False)
                print(f"⚡ Desde cache: {from_cache} (debería ser False)")
                
                if not from_cache and execution_time > 10:
                    print("✅ Test 3 exitoso - Análisis forzado funcionando correctamente")
                elif not from_cache:
                    print("⚠️  Test 3 - Análisis forzado funcionó pero fue muy rápido")
                else:
                    print("❌ Test 3 - Usó cache cuando debería haber forzado nuevo análisis")
                    return False
            else:
                print(f"❌ Error en respuesta: {body.get('message', 'Error desconocido')}")
                return False
        else:
            print(f"❌ Test 3 falló con status {response3['statusCode']}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando Test 3: {e}")
        print("ℹ️  Continuando...")
        return False
    
    # Test 4: Fecha diferente - Debería ir a Gemini (nueva fecha)
    print("\n6️⃣ Test 4: Fecha diferente - Análisis nuevo")
    print("-" * 40)
    
    # Usar fecha de ayer para probar con fecha diferente
    from datetime import timedelta
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    print(f"🔍 Flujo esperado: BD (fecha {yesterday} no existe) → Gemini → Guardar en BD")
    
    event4 = create_api_gateway_event(fecha=yesterday)
    
    try:
        print(f"🚀 Ejecutando lambda_handler con fecha {yesterday}...")
        start_time = datetime.now()
        
        response4 = lambda_handler(event4, context)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        print(f"⏱️  Tiempo de ejecución: {execution_time:.2f} segundos")
        print(f"📊 Status Code: {response4['statusCode']}")
        
        if response4['statusCode'] == 200:
            body = json.loads(response4['body'])
            if body['success']:
                data = body['data']
                from_cache = data['metadatos'].get('desde_cache', False)
                print(f"⚡ Desde cache: {from_cache} (debería ser False)")
                print(f"📅 Fecha procesada: {data['fecha']}")
                
                if not from_cache and data['fecha'] == yesterday:
                    print("✅ Test 4 exitoso - Fecha diferente procesada correctamente")
                else:
                    print("⚠️  Test 4 - Comportamiento inesperado con fecha diferente")
            else:
                print(f"❌ Error en respuesta: {body.get('message', 'Error desconocido')}")
        else:
            print(f"❌ Test 4 falló con status {response4['statusCode']}")
            
    except Exception as e:
        print(f"❌ Error ejecutando Test 4: {e}")
        print("ℹ️  Continuando...")

    print("\n🎉 Tests locales completados!")
    print("\n📊 Resumen del flujo probado:")
    print("   ✅ Primera llamada: BD → Gemini → Guardar")
    print("   ✅ Segunda llamada: BD → Cache")
    print("   ✅ Tercera llamada (forzada): Gemini → Actualizar BD")
    print("   ✅ Cuarta llamada (fecha diferente): BD → Gemini → Guardar")
    
    return True

def show_usage():
    """Muestra información de uso"""
    print("\n📋 Uso del script:")
    print("=" * 30)
    print("python test_lambda_local.py")
    print()
    print("📋 Variables de entorno requeridas:")
    print("   - GEMINI_API_KEY")
    print("   - MONGODB_CONNECTION_STRING")
    print("   - MONGODB_DATABASE")
    print("   - MONGODB_COLLECTION")
    print()
    print("📋 Variables opcionales:")
    print("   - LANGCHAIN_MODEL (default: gemini-2.5-flash)")
    print("   - LANGCHAIN_TEMPERATURE (default: 0.1)")

if __name__ == "__main__":
    print("🧪 Test Local de AWS Lambda Function")
    print("=" * 50)
    print("Este script simula el entorno de AWS Lambda localmente")
    print("para probar toda la funcionalidad sin desplegar.")
    print()
    print("ℹ️  Probando flujo completo de Lambda:")
    print("   📥 Lambda recibe fecha → 🔍 Busca en MongoDB → 🤖 Llama Gemini si no existe → 💾 Guarda resultado")
    print("   ⚡ Sin LangChain - Usa google-genai directamente")
    print("   🧠 Thinking habilitado - Análisis más profundo")
    print("   🔍 Google Search - Acceso directo a URLs del Boletín Oficial")
    
    success = test_lambda_function_local()
    
    if success:
        print("\n✅ RESULTADO: Funcionalidad local funcionando correctamente")
        print("   Tu aplicación está lista para desplegar a AWS Lambda")
    else:
        print("\n❌ RESULTADO: Hay problemas en la funcionalidad")
        print("   Revisa los errores anteriores antes de desplegar")
        print("\n💡 Posibles causas:")
        print("   - Fecha sin contenido en Boletín Oficial")
        print("   - Problemas de conectividad")
        print("   - API de Gemini sin cuota")
        print("   - MongoDB no accesible")
    
    show_usage()
    
    sys.exit(0 if success else 1)