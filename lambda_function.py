"""
Main Lambda handler for Boletin Oficial Telegram App
Handles HTTP requests from API Gateway and coordinates all services
"""

import json
import logging
import os
 
from datetime import datetime
from typing import Dict, Any, Optional

# Import services
from services.database_service import MongoDBService
from services.llm_service_direct import LLMAnalysisServiceDirect as LLMAnalysisService
from services.config_service import config_service
from utils.error_handler import error_handler, ErrorCode

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Global service instances (reused across Lambda invocations)
database_service = None
llm_service = None


def lambda_handler(event, context):
    """
    Punto de entrada principal de la Lambda function
    
    Args:
        event: Evento HTTP de API Gateway o Lambda Function URL
        context: Contexto de ejecución de Lambda
        
    Returns:
        dict: Respuesta HTTP estructurada
    """
    start_time = datetime.utcnow()
    
    try:
        # Log request start
        error_handler.log_info('lambda_request_start', {
            'request_id': context.aws_request_id,
            'function_name': context.function_name,
            'remaining_time_ms': context.get_remaining_time_in_millis()
        })
        
        # Parse HTTP event from API Gateway or Lambda Function URL
        parsed_request = parse_api_gateway_event(event)
        
        # Handle OPTIONS request for CORS preflight
        if parsed_request['method'] == 'OPTIONS':
            return format_options_response()
        
        # Validate input parameters
        validated_params = validate_request_parameters(parsed_request)
        
        # Initialize services if needed
        initialize_services()
        
        # Process analysis request
        result = process_analysis_request(validated_params, context)
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Format successful HTTP response
        response = format_success_response(result, processing_time)
        
        # Log successful completion
        error_handler.log_info('lambda_request_completed', {
            'request_id': context.aws_request_id,
            'processing_time_seconds': processing_time,
            'fecha': validated_params.get('fecha'),
            'from_cache': result.get('metadatos', {}).get('desde_cache', False)
        })
        
        return response
        
    except Exception as e:
        # Calculate processing time for error case
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Handle and format error response
        error_response = handle_lambda_error(e, event, context, processing_time)
        
        return error_response


def parse_api_gateway_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse HTTP event from API Gateway or Lambda Function URL
    
    Args:
        event: API Gateway or Lambda Function URL event
        
    Returns:
        dict: Parsed request data
        
    Raises:
        ValueError: If event format is invalid
    """
    try:
        # Detect event type and extract HTTP method
        if 'httpMethod' in event:
            # API Gateway event format
            http_method = event.get('httpMethod', '').upper()
            event_type = 'api_gateway'
        elif 'requestContext' in event and 'http' in event.get('requestContext', {}):
            # Lambda Function URL event format
            http_method = event.get('requestContext', {}).get('http', {}).get('method', '').upper()
            event_type = 'function_url'
        else:
            # Try to infer from available fields
            http_method = 'POST'  # Default assumption
            event_type = 'unknown'
        
        # Extract request body
        body = event.get('body', '{}')
        if isinstance(body, str):
            try:
                body_data = json.loads(body) if body else {}
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON in request body")
        else:
            body_data = body or {}
        
        # Extract query parameters (different format for Function URL)
        if event_type == 'function_url':
            query_params = event.get('queryStringParameters') or {}
        else:
            query_params = event.get('queryStringParameters') or {}
        
        # Extract path parameters
        path_params = event.get('pathParameters') or {}
        
        # Extract headers
        headers = event.get('headers') or {}
        
        # Extract source IP (different paths for different event types)
        if event_type == 'function_url':
            source_ip = event.get('requestContext', {}).get('http', {}).get('sourceIp')
        else:
            source_ip = event.get('requestContext', {}).get('identity', {}).get('sourceIp')
        
        parsed_request = {
            'method': http_method,
            'body': body_data,
            'query_params': query_params,
            'path_params': path_params,
            'headers': headers,
            'source_ip': source_ip,
            'user_agent': headers.get('User-Agent', ''),
            'event_type': event_type
        }
        
        error_handler.log_info('http_event_parsed', {
            'event_type': event_type,
            'method': http_method,
            'has_body': bool(body_data),
            'query_params_count': len(query_params),
            'source_ip': source_ip
        })
        
        return parsed_request
        
    except Exception as e:
        error_handler.log_error(ErrorCode.VALIDATION_ERROR, e, {
            'action': 'parse_http_event',
            'event_keys': list(event.keys()) if isinstance(event, dict) else 'invalid_event'
        })
        raise ValueError(f"Error parsing HTTP event: {str(e)}")


def validate_request_parameters(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalize request parameters
    
    Args:
        request: Parsed request data
        
    Returns:
        dict: Validated parameters
        
    Raises:
        ValueError: If parameters are invalid
    """
    try:
        # Handle OPTIONS method for CORS preflight
        if request['method'] == 'OPTIONS':
            return {
                'method': 'OPTIONS',
                'body': {},
                'query_params': {},
                'path_params': {},
                'headers': {},
                'source_ip': request.get('source_ip'),
                'user_agent': '',
                'event_type': request.get('event_type', 'unknown')
            }
        
        # Only support POST method for analysis requests
        if request['method'] != 'POST':
            raise ValueError(f"Method {request['method']} not allowed. Only POST is supported.")
        
        # Extract parameters from body
        body = request['body']
        
        # Get fecha parameter
        fecha = body.get('fecha')
        if not fecha:
            # Use current date if not provided
            fecha = datetime.now().strftime('%Y-%m-%d')
        
        # Validate fecha format
        try:
            datetime.strptime(fecha, '%Y-%m-%d')
        except ValueError:
            raise ValueError(f"Invalid date format: {fecha}. Use YYYY-MM-DD format.")
        
        # Validate fecha is not in the future
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
        if fecha_obj.date() > datetime.now().date():
            raise ValueError(f"Date {fecha} is in the future. No data available.")
        
        # Get forzar_reanalisis parameter (optional)
        forzar_reanalisis = body.get('forzar_reanalisis', False)
        if not isinstance(forzar_reanalisis, bool):
            # Try to convert string to boolean
            if isinstance(forzar_reanalisis, str):
                forzar_reanalisis = forzar_reanalisis.lower() in ['true', '1', 'yes', 'on']
            else:
                forzar_reanalisis = bool(forzar_reanalisis)
        
        validated_params = {
            'fecha': fecha,
            'forzar_reanalisis': forzar_reanalisis,
            'seccion': 'legislacion_avisos_oficiales'  # Fixed section for now
        }
        
        error_handler.log_info('request_parameters_validated', validated_params)
        
        return validated_params
        
    except Exception as e:
        error_handler.log_error(ErrorCode.VALIDATION_ERROR, e, {
            'action': 'validate_request_parameters',
            'request_method': request.get('method'),
            'body_keys': list(request.get('body', {}).keys())
        })
        raise


def initialize_services():
    """
    Initialize global service instances (reused across Lambda invocations)
    """
    global database_service, llm_service
    
    try:
        # Load configuration first
        error_handler.log_info('loading_configuration')
        config_service.load_config()
        
        # Initialize database service
        if database_service is None:
            error_handler.log_info('initializing_database_service')
            database_service = MongoDBService()
        
        # Initialize LLM service
        if llm_service is None:
            error_handler.log_info('initializing_llm_service')
            llm_service = LLMAnalysisService()
        
        error_handler.log_info('services_initialized_successfully')
        
    except Exception as e:
        error_handler.log_error(ErrorCode.CONFIG_MISSING_ERROR, e, {
            'action': 'initialize_services'
        })
        raise


def process_analysis_request(params: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Main processing logic for analysis requests
    
    Args:
        params: Validated request parameters
        context: Lambda context
        
    Returns:
        dict: Analysis result
    """
    fecha = params['fecha']
    forzar_reanalisis = params['forzar_reanalisis']
    
    try:
        # Check if analysis already exists (cache logic)
        if not forzar_reanalisis:
            existing_analysis = check_existing_analysis(fecha)
            if existing_analysis:
                error_handler.log_info('analysis_retrieved_from_cache', {
                    'fecha': fecha
                })
                # Add cache metadata
                existing_analysis['metadatos']['desde_cache'] = True
                return existing_analysis
        
        # Perform new analysis
        error_handler.log_info('starting_new_analysis', {
            'fecha': fecha,
            'forced': forzar_reanalisis
        })
        
        # Step 1: Analyze normativa with LLM using direct URL access (simplified)
        analysis_result = analyze_normativa_with_llm(fecha, context)
        
        # Check if analysis failed - if so, don't continue with expert opinions or save to DB
        if analysis_result.get('error', False):
            error_handler.log_error(ErrorCode.LLM_API_ERROR, Exception(analysis_result.get('error_message', 'Unknown error')), {
                'fecha': fecha,
                'action': 'analyze_normativa_failed'
            })
            # Return error response without saving to database
            return analysis_result
        
        # Step 4: Get expert opinions (only if analysis was successful)
        expert_opinions = get_expert_opinions(analysis_result, context, fecha)
        
        # Step 3: Prepare complete analysis data
        complete_analysis = prepare_analysis_data(
            fecha, analysis_result, expert_opinions
        )
        
        # Step 6: Save analysis to database (only if analysis was successful)
        save_analysis_to_database(complete_analysis, context)
        
        # Add metadata
        complete_analysis['metadatos']['desde_cache'] = False
        
        error_handler.log_info('new_analysis_completed', {
            'fecha': fecha,
            'method': 'direct_gemini_analysis',
            'changes_count': len(analysis_result.get('cambios_principales', [])),
            'opinions_count': len(expert_opinions)
        })
        
        return complete_analysis
        
    except Exception as e:
        error_handler.log_error(ErrorCode.UNKNOWN_ERROR, e, {
            'action': 'process_analysis_request',
            'fecha': fecha,
            'forced': forzar_reanalisis
        })
        raise


def check_existing_analysis(fecha: str) -> Optional[Dict[str, Any]]:
    """
    Check if analysis already exists for the given date
    
    Args:
        fecha: Date in YYYY-MM-DD format
        
    Returns:
        dict or None: Existing analysis or None if not found
    """
    try:
        error_handler.log_info('cache_check_starting', {
            'fecha': fecha,
            'fecha_type': type(fecha).__name__,
            'fecha_length': len(fecha)
        })
        
        result = database_service.get_analysis_by_date(fecha)
        
        error_handler.log_info('cache_check_completed', {
            'fecha': fecha,
            'found': result is not None,
            'result_keys': list(result.keys()) if result else None
        })
        
        return result
    except Exception as e:
        error_handler.log_error(ErrorCode.DATABASE_QUERY_ERROR, e, {
            'fecha': fecha,
            'error': str(e),
            'error_type': type(e).__name__
        })
        return None

def analyze_normativa_with_llm(fecha: str, context) -> Dict[str, Any]:
    """
    Analyze normativa using LLM with direct URL access
    
    Args:
        fecha: Date for analysis
        context: Lambda context
        
    Returns:
        dict: Analysis result
    """
    try:
        # Check remaining time
        remaining_time = context.get_remaining_time_in_millis()
        if remaining_time < 60000:  # Less than 60 seconds
            raise Exception("Insufficient time remaining for LLM analysis")
        
        # Use new method that accesses URL directly
        analysis_result = llm_service.analyze_normativa(fecha)
        
        error_handler.log_info('llm_analysis_completed', {
            'fecha': fecha,
            'method': 'direct_url_access',
            'changes_identified': len(analysis_result.get('cambios_principales', [])),
            'areas_affected': len(analysis_result.get('areas_afectadas', []))
        })
        
        return analysis_result
        
    except Exception as e:
        error_handler.log_error(ErrorCode.LLM_API_ERROR, e, {
            'fecha': fecha,
            'method': 'direct_url_access',
            'remaining_time_ms': context.get_remaining_time_in_millis()
        })
        raise


def get_expert_opinions(analysis_result: Dict[str, Any], context, fecha_boletin: str) -> list:
    """
    Get expert opinions based on analysis
    
    Args:
        analysis_result: Result from LLM analysis
        context: Lambda context
        fecha_boletin: Fecha del boletín oficial
        
    Returns:
        list: Expert opinions
    """
    try:
        # Check remaining time
        remaining_time = context.get_remaining_time_in_millis()
        if remaining_time < 50000:  # Less than 50 seconds
            error_handler.log_warning('insufficient_time_for_expert_opinions', {
                'remaining_time_ms': remaining_time,
                'fecha_boletin': fecha_boletin
            })
            return []
        
        resumen = analysis_result.get('resumen', '')
        cambios_principales = analysis_result.get('cambios_principales', [])
        
        expert_opinions = llm_service.get_expert_opinions(resumen, cambios_principales, fecha_boletin)
        
        error_handler.log_info('expert_opinions_generated', {
            'opinions_count': len(expert_opinions),
            'fecha_boletin': fecha_boletin
        })
        
        return expert_opinions
        
    except Exception as e:
        error_handler.log_warning('expert_opinions_failed', {
            'error': str(e),
            'remaining_time_ms': context.get_remaining_time_in_millis(),
            'fecha_boletin': fecha_boletin
        })
        # Return empty list if expert opinions fail (non-critical)
        return []


def prepare_analysis_data(fecha: str, analysis_result: Dict[str, Any], expert_opinions: list) -> Dict[str, Any]:
    """
    Prepare complete analysis data structure
    
    Args:
        fecha: Analysis date
        analysis_result: LLM analysis result
        expert_opinions: Expert opinions
        
    Returns:
        dict: Complete analysis data
    """
    return {
        'fecha': fecha,
        'seccion': 'legislacion_avisos_oficiales',
        'pdf_url': 'https://www.boletinoficial.gob.ar/',  # Base URL used for analysis
        'contenido_original': 'Análisis realizado con acceso directo a URL del Boletín Oficial',
        'analisis': analysis_result,
        'opiniones_expertos': expert_opinions,
        'metadatos': {
            'fecha_creacion': datetime.utcnow(),
            'version_analisis': '2.0',  # Updated version for URL-based analysis
            'modelo_llm_usado': os.getenv('LANGCHAIN_MODEL', 'gemini-2.5-flash'),
            'tiempo_procesamiento': 0,  # Will be calculated later
            'estado': 'completado',
            'metodo_analisis': 'url_directa',
            'url_fuente': 'https://www.boletinoficial.gob.ar/'
        }
    }


def save_analysis_to_database(analysis_data: Dict[str, Any], context) -> str:
    """
    Save analysis to database
    
    Args:
        analysis_data: Complete analysis data
        context: Lambda context
        
    Returns:
        str: Document ID
    """
    try:
        document_id = database_service.save_analysis(analysis_data)
        
        error_handler.log_info('analysis_saved_to_database', {
            'document_id': document_id,
            'fecha': analysis_data['fecha']
        })
        
        return document_id
        
    except Exception as e:
        error_handler.log_error(ErrorCode.DATABASE_QUERY_ERROR, e, {
            'action': 'save_analysis',
            'fecha': analysis_data.get('fecha')
        })
        # Don't fail the entire request if database save fails
        error_handler.log_warning('analysis_not_saved_continuing', {
            'fecha': analysis_data.get('fecha')
        })
        return ''


def format_options_response() -> Dict[str, Any]:
    """
    Format CORS preflight OPTIONS response
    
    Returns:
        dict: HTTP OPTIONS response
    """
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With, Accept',
            'Access-Control-Max-Age': '86400',
            'Content-Type': 'application/json'
        },
        'body': ''
    }


def format_success_response(result: Dict[str, Any], processing_time: float) -> Dict[str, Any]:
    """
    Format successful HTTP response
    
    Args:
        result: Analysis result
        processing_time: Processing time in seconds
        
    Returns:
        dict: HTTP response
    """
    # Update processing time in metadata
    if 'metadatos' in result:
        result['metadatos']['tiempo_procesamiento'] = round(processing_time, 2)
    
    response = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With, Accept'
        },
        'body': json.dumps({
            'success': True,
            'data': result,
            'message': 'Análisis completado exitosamente'
        }, ensure_ascii=False, default=str)
    }
    
    return response


def handle_lambda_error(error: Exception, event: Dict[str, Any], 
                       context, processing_time: float) -> Dict[str, Any]:
    """
    Handle and format error responses
    
    Args:
        error: Exception that occurred
        event: Original event
        context: Lambda context
        processing_time: Processing time in seconds
        
    Returns:
        dict: HTTP error response
    """
    # Determine error type and get appropriate error response
    if "validation" in str(error).lower() or "invalid" in str(error).lower():
        error_response = error_handler.handle_validation_error(error, {
            'processing_time': processing_time,
            'request_id': context.aws_request_id
        })
    elif "pdf" in str(error).lower():
        error_response = error_handler.handle_pdf_error(error, {
            'processing_time': processing_time,
            'request_id': context.aws_request_id
        })
    elif "llm" in str(error).lower() or "gemini" in str(error).lower():
        error_response = error_handler.handle_llm_error(error, {
            'processing_time': processing_time,
            'request_id': context.aws_request_id
        })
    elif "database" in str(error).lower() or "mongo" in str(error).lower():
        error_response = error_handler.handle_database_error(error, {
            'processing_time': processing_time,
            'request_id': context.aws_request_id
        })
    elif "timeout" in str(error).lower():
        error_response = error_handler.handle_timeout_error(error, {
            'processing_time': processing_time,
            'request_id': context.aws_request_id
        })
    else:
        error_response = error_handler.handle_unknown_error(error, {
            'processing_time': processing_time,
            'request_id': context.aws_request_id
        })
    
    # Format HTTP error response
    http_response = {
        'statusCode': error_response.get('http_status', 500),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With, Accept'
        },
        'body': json.dumps({
            'success': False,
            'error': error_response['error'],
            'message': error_response['error']['message']
        }, ensure_ascii=False, default=str)
    }
    
    return http_response