#!/usr/bin/env python3
"""
Script para debuggear qué se guardó exactamente en MongoDB
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pprint import pprint

load_dotenv()

def debug_mongodb_records():
    """Ver exactamente qué hay en la base de datos"""
    
    print("🔍 Debugging MongoDB Records")
    print("=" * 40)
    
    try:
        # Conectar
        client = MongoClient(os.getenv('MONGODB_CONNECTION_STRING'))
        db = client[os.getenv('MONGODB_DATABASE')]
        collection = db[os.getenv('MONGODB_COLLECTION')]
        
        print(f"📋 Base de datos: {os.getenv('MONGODB_DATABASE')}")
        print(f"📋 Colección: {os.getenv('MONGODB_COLLECTION')}")
        
        # Contar documentos
        total_docs = collection.count_documents({})
        print(f"📊 Total de documentos: {total_docs}")
        
        if total_docs == 0:
            print("❌ No hay documentos en la colección")
            return
        
        print("\n📄 Documentos en la colección:")
        print("-" * 50)
        
        # Mostrar todos los documentos
        for i, doc in enumerate(collection.find().limit(10)):
            print(f"\n🔸 Documento {i+1}:")
            print(f"   _id: {doc.get('_id')}")
            print(f"   fecha: {doc.get('fecha', 'NO TIENE CAMPO FECHA')}")
            print(f"   seccion: {doc.get('seccion', 'NO TIENE CAMPO SECCION')}")
            
            # Mostrar todos los campos del documento
            print("   Todos los campos:")
            for key, value in doc.items():
                if key != '_id':  # Skip _id for readability
                    if isinstance(value, dict):
                        print(f"     {key}: {type(value).__name__} con {len(value)} campos")
                    elif isinstance(value, list):
                        print(f"     {key}: {type(value).__name__} con {len(value)} elementos")
                    else:
                        print(f"     {key}: {value}")
        
        print("\n🔍 Probando búsquedas específicas:")
        print("-" * 40)
        
        # Buscar por fecha específica
        test_dates = ['2025-05-04', '2024-07-31-test', '2024-07-31-simple-test']
        
        for date in test_dates:
            result = collection.find_one({'fecha': date})
            if result:
                print(f"✅ Encontrado documento con fecha '{date}'")
                print(f"   ID: {result['_id']}")
                print(f"   Sección: {result.get('seccion')}")
            else:
                print(f"❌ NO encontrado documento con fecha '{date}'")
        
        # Buscar documentos recientes (últimas 24 horas)
        from datetime import datetime, timedelta
        yesterday = datetime.now() - timedelta(days=1)
        
        print(f"\n🕐 Documentos creados después de {yesterday}:")
        recent_docs = collection.find({
            'metadatos.fecha_creacion': {'$gte': yesterday}
        })
        
        for doc in recent_docs:
            print(f"   - Fecha: {doc.get('fecha')}, Creado: {doc.get('metadatos', {}).get('fecha_creacion')}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    debug_mongodb_records()