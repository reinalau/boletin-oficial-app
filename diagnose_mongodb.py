#!/usr/bin/env python3
"""
Script de diagnóstico detallado para MongoDB
"""

import os
import sys
import traceback
from dotenv import load_dotenv

def diagnose_mongodb():
    """Diagnóstico completo de MongoDB"""
    
    print("🔍 Diagnóstico Completo de MongoDB")
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
    
    # 2. Verificar variables de entorno
    print("\n2️⃣ Verificando variables de entorno...")
    required_vars = {
        'MONGODB_CONNECTION_STRING': 'Connection string de MongoDB',
        'MONGODB_DATABASE': 'Nombre de la base de datos',
        'MONGODB_COLLECTION': 'Nombre de la colección'
    }
    
    all_vars_ok = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            if var == 'MONGODB_CONNECTION_STRING':
                # Mostrar solo parte del connection string por seguridad
                masked_value = value[:30] + "..." + value[-20:] if len(value) > 50 else value
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NO CONFIGURADA ({description})")
            all_vars_ok = False
    
    if not all_vars_ok:
        print("\n❌ Faltan variables de entorno requeridas")
        return False
    
    # 3. Verificar dependencias
    print("\n3️⃣ Verificando dependencias...")
    try:
        import pymongo
        print(f"✅ pymongo: {pymongo.__version__}")
    except ImportError as e:
        print(f"❌ pymongo no instalado: {e}")
        return False
    
    try:
        from services.config_service import config_service
        print("✅ config_service importado")
    except ImportError as e:
        print(f"❌ Error importando config_service: {e}")
        return False
    
    try:
        from services.database_service import MongoDBService
        print("✅ MongoDBService importado")
    except ImportError as e:
        print(f"❌ Error importando MongoDBService: {e}")
        return False
    
    # 4. Probar configuración
    print("\n4️⃣ Probando configuración...")
    try:
        config = config_service.get_mongodb_config()
        print("✅ Configuración de MongoDB cargada")
        print(f"   - Database: {config['database']}")
        print(f"   - Collection: {config['collection']}")
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False
    
    # 5. Probar conexión básica con pymongo
    print("\n5️⃣ Probando conexión básica con pymongo...")
    try:
        from pymongo import MongoClient
        
        connection_string = os.getenv('MONGODB_CONNECTION_STRING')
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        
        # Probar conexión
        client.admin.command('ping')
        print("✅ Conexión básica exitosa")
        
        # Probar acceso a base de datos
        db_name = os.getenv('MONGODB_DATABASE')
        db = client[db_name]
        print(f"✅ Acceso a base de datos '{db_name}' exitoso")
        
        # Probar acceso a colección
        collection_name = os.getenv('MONGODB_COLLECTION')
        collection = db[collection_name]
        print(f"✅ Acceso a colección '{collection_name}' exitoso")
        
        # Probar operación básica
        test_doc = {"test": "connection", "timestamp": "2024-07-31"}
        result = collection.insert_one(test_doc)
        print(f"✅ Inserción de prueba exitosa: {result.inserted_id}")
        
        # Limpiar documento de prueba
        collection.delete_one({"_id": result.inserted_id})
        print("✅ Limpieza de documento de prueba exitosa")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error en conexión básica: {e}")
        print(f"   Tipo de error: {type(e).__name__}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False
    
    # 6. Probar con MongoDBService
    print("\n6️⃣ Probando con MongoDBService...")
    try:
        db_service = MongoDBService()
        print("✅ MongoDBService inicializado")
        
        # Probar operación básica
        test_data = {
            'fecha': '2024-07-31-test',
            'seccion': 'test',
            'pdf_url': 'test',
            'contenido_original': 'test',
            'analisis': {'resumen': 'test'},
            'opiniones_expertos': []
        }
        
        doc_id = db_service.save_analysis(test_data)
        print(f"✅ Guardado con MongoDBService exitoso: {doc_id}")
        
        # Recuperar
        retrieved = db_service.get_analysis_by_date('2024-07-31-test')
        if retrieved:
            print("✅ Recuperación exitosa")
        else:
            print("❌ No se pudo recuperar el documento")
        
        # Limpiar
        deleted = db_service.delete_analysis('2024-07-31-test')
        print(f"✅ Limpieza exitosa: {deleted}")
        
        db_service.close_connection()
        
    except Exception as e:
        print(f"❌ Error con MongoDBService: {e}")
        print(f"   Tipo de error: {type(e).__name__}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False
    
    print("\n🎉 ¡Todos los diagnósticos pasaron exitosamente!")
    print("   Tu configuración de MongoDB está funcionando correctamente")
    return True

def show_troubleshooting_tips():
    """Muestra tips de troubleshooting"""
    print("\n🔧 Tips de Troubleshooting:")
    print("=" * 30)
    print("1. Verifica que tu IP esté en la whitelist de MongoDB Atlas")
    print("2. Verifica que el usuario tenga permisos de lectura/escritura")
    print("3. Verifica que el cluster esté activo")
    print("4. Verifica que el connection string sea correcto")
    print("5. Verifica que no haya firewall bloqueando la conexión")

if __name__ == "__main__":
    success = diagnose_mongodb()
    
    if not success:
        show_troubleshooting_tips()
        sys.exit(1)
    else:
        print("\n✅ MongoDB está funcionando correctamente")
        sys.exit(0)