#!/usr/bin/env python3
"""
Test simplificado de MongoDB para evitar problemas de recursión
"""

import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

def test_simple_mongodb():
    """Test directo con pymongo, sin usar los servicios"""
    
    print("🧪 Test Simplificado de MongoDB")
    print("=" * 40)
    
    # Obtener configuración
    conn_str = os.getenv('MONGODB_CONNECTION_STRING')
    db_name = os.getenv('MONGODB_DATABASE')
    collection_name = os.getenv('MONGODB_COLLECTION')
    
    print(f"📋 Configuración:")
    print(f"   Database: {db_name}")
    print(f"   Collection: {collection_name}")
    print(f"   Connection: {conn_str[:50]}...")
    
    try:
        print("\n🔌 Conectando a MongoDB...")
        client = MongoClient(conn_str, serverSelectionTimeoutMS=10000)
        
        # Test de ping
        client.admin.command('ping')
        print("✅ Ping exitoso")
        
        # Acceder a la base de datos y colección
        db = client[db_name]
        collection = db[collection_name]
        print("✅ Acceso a base de datos y colección exitoso")
        
        # Crear documento de prueba
        test_doc = {
            'fecha': '2025-07-31-simple-test',
            'seccion': 'test',
            'contenido_original': 'Test simplificado de conexión',
            'analisis': {
                'resumen': 'Test de conectividad directa',
                'cambios_principales': [],
                'areas_afectadas': ['testing']
            },
            'opiniones_expertos': [],
            'metadatos': {
                'fecha_creacion': datetime.utcnow(),
                'version_analisis': '1.0',
                'estado': 'test'
            }
        }
        
        print("\n💾 Insertando documento de prueba...")
        result = collection.insert_one(test_doc)
        doc_id = str(result.inserted_id)
        print(f"✅ Documento insertado con ID: {doc_id}")
        
        # Verificar que se insertó
        found_doc = collection.find_one({'_id': result.inserted_id})
        if found_doc:
            print("✅ Documento encontrado en la base de datos")
            print(f"   Fecha: {found_doc['fecha']}")
            print(f"   Resumen: {found_doc['analisis']['resumen']}")
        else:
            print("❌ Documento no encontrado")
            return False
        
        # Buscar por fecha
        print("\n🔍 Buscando por fecha...")
        found_by_date = collection.find_one({'fecha': '2024-07-31-simple-test'})
        if found_by_date:
            print("✅ Búsqueda por fecha exitosa")
        else:
            print("❌ No se encontró por fecha")
        
        # Contar documentos
        count = collection.count_documents({})
        print(f"📊 Total de documentos en la colección: {count}")
        
        # Limpiar documento de prueba
        print("\n🧹 Limpiando documento de prueba...")
        delete_result = collection.delete_one({'_id': result.inserted_id})
        if delete_result.deleted_count > 0:
            print("✅ Documento de prueba eliminado")
        else:
            print("⚠️  No se pudo eliminar el documento de prueba")
        
        # Cerrar conexión
        client.close()
        print("✅ Conexión cerrada")
        
        print("\n🎉 ¡Test simplificado exitoso!")
        print("   Tu MongoDB está funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"   Tipo: {type(e).__name__}")
        
        # Información adicional para debugging
        import traceback
        print(f"\n🔧 Traceback completo:")
        print(traceback.format_exc())
        
        return False

if __name__ == "__main__":
    success = test_simple_mongodb()
    
    if success:
        print("\n✅ RESULTADO: MongoDB funciona correctamente")
        sys.exit(0)
    else:
        print("\n❌ RESULTADO: Hay problemas con MongoDB")
        sys.exit(1)