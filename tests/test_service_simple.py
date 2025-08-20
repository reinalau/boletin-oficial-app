#!/usr/bin/env python3
"""
Test del MongoDBService con inicialización simplificada
"""

import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

class SimpleMongoDBService:
    """Versión simplificada del MongoDBService para evitar recursión"""
    
    def __init__(self):
        """Inicialización simple sin config_service"""
        self.connection_string = os.getenv('MONGODB_CONNECTION_STRING')
        self.database_name = os.getenv('MONGODB_DATABASE')
        self.collection_name = os.getenv('MONGODB_COLLECTION')
        
        if not all([self.connection_string, self.database_name, self.collection_name]):
            raise ValueError("Faltan variables de entorno de MongoDB")
        
        self.client = None
        self.database = None
        self.collection = None
        
        self._connect()
    
    def _connect(self):
        """Conectar a MongoDB"""
        self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=10000)
        self.database = self.client[self.database_name]
        self.collection = self.database[self.collection_name]
        
        # Test de conexión
        self.client.admin.command('ping')
    
    def save_analysis(self, analysis_data):
        """Guardar análisis simplificado"""
        # Agregar metadatos básicos
        analysis_data['metadatos'] = {
            'fecha_creacion': datetime.utcnow(),
            'version_analisis': '1.0',
            'estado': 'completado'
        }
        
        # Insertar documento
        result = self.collection.insert_one(analysis_data)
        return str(result.inserted_id)
    
    def get_analysis_by_date(self, fecha):
        """Obtener análisis por fecha"""
        return self.collection.find_one({'fecha': fecha})
    
    def delete_analysis(self, fecha):
        """Eliminar análisis por fecha"""
        result = self.collection.delete_one({'fecha': fecha})
        return result.deleted_count > 0
    
    def close(self):
        """Cerrar conexión"""
        if self.client:
            self.client.close()

def test_simple_service():
    """Test del servicio simplificado"""
    
    print("🧪 Test del MongoDBService Simplificado")
    print("=" * 45)
    
    try:
        print("🔌 Inicializando servicio...")
        service = SimpleMongoDBService()
        print("✅ Servicio inicializado correctamente")
        
        # Datos de prueba
        test_data = {
            'fecha': '2024-07-31-service-test',
            'seccion': 'legislacion_avisos_oficiales',
            'pdf_url': 'https://example.com/test.pdf',
            'contenido_original': 'Test del servicio simplificado',
            'analisis': {
                'resumen': 'Test de servicio sin recursión',
                'cambios_principales': [
                    {
                        'tipo': 'test',
                        'numero': 'TEST/2024',
                        'titulo': 'Test de servicio',
                        'descripcion': 'Verificación de funcionalidad',
                        'impacto': 'bajo'
                    }
                ],
                'impacto_estimado': 'Test exitoso',
                'areas_afectadas': ['testing']
            },
            'opiniones_expertos': []
        }
        
        print("\n💾 Guardando análisis...")
        doc_id = service.save_analysis(test_data)
        print(f"✅ Análisis guardado con ID: {doc_id}")
        
        print("\n📖 Recuperando análisis...")
        retrieved = service.get_analysis_by_date('2024-07-31-service-test')
        if retrieved:
            print("✅ Análisis recuperado exitosamente")
            print(f"   Fecha: {retrieved['fecha']}")
            print(f"   Resumen: {retrieved['analisis']['resumen']}")
        else:
            print("❌ No se pudo recuperar el análisis")
            return False
        
        print("\n🧹 Limpiando datos de prueba...")
        deleted = service.delete_analysis('2024-07-31-service-test')
        print(f"✅ Datos eliminados: {deleted}")
        
        service.close()
        print("✅ Conexión cerrada")
        
        print("\n🎉 ¡Test del servicio simplificado exitoso!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"   Tipo: {type(e).__name__}")
        
        import traceback
        print(f"\n🔧 Traceback:")
        print(traceback.format_exc())
        
        return False

if __name__ == "__main__":
    success = test_simple_service()
    
    if success:
        print("\n✅ RESULTADO: El servicio simplificado funciona")
       
    else:
        print("\n❌ RESULTADO: Hay problemas básicos")
    
    sys.exit(0 if success else 1)