"""
MongoDB service for the Boletin Oficial application.
Handles database connections, operations, and data validation.
"""

import pymongo
from pymongo import MongoClient
from pymongo.errors import (
    ConnectionFailure, 
    ServerSelectionTimeoutError, 
    OperationFailure,
    DuplicateKeyError,
    NetworkTimeout
)
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import time
import threading
from utils.error_handler import error_handler, ErrorCode


class MongoDBService:
    """Service for MongoDB Atlas operations with connection pooling and error handling."""
    
    def __init__(self):
        """Inicializa conexión a MongoDB Atlas"""
        self._client = None
        self._database = None
        self._collection = None
        self._connection_lock = threading.Lock()
        self._last_connection_check = None
        self._connection_check_interval = 300  # 5 minutes
        self._max_retry_attempts = 3
        self._retry_delay = 1  # seconds
        
        # Load configuration directly from environment to avoid recursion
        import os
        self._connection_string = os.getenv('MONGODB_CONNECTION_STRING')
        self._database_name = os.getenv('MONGODB_DATABASE')
        self._collection_name = os.getenv('MONGODB_COLLECTION')
        
        # Validate required configuration
        if not all([self._connection_string, self._database_name, self._collection_name]):
            raise ValueError("Missing required MongoDB configuration. Check MONGODB_CONNECTION_STRING, MONGODB_DATABASE, and MONGODB_COLLECTION environment variables.")
        
        # Initialize connection
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize MongoDB connection with connection pooling."""
        try:
            # Configure connection with pooling options
            client_options = {
                'serverSelectionTimeoutMS': 5000,  # 5 seconds
                'connectTimeoutMS': 10000,  # 10 seconds
                'socketTimeoutMS': 30000,  # 30 seconds
                'maxPoolSize': 10,  # Maximum connections in pool
                'minPoolSize': 1,   # Minimum connections in pool
                'maxIdleTimeMS': 30000,  # Close connections after 30s idle
                'retryWrites': True,
                'retryReads': True,
                'w': 'majority',  # Write concern
                'readPreference': 'primary'
            }
            
            self._client = MongoClient(self._connection_string, **client_options)
            
            # Test connection
            self._client.admin.command('ping')
            
            # Get database and collection references
            self._database = self._client[self._database_name]
            self._collection = self._database[self._collection_name]
            
            # Create indexes for better performance
            self._create_indexes()
            
            self._last_connection_check = datetime.utcnow()
            
            error_handler.log_info('mongodb_connection_initialized', {
                'database': self._database_name,
                'collection': self._collection_name,
                'pool_size': client_options['maxPoolSize']
            })
            
        except Exception as e:
            error_handler.log_error(ErrorCode.DATABASE_CONNECTION_ERROR, e, {
                'action': 'initialize_connection',
                'database': self._database_name
            })
            raise
    
    def _create_indexes(self):
        """Create database indexes for optimal performance."""
        try:
            # Index on fecha for fast date queries
            self._collection.create_index([("fecha", pymongo.ASCENDING)], unique=True)
            
            # Index on metadatos.fecha_creacion for sorting
            self._collection.create_index([("metadatos.fecha_creacion", pymongo.DESCENDING)])
            
            # Index on metadatos.estado for filtering
            self._collection.create_index([("metadatos.estado", pymongo.ASCENDING)])
            
            # Compound index for common queries
            self._collection.create_index([
                ("fecha", pymongo.ASCENDING),
                ("seccion", pymongo.ASCENDING)
            ])
            
            error_handler.log_info('mongodb_indexes_created', {
                'collection': self._collection_name
            })
            
        except Exception as e:
            # Index creation errors are not critical, log but don't fail
            error_handler.log_warning('mongodb_index_creation_failed', {
                'error': str(e),
                'collection': self._collection_name
            })
    
    def _ensure_connection(self):
        """Ensure database connection is active, reconnect if necessary."""
        with self._connection_lock:
            current_time = datetime.utcnow()
            
            # Check if we need to verify connection
            if (self._last_connection_check is None or 
                (current_time - self._last_connection_check).total_seconds() > self._connection_check_interval):
                
                try:
                    # Test connection
                    self._client.admin.command('ping')
                    self._last_connection_check = current_time
                    
                except Exception as e:
                    error_handler.log_warning('mongodb_connection_lost', {
                        'error': str(e),
                        'attempting_reconnection': True
                    })
                    
                    # Attempt to reconnect
                    self._reconnect()
    
    def _reconnect(self):
        """Reconnect to MongoDB with exponential backoff."""
        for attempt in range(self._max_retry_attempts):
            try:
                # Close existing connection
                if self._client:
                    self._client.close()
                
                # Wait with exponential backoff
                if attempt > 0:
                    delay = self._retry_delay * (2 ** (attempt - 1))
                    time.sleep(delay)
                
                # Reinitialize connection
                self._initialize_connection()
                
                error_handler.log_info('mongodb_reconnection_successful', {
                    'attempt': attempt + 1,
                    'database': self._database_name
                })
                return
                
            except Exception as e:
                error_handler.log_warning('mongodb_reconnection_attempt_failed', {
                    'attempt': attempt + 1,
                    'max_attempts': self._max_retry_attempts,
                    'error': str(e)
                })
                
                if attempt == self._max_retry_attempts - 1:
                    error_handler.log_error(ErrorCode.DATABASE_CONNECTION_ERROR, e, {
                        'action': 'reconnect',
                        'attempts': self._max_retry_attempts
                    })
                    raise
    
    def _execute_with_retry(self, operation_func, *args, **kwargs):
        """Execute database operation with retry logic."""
        for attempt in range(self._max_retry_attempts):
            try:
                # Ensure connection is active
                self._ensure_connection()
                
                # Execute operation
                return operation_func(*args, **kwargs)
                
            except (ConnectionFailure, ServerSelectionTimeoutError, NetworkTimeout) as e:
                error_handler.log_warning('mongodb_operation_connection_error', {
                    'attempt': attempt + 1,
                    'error': str(e),
                    'operation': operation_func.__name__
                })
                
                if attempt == self._max_retry_attempts - 1:
                    raise
                
                # Wait before retry
                time.sleep(self._retry_delay * (attempt + 1))
                
                # Force reconnection on next attempt
                self._last_connection_check = None
                
            except Exception as e:
                # Non-connection errors should not be retried
                error_handler.log_error(ErrorCode.DATABASE_QUERY_ERROR, e, {
                    'operation': operation_func.__name__,
                    'attempt': attempt + 1
                })
                raise
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection status and statistics."""
        try:
            # Test connection
            self._client.admin.command('ping')
            
            # Get server info
            server_info = self._client.server_info()
            
            # Get database stats
            db_stats = self._database.command('dbStats')
            
            return {
                'connected': True,
                'server_version': server_info.get('version'),
                'database': self._database_name,
                'collection': self._collection_name,
                'last_check': self._last_connection_check.isoformat() if self._last_connection_check else None,
                'database_size_mb': round(db_stats.get('dataSize', 0) / (1024 * 1024), 2),
                'collection_count': db_stats.get('collections', 0)
            }
            
        except Exception as e:
            return {
                'connected': False,
                'error': str(e),
                'database': self._database_name,
                'collection': self._collection_name,
                'last_check': self._last_connection_check.isoformat() if self._last_connection_check else None
            }
    
    def close_connection(self):
        """Close database connection and cleanup resources."""
        try:
            if self._client:
                self._client.close()
                self._client = None
                self._database = None
                self._collection = None
                
                error_handler.log_info('mongodb_connection_closed', {
                    'database': self._database_name
                })
                
        except Exception as e:
            error_handler.log_warning('mongodb_connection_close_error', {
                'error': str(e)
            })
    
    def __del__(self):
        """Cleanup on object destruction."""
        self.close_connection()    

    def save_analysis(self, analysis_data: dict) -> str:
        """
        Guarda análisis en la base de datos.
        
        Args:
            analysis_data: Diccionario con los datos del análisis
            
        Returns:
            str: ID del documento guardado
            
        Raises:
            Exception: Si hay error en la validación o guardado
        """
        try:
            # Validate analysis data
            validated_data = self._validate_analysis_data(analysis_data)
            
            # Add metadata
            validated_data['metadatos'] = {
                'fecha_creacion': datetime.utcnow(),
                'version_analisis': '1.0',
                'estado': 'completado',
                **validated_data.get('metadatos', {})
            }
            
            # Execute save operation with retry
            def _save_operation():
                try:
                    result = self._collection.insert_one(validated_data)
                    return str(result.inserted_id)
                except DuplicateKeyError:
                    # If document exists, update it instead (excluding _id from update)
                    update_data = {k: v for k, v in validated_data.items() if k != '_id'}
                    result = self._collection.update_one(
                        {'fecha': validated_data['fecha']},
                        {'$set': update_data},
                        upsert=True
                    )
                    if result.upserted_id:
                        return str(result.upserted_id)
                    else:
                        # Find the existing document ID
                        existing_doc = self._collection.find_one(
                            {'fecha': validated_data['fecha']},
                            {'_id': 1}
                        )
                        return str(existing_doc['_id']) if existing_doc else None
            
            document_id = self._execute_with_retry(_save_operation)
            
            error_handler.log_info('analysis_saved', {
                'document_id': document_id,
                'fecha': validated_data['fecha'],
                'seccion': validated_data.get('seccion')
            })
            
            return document_id
            
        except Exception as e:
            error_handler.handle_database_error(e, {
                'action': 'save_analysis',
                'fecha': analysis_data.get('fecha')
            })
            raise
    
    def get_analysis_by_date(self, date: str) -> Optional[dict]:
        """
        Recupera análisis existente por fecha.
        
        Args:
            date: Fecha en formato YYYY-MM-DD
            
        Returns:
            dict: Datos del análisis o None si no existe
            
        Raises:
            Exception: Si hay error en la consulta
        """
        try:
            # Validate date format
            self._validate_date_format(date)
            
            # Execute query with retry
            def _get_operation():
                return self._collection.find_one(
                    {'fecha': date},
                    {'_id': 0}  # Exclude MongoDB _id from result
                )
            
            result = self._execute_with_retry(_get_operation)
            
            if result:
                error_handler.log_info('analysis_retrieved', {
                    'fecha': date,
                    'found': True
                })
            else:
                error_handler.log_info('analysis_retrieved', {
                    'fecha': date,
                    'found': False
                })
            
            return result
            
        except Exception as e:
            error_handler.handle_database_error(e, {
                'action': 'get_analysis_by_date',
                'fecha': date
            })
            raise
    
    def analysis_exists(self, date: str) -> bool:
        """
        Verifica si ya existe análisis para una fecha.
        
        Args:
            date: Fecha en formato YYYY-MM-DD
            
        Returns:
            bool: True si existe análisis para la fecha
            
        Raises:
            Exception: Si hay error en la consulta
        """
        try:
            # Validate date format
            self._validate_date_format(date)
            
            # Execute query with retry
            def _exists_operation():
                return self._collection.count_documents(
                    {'fecha': date},
                    limit=1
                ) > 0
            
            exists = self._execute_with_retry(_exists_operation)
            
            error_handler.log_info('analysis_existence_checked', {
                'fecha': date,
                'exists': exists
            })
            
            return exists
            
        except Exception as e:
            error_handler.handle_database_error(e, {
                'action': 'analysis_exists',
                'fecha': date
            })
            raise
    
    def get_recent_analyses(self, limit: int = 10) -> List[dict]:
        """
        Obtiene los análisis más recientes.
        
        Args:
            limit: Número máximo de análisis a retornar
            
        Returns:
            list: Lista de análisis ordenados por fecha de creación descendente
        """
        try:
            def _get_recent_operation():
                cursor = self._collection.find(
                    {},
                    {'_id': 0}
                ).sort('metadatos.fecha_creacion', -1).limit(limit)
                return list(cursor)
            
            results = self._execute_with_retry(_get_recent_operation)
            
            error_handler.log_info('recent_analyses_retrieved', {
                'count': len(results),
                'limit': limit
            })
            
            return results
            
        except Exception as e:
            error_handler.handle_database_error(e, {
                'action': 'get_recent_analyses',
                'limit': limit
            })
            raise
    
    def delete_analysis(self, date: str) -> bool:
        """
        Elimina un análisis por fecha.
        
        Args:
            date: Fecha en formato YYYY-MM-DD
            
        Returns:
            bool: True si se eliminó el análisis
        """
        try:
            # Validate date format
            self._validate_date_format(date)
            
            def _delete_operation():
                result = self._collection.delete_one({'fecha': date})
                return result.deleted_count > 0
            
            deleted = self._execute_with_retry(_delete_operation)
            
            error_handler.log_info('analysis_deleted', {
                'fecha': date,
                'deleted': deleted
            })
            
            return deleted
            
        except Exception as e:
            error_handler.handle_database_error(e, {
                'action': 'delete_analysis',
                'fecha': date
            })
            raise
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de los análisis almacenados.
        
        Returns:
            dict: Estadísticas de la colección
        """
        try:
            def _stats_operation():
                # Count total documents
                total_count = self._collection.count_documents({})
                
                # Get date range
                oldest = self._collection.find_one(
                    {},
                    {'fecha': 1},
                    sort=[('fecha', 1)]
                )
                newest = self._collection.find_one(
                    {},
                    {'fecha': 1},
                    sort=[('fecha', -1)]
                )
                
                # Count by status
                status_pipeline = [
                    {'$group': {
                        '_id': '$metadatos.estado',
                        'count': {'$sum': 1}
                    }}
                ]
                status_counts = list(self._collection.aggregate(status_pipeline))
                
                return {
                    'total_analyses': total_count,
                    'oldest_date': oldest['fecha'] if oldest else None,
                    'newest_date': newest['fecha'] if newest else None,
                    'status_counts': {item['_id']: item['count'] for item in status_counts}
                }
            
            stats = self._execute_with_retry(_stats_operation)
            
            error_handler.log_info('analysis_stats_retrieved', stats)
            
            return stats
            
        except Exception as e:
            error_handler.handle_database_error(e, {
                'action': 'get_analysis_stats'
            })
            raise
    
    def _validate_analysis_data(self, data: dict) -> dict:
        """
        Valida los datos del análisis según el esquema esperado.
        
        Args:
            data: Datos del análisis a validar
            
        Returns:
            dict: Datos validados y normalizados
            
        Raises:
            ValueError: Si los datos no son válidos
        """
        if not isinstance(data, dict):
            raise ValueError("Los datos del análisis deben ser un diccionario")
        
        # Required fields
        required_fields = ['fecha', 'seccion']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Campo requerido faltante: {field}")
        
        # Validate date format
        self._validate_date_format(data['fecha'])
        
        # Validate seccion
        valid_sections = ['legislacion_avisos_oficiales']
        if data['seccion'] not in valid_sections:
            raise ValueError(f"Sección inválida: {data['seccion']}. Debe ser una de: {valid_sections}")
        
        # Create validated copy
        validated_data = {
            'fecha': data['fecha'],
            'seccion': data['seccion'],
            'pdf_url': data.get('pdf_url', ''),
            'contenido_original': data.get('contenido_original', ''),
            'analisis': data.get('analisis', {}),
            'opiniones_expertos': data.get('opiniones_expertos', [])
        }
        
        # Validate analisis structure if present
        if validated_data['analisis']:
            self._validate_analysis_structure(validated_data['analisis'])
        
        # Validate opiniones_expertos structure if present
        if validated_data['opiniones_expertos']:
            self._validate_opinions_structure(validated_data['opiniones_expertos'])
        
        return validated_data
    
    def _validate_date_format(self, date_str: str):
        """
        Valida que la fecha esté en formato YYYY-MM-DD.
        
        Args:
            date_str: Fecha como string
            
        Raises:
            ValueError: Si el formato de fecha es inválido
        """
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            raise ValueError(f"Formato de fecha inválido: {date_str}. Debe ser YYYY-MM-DD")
    
    def _validate_analysis_structure(self, analisis: dict):
        """
        Valida la estructura del análisis.
        
        Args:
            analisis: Diccionario con el análisis
            
        Raises:
            ValueError: Si la estructura es inválida
        """
        if not isinstance(analisis, dict):
            raise ValueError("El análisis debe ser un diccionario")
        
        # Optional but expected fields
        expected_fields = ['resumen', 'cambios_principales', 'impacto_estimado', 'areas_afectadas']
        
        # Validate cambios_principales if present
        if 'cambios_principales' in analisis:
            if not isinstance(analisis['cambios_principales'], list):
                raise ValueError("cambios_principales debe ser una lista")
        
        # Validate areas_afectadas if present
        if 'areas_afectadas' in analisis:
            if not isinstance(analisis['areas_afectadas'], list):
                raise ValueError("areas_afectadas debe ser una lista")
    
    def update_analysis_expert_opinions(self, date: str, expert_opinions: list) -> bool:
        """
        Update existing analysis with expert opinions
        
        Args:
            date: Date in YYYY-MM-DD format
            expert_opinions: List of expert opinions to add
            
        Returns:
            bool: True if update was successful
            
        Raises:
            Exception: If there's an error in the update
        """
        try:
            # Validate date format
            self._validate_date_format(date)
            
            # Validate opinions structure
            if expert_opinions:
                self._validate_opinions_structure(expert_opinions)
            
            # Execute update with retry
            def _update_operation():
                result = self._collection.update_one(
                    {'fecha': date},
                    {
                        '$set': {
                            'opiniones_expertos': expert_opinions,
                            'metadatos.fecha_actualizacion_opiniones': datetime.utcnow()
                        }
                    }
                )
                return result.modified_count > 0
            
            updated = self._execute_with_retry(_update_operation)
            
            error_handler.log_info('analysis_expert_opinions_updated', {
                'fecha': date,
                'updated': updated,
                'opinions_count': len(expert_opinions)
            })
            
            return updated
            
        except Exception as e:
            error_handler.log_error(ErrorCode.DATABASE_QUERY_ERROR, e, {
                'action': 'update_analysis_expert_opinions',
                'fecha': date,
                'opinions_count': len(expert_opinions) if expert_opinions else 0
            })
            raise

    def _validate_opinions_structure(self, opiniones: list):
        """
        Valida la estructura de las opiniones de expertos.
        
        Args:
            opiniones: Lista de opiniones
            
        Raises:
            ValueError: Si la estructura es inválida
        """
        if not isinstance(opiniones, list):
            raise ValueError("Las opiniones deben ser una lista")
        
        for i, opinion in enumerate(opiniones):
            if not isinstance(opinion, dict):
                raise ValueError(f"La opinión {i} debe ser un diccionario")
            
            # Check for expected fields
            expected_fields = ['fuente', 'opinion', 'fecha_opinion', 'relevancia']
            for field in expected_fields:
                if field in opinion and not isinstance(opinion[field], str):
                    raise ValueError(f"El campo {field} en la opinión {i} debe ser un string")