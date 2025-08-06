"""
Error handling utilities for the Boletin Oficial application.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class ErrorCode(Enum):
    """Standard error codes for the application."""
    # PDF related errors
    PDF_NOT_FOUND = "PDF_001"
    PDF_PROCESSING_ERROR = "PDF_002"
    PDF_DOWNLOAD_ERROR = "PDF_003"
    PDF_EXTRACTION_ERROR = "PDF_004"
    
    # LLM related errors
    LLM_API_ERROR = "LLM_001"
    LLM_TIMEOUT_ERROR = "LLM_002"
    LLM_QUOTA_ERROR = "LLM_003"
    LLM_PARSING_ERROR = "LLM_004"
    
    # Database related errors
    DATABASE_CONNECTION_ERROR = "DB_001"
    DATABASE_QUERY_ERROR = "DB_002"
    DATABASE_VALIDATION_ERROR = "DB_003"
    
    # Configuration errors
    CONFIG_MISSING_ERROR = "CFG_001"
    CONFIG_INVALID_ERROR = "CFG_002"
    
    # General errors
    VALIDATION_ERROR = "VAL_001"
    TIMEOUT_ERROR = "TMO_001"
    UNKNOWN_ERROR = "UNK_001"


class ErrorHandler:
    """Centralized error handling for the application."""
    
    # Error definitions with codes, messages, and HTTP status codes
    ERROR_DEFINITIONS = {
        ErrorCode.PDF_NOT_FOUND: {
            'message': 'No se encontró PDF para la fecha especificada',
            'http_status': 404,
            'retryable': False
        },
        ErrorCode.PDF_PROCESSING_ERROR: {
            'message': 'Error procesando el contenido del PDF',
            'http_status': 500,
            'retryable': True
        },
        ErrorCode.PDF_DOWNLOAD_ERROR: {
            'message': 'Error descargando el PDF del boletín oficial',
            'http_status': 503,
            'retryable': True
        },
        ErrorCode.PDF_EXTRACTION_ERROR: {
            'message': 'Error extrayendo texto del PDF',
            'http_status': 500,
            'retryable': False
        },
        ErrorCode.LLM_API_ERROR: {
            'message': 'Error en el servicio de análisis de IA',
            'http_status': 503,
            'retryable': True
        },
        ErrorCode.LLM_TIMEOUT_ERROR: {
            'message': 'Timeout en el servicio de análisis de IA',
            'http_status': 504,
            'retryable': True
        },
        ErrorCode.LLM_QUOTA_ERROR: {
            'message': 'Cuota excedida en el servicio de IA',
            'http_status': 429,
            'retryable': False
        },
        ErrorCode.LLM_PARSING_ERROR: {
            'message': 'Error procesando respuesta del servicio de IA',
            'http_status': 500,
            'retryable': False
        },
        ErrorCode.DATABASE_CONNECTION_ERROR: {
            'message': 'Error de conexión con la base de datos',
            'http_status': 500,
            'retryable': True
        },
        ErrorCode.DATABASE_QUERY_ERROR: {
            'message': 'Error ejecutando consulta en la base de datos',
            'http_status': 500,
            'retryable': True
        },
        ErrorCode.DATABASE_VALIDATION_ERROR: {
            'message': 'Error de validación de datos',
            'http_status': 400,
            'retryable': False
        },
        ErrorCode.CONFIG_MISSING_ERROR: {
            'message': 'Configuración requerida no encontrada',
            'http_status': 500,
            'retryable': False
        },
        ErrorCode.CONFIG_INVALID_ERROR: {
            'message': 'Configuración inválida',
            'http_status': 500,
            'retryable': False
        },
        ErrorCode.VALIDATION_ERROR: {
            'message': 'Error de validación de entrada',
            'http_status': 400,
            'retryable': False
        },
        ErrorCode.TIMEOUT_ERROR: {
            'message': 'Timeout en la operación',
            'http_status': 504,
            'retryable': True
        },
        ErrorCode.UNKNOWN_ERROR: {
            'message': 'Error desconocido',
            'http_status': 500,
            'retryable': False
        }
    }
    
    def __init__(self):
        """Initialize the error handler with structured logging."""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Configure structured logging format
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def handle_pdf_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle PDF-related errors."""
        error_code = self._classify_pdf_error(error)
        return self._create_error_response(error_code, error, context)
    
    def handle_llm_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle LLM/LangChain related errors."""
        error_code = self._classify_llm_error(error)
        return self._create_error_response(error_code, error, context)
    
    def handle_database_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle database related errors."""
        error_code = self._classify_database_error(error)
        return self._create_error_response(error_code, error, context)
    
    def handle_config_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle configuration related errors."""
        error_code = self._classify_config_error(error)
        return self._create_error_response(error_code, error, context)
    
    def handle_validation_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle validation errors."""
        return self._create_error_response(ErrorCode.VALIDATION_ERROR, error, context)
    
    def handle_timeout_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle timeout errors."""
        return self._create_error_response(ErrorCode.TIMEOUT_ERROR, error, context)
    
    def handle_unknown_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle unknown/unclassified errors."""
        return self._create_error_response(ErrorCode.UNKNOWN_ERROR, error, context)
    
    def _classify_pdf_error(self, error: Exception) -> ErrorCode:
        """Classify PDF-related errors based on exception type and message."""
        error_str = str(error).lower()
        
        if "not found" in error_str or "404" in error_str:
            return ErrorCode.PDF_NOT_FOUND
        elif "download" in error_str or "connection" in error_str:
            return ErrorCode.PDF_DOWNLOAD_ERROR
        elif "extract" in error_str or "parse" in error_str:
            return ErrorCode.PDF_EXTRACTION_ERROR
        else:
            return ErrorCode.PDF_PROCESSING_ERROR
    
    def _classify_llm_error(self, error: Exception) -> ErrorCode:
        """Classify LLM-related errors based on exception type and message."""
        error_str = str(error).lower()
        
        if "timeout" in error_str:
            return ErrorCode.LLM_TIMEOUT_ERROR
        elif "quota" in error_str or "rate limit" in error_str or "429" in error_str:
            return ErrorCode.LLM_QUOTA_ERROR
        elif "parse" in error_str or "json" in error_str:
            return ErrorCode.LLM_PARSING_ERROR
        else:
            return ErrorCode.LLM_API_ERROR
    
    def _classify_database_error(self, error: Exception) -> ErrorCode:
        """Classify database-related errors based on exception type and message."""
        error_str = str(error).lower()
        
        if "connection" in error_str or "connect" in error_str:
            return ErrorCode.DATABASE_CONNECTION_ERROR
        elif "validation" in error_str or "schema" in error_str:
            return ErrorCode.DATABASE_VALIDATION_ERROR
        else:
            return ErrorCode.DATABASE_QUERY_ERROR
    
    def _classify_config_error(self, error: Exception) -> ErrorCode:
        """Classify configuration-related errors based on exception type and message."""
        error_str = str(error).lower()
        
        if "not found" in error_str or "missing" in error_str:
            return ErrorCode.CONFIG_MISSING_ERROR
        else:
            return ErrorCode.CONFIG_INVALID_ERROR
    
    def _create_error_response(self, error_code: ErrorCode, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a standardized error response."""
        error_def = self.ERROR_DEFINITIONS[error_code]
        
        error_response = {
            'success': False,
            'error': {
                'code': error_code.value,
                'message': error_def['message'],
                'details': str(error),
                'retryable': error_def['retryable'],
                'timestamp': datetime.utcnow().isoformat()
            },
            'http_status': error_def['http_status']
        }
        
        if context:
            error_response['error']['context'] = context
        
        # Log the error with structured logging
        self.log_error(error_code, error, context)
        
        return error_response
    
    def log_error(self, error_code: ErrorCode, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log error with structured format."""
        log_data = {
            'event': 'error_occurred',
            'error_code': error_code.value,
            'error_message': str(error),
            'error_type': type(error).__name__,
            'timestamp': datetime.utcnow().isoformat(),
            'retryable': self.ERROR_DEFINITIONS[error_code]['retryable']
        }
        
        if context:
            log_data['context'] = context
        
        self.logger.error(json.dumps(log_data))
    
    def log_info(self, event: str, data: Optional[Dict[str, Any]] = None):
        """Log informational events with structured format."""
        log_data = {
            'event': event,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if data:
            log_data.update(data)
        
        self.logger.info(json.dumps(log_data))
    
    def log_warning(self, event: str, data: Optional[Dict[str, Any]] = None):
        """Log warning events with structured format."""
        log_data = {
            'event': event,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if data:
            log_data.update(data)
        
        self.logger.warning(json.dumps(log_data))
    
    def is_retryable_error(self, error_code: ErrorCode) -> bool:
        """Check if an error is retryable."""
        return self.ERROR_DEFINITIONS[error_code]['retryable']
    
    def get_http_status(self, error_code: ErrorCode) -> int:
        """Get HTTP status code for an error."""
        return self.ERROR_DEFINITIONS[error_code]['http_status']


# Global error handler instance
error_handler = ErrorHandler()