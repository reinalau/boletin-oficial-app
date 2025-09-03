"""
LLM service usando Gemini directamente sin LangChain
Versión simplificada y sin conflictos de dependencias
Basado en geminiPrompt.py con fecha actual
"""

import os
import json
import logging
import requests
import time
import base64
from datetime import datetime
from typing import Dict, Any, Optional
from google import genai
from google.genai import types
from utils.error_handler import error_handler, ErrorCode

logger = logging.getLogger(__name__)

class LLMAnalysisServiceDirect:
    """Servicio de análisis LLM usando Gemini directamente"""
    
    def __init__(self):
        """Inicializa el servicio de Gemini directamente"""
        try:
            # Configurar API key - usar GEMINI_API_KEY como en geminiPrompt.py
            api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY o GOOGLE_API_KEY no está configurada en las variables de entorno")
            
            # Inicializar cliente Gemini
            self.client = genai.Client(api_key=api_key)

             
            # Configurar modelo desde variables de entorno
            self.model_name = os.getenv('LANGCHAIN_MODEL', 'gemini-2.5-flash')
            
            logger.info(f"LLMAnalysisServiceDirect inicializado con modelo: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Error inicializando LLMAnalysisServiceDirect: {str(e)}")
            raise
    
    def crear_sesion_pdf_fecha(self, fecha_boletin: str = None):
        """Crea una nueva sesión con cookies frescas para poder consultar el boletin de fecha_boletin"""
        session = requests.Session()
    
        # Visitar página principal para establecer sesión
        session.get('https://www.boletinoficial.gob.ar/seccion/primera')
        time.sleep(1)
        fecha_obj = datetime.strptime(fecha_boletin, '%Y-%m-%d')
        fecha_formateada= fecha_obj.strftime('%d-%m-%Y')

        url1= f'https://www.boletinoficial.gob.ar/edicion/actualizar/{fecha_formateada}'
        #sesion que setea la fecha para traer el pdf de una fecha determinada
        response = session.get(url1)
        
        if response.status_code == 200:
                url2 = "https://www.boletinoficial.gob.ar/pdf/download_section"
                headers = {
                        'Accept': 'application/json, text/javascript, */*; q=0.01',
                        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'Origin': 'https://www.boletinoficial.gob.ar',
                        'Referer': 'https://www.boletinoficial.gob.ar/seccion/primera',
                        'X-Requested-With': 'XMLHttpRequest',
                        'Sec-Fetch-Dest': 'empty',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Site': 'same-origin',
                }
                data = {
                    'nombreSeccion': 'primera',
                }

                # Hacer petición POST con la sesión establecida
                response = session.post(url2, data=data, headers=headers, timeout=30)

                if response.status_code == 200:
                    # La respuesta es JSON con el PDF en Base64
                    json_data = response.json()
                    pdf_base64 = json_data['pdfBase64']
                    return pdf_base64
                else:
                    return self._create_error_response("No puedo obtener pdf anterior") 
    
        else:
            return self._create_error_response("No puedo obtener sesion pdf anterior") 

    
    def analyze_normativa(self, date: str = None) -> Dict[str, Any]:
        """
        Analiza el contenido normativo usando Gemini directamente
        Siempre usa la fecha parametro o la mas actual que encuentre
        
        Args:
            date: Fecha del boletín 
            
        Returns:
            dict: Análisis estructurado de la normativa
        """
        current_date = datetime.now().strftime('%d/%m/%Y')
        # Usa la fecha que ingresa como parametro
        param_date = date
        
        max_retries = int(os.getenv('MAX_RETRY_ATTEMPTS', '3'))
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Iniciando análisis de normativa para la fecha {param_date}, intento {attempt + 1}")
                
               
                # Crear contenido usando el formato de geminiPrompt.py
                contents = self._create_analysis_contents(param_date)
                
                # Configurar tools y thinking
                tool_config = {"force_refresh": True}
                tools = [
                    types.Tool(url_context=types.UrlContext()),
                    types.Tool(googleSearch=types.GoogleSearch()),
                ]
                
                generate_content_config = types.GenerateContentConfig(
                    temperature=int(os.getenv('LANGCHAIN_TEMPERATURE', '0')),
                    thinking_config = types.ThinkingConfig(
                        thinking_budget=-1,
                    ),
                    media_resolution="MEDIA_RESOLUTION_UNSPECIFIED",
                    tools=tools,
                )
                
                # Realizar llamada a Gemini
                logger.info("Enviando solicitud a Gemini API con thinking y Google Search")
                
                # Recopilar respuesta completa
                response_text = ""
                for chunk in self.client.models.generate_content_stream(
                    model=self.model_name,
                    contents=contents,
                    config=generate_content_config,
                ):
                    if chunk.text:
                        response_text += chunk.text
                
                #Borrar Cache de contexto pendiente
                
                
                if not response_text:
                    raise Exception("Respuesta vacía de Gemini")
                
                logger.info(f"Respuesta recibida de Gemini: {len(response_text)} caracteres")
                
                # Parsear respuesta JSON
                analysis_result = self._parse_response(response_text)
                
                # Validar estructura de respuesta
                validated_result = self._validate_analysis_response(analysis_result)
                
                logger.info("Análisis de normativa completado exitosamente con Gemini directo")
                return validated_result
                
            except json.JSONDecodeError as e:
                error_handler.log_error(ErrorCode.LLM_PARSING_ERROR, e, {
                    'attempt': attempt + 1,
                    'fecha_actual': current_date
                })
                if attempt == max_retries - 1:
                    return self._create_error_response(f"Error parseando respuesta después de {max_retries} intentos")
                continue
                
            except Exception as e:
                error_handler.log_error(ErrorCode.LLM_API_ERROR, e, {
                    'attempt': attempt + 1,
                    'fecha_actual': current_date
                })
                if attempt == max_retries - 1:
                    return self._create_error_response(f"Error en análisis después de {max_retries} intentos: {str(e)}")
                continue
        
        # Si llegamos aquí, todos los intentos fallaron
        return self._create_error_response("Todos los intentos de análisis fallaron")
    
    def get_expert_opinions(self, normativa_summary: str, cambios_principales: list = None, fecha_boletin: str = None) -> list:
        """
        Obtiene opiniones de expertos sobre el análisis del Boletín Oficial
        buscando en portales argentinos
        
        Args:
            normativa_summary: Resumen de la normativa
            cambios_principales: Lista de cambios principales
            fecha_boletin: Fecha del boletín oficial a buscar
            
        Returns:
            list: Lista de opiniones de expertos con referencias
        """
        if not fecha_boletin:
            logger.warning("get_expert_opinions: No se proporcionó fecha del boletín")
            return []
        
        max_retries = int(os.getenv('MAX_RETRY_ATTEMPTS', '2'))
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Buscando opiniones de expertos para fecha {fecha_boletin}, intento {attempt + 1}")
                
                # Crear contenido para búsqueda de opiniones
                contents = self._create_expert_opinions_contents(fecha_boletin, normativa_summary, cambios_principales)
                
                # Configurar tools para búsqueda web
                tools = [
                    types.Tool(googleSearch=types.GoogleSearch())
                ]
                
                generate_content_config = types.GenerateContentConfig(
                    tools=tools,
                    temperature=1,
                )
                
                # Realizar llamada a Gemini
                logger.info("Enviando solicitud a Gemini para búsqueda de opiniones de expertos")
                
                response_text = ""
                for chunk in self.client.models.generate_content_stream(
                    model=self.model_name,
                    contents=contents,
                    config=generate_content_config,
                ):
                    if chunk.text:
                        response_text += chunk.text
                
                if not response_text:
                    logger.warning("Respuesta vacía de Gemini para opiniones de expertos")
                    return []
                
                logger.info(f"Respuesta de opiniones recibida: {len(response_text)} caracteres")
                
                # Parsear respuesta JSON
                opinions_result = self._parse_expert_opinions_response(response_text)
                
                logger.info(f"Opiniones de expertos obtenidas: {len(opinions_result)} opiniones")
                return opinions_result
                
            except Exception as e:
                error_handler.log_error(ErrorCode.LLM_API_ERROR, e, {
                    'attempt': attempt + 1,
                    'fecha_boletin': fecha_boletin,
                    'action': 'get_expert_opinions'
                })
                if attempt == max_retries - 1:
                    logger.warning(f"Error obteniendo opiniones después de {max_retries} intentos: {str(e)}")
                    return []
                continue
        
        return []
    
    def _create_analysis_contents(self,param_date) -> list:
        """Crea el contenido para análisis en Gemini"""

        #obtiene el pdf de la fecha
        pdf_base64 = self.crear_sesion_pdf_fecha(param_date)

        prompt_text = f"""
        Analiza los puntos mas importantes de el contenido adjunto de la Primera Sección del Boletín Oficial de la República Argentina - Sección 1 - Legislación y Avisos Oficiales para la Edición adjunto de fecha {param_date}
        
        INSTRUCCIONES PARA EL ANÁLISIS REQUERIDO:
        - Tomar la fuente adjunta  para analizar y hacer el resumen ejecutivo de los cambios normativos relevantes como privatizaciones, área previsional, desregulaciones importantes (para la fecha indicada).
        - Lista detallada de cambios principales: decretos, resoluciones, disposiciones, avisos oficiales, convenciones colectivas de trabajo y si se identifican cambio en leyes.
        - Impacto estimado de los cambios.
        - Áreas del derecho afectadas.

        FORMATO DE RESPUESTA (JSON válido):
        {{
        "resumen": "Resumen ejecutivo de los cambios normativos encontrados para {param_date}",
        "cambios_principales": [
        {{
        "tipo": "decreto|resolución|ley|disposición",
        "numero": "número del instrumento legal",
        "rotulo": "Titulo exacto completo asociado al instrumento legal (Ejemplo: AGENCIA DE RECAUDACIÓN Y CONTROL ADUANERO. DIRECCIÓN REGIONAL SANTA FE. Disposición 44/2025)",
        "titulo": "título o tema principal",
        "descripcion": "descripción detallada del cambio",
        "impacto": "alto|medio|bajo",
        "justificacion_impacto": "explicación del nivel de impacto"
        }}
        ],
        "impacto_estimado": "Análisis general del impacto de todos los cambios",
        "areas_afectadas": ["tributario", "laboral", "comercial", "civil", "penal", "administrativo", "otros"]
        }}

        IMPORTANTE:
        Responde ÚNICAMENTE con el JSON válido, sin texto adicional.
        Asegúrate de que todas las áreas afectadas estén en minúsculas.
        Responder en español..
        """

        contents = [
            types.Content(
                role="user",
                parts=[
                       types.Part.from_bytes(
                       mime_type="application/pdf",
                       data=base64.b64decode(
                       pdf_base64
                                            ),
                        ),
                        types.Part.from_text(text=prompt_text),
                    ],
                        ),
                ]
        
        logger.info( contents)
        return contents
    
    def _create_expert_opinions_contents(self, fecha_boletin: str, normativa_summary: str, cambios_principales: list) -> list:
        """Crea el contenido para búsqueda de opiniones de expertos"""
        
        # Crear resumen de cambios para el contexto
        cambios_texto = ""
        if cambios_principales:
            cambios_texto = "\n".join([
                f"- {cambio.get('tipo', 'N/A')} {cambio.get('numero', 'N/A')}: {cambio.get('titulo', 'N/A')} - {cambio.get('descripcion', 'N/A')}"
                for cambio in cambios_principales[:5]  # Limitar a 5 cambios principales
            ])
        
        
        
        prompt_text = f"""
    Buscar análisis del contenido del Boletín Oficial de la República Argentina para la fecha {fecha_boletin} en los principales portales de Argentina. 

    CONTEXTO DEL BOLETÍN:
    Resumen: {normativa_summary}

    Principales cambios identificados:
    {cambios_texto}

    INSTRUCCIONES DE BÚSQUEDA:
    1. Busca en portales argentinos como los del siguiente listado para la fecha {fecha_boletin} :
    - La Nación (lanacion.com.ar)
    - Clarín (clarin.com)
    - Página/12 (pagina12.com.ar)
    - Ámbito Financiero (ambito.com)
    - El Cronista (cronista.com)
    - Infobae (infobae.com)
    - BAE Negocios (baenegocios.com)
    - Portales jurídicos especializados.
    - Sitios de análisis económico y legal

    2. 
    -Excluir de las busquedas los sitios: https://www.boletinoficial.gob.ar/ y https://boa.com.ar/ (BOA)
    -Excluir publicaciones con fechas anteriores a 2 dias de {fecha_boletin} .   

    3. Busca específicamente análisis, opiniones o comentarios para la fecha {fecha_boletin} sobre:
    - Los cambios normativos del {fecha_boletin}
    - Impacto de las nuevas regulaciones
    - Opiniones de expertos legales o económicos
    - Análisis de consultoras o estudios jurídicos

    4. Haz una lista con resumen de las principales opiniones y referencia el medio donde lo encontraste.

    FORMATO DE RESPUESTA (JSON válido):
    [
    {{
        "medio": "Nombre del medio o portal",
        "url": "URL del artículo o analisis periodistico (si está disponible)",
        "autor": "Nombre del autor o experto (si está disponible)",
        "titulo": "Título del artículo o análisis",
        "opinion_resumen": "Resumen de la opinión o análisis encontrado",
        "fecha_publicacion": "Fecha de publicación (si está disponible)",
        "relevancia": "alta|media|baja"
    }}
    ]

    IMPORTANTE:
    - Responde ÚNICAMENTE con el JSON válido, sin texto adicional
    - Incluye máximo 10 opiniones
    - Prioriza fuentes confiables y reconocidas
    - Si no encuentras información, retorna un array vacío []
    """ 
        
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt_text),
                ],
            ),
        ]
        
        return contents
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parsea la respuesta de Gemini"""
        try:
            # Limpiar la respuesta
            cleaned_response = response_text.strip()
            
            # Buscar el JSON en la respuesta
            start_idx = cleaned_response.find('{')
            end_idx = cleaned_response.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise json.JSONDecodeError("No se encontró JSON válido en la respuesta", cleaned_response, 0)
            
            json_str = cleaned_response[start_idx:end_idx]
            
            # Parsear JSON
            parsed_response = json.loads(json_str)
            
            logger.info("Respuesta de Gemini parseada correctamente")
            return parsed_response
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando JSON: {str(e)}")
            logger.error(f"Respuesta problemática: {response_text[:500]}...")
            raise
    
    def _validate_analysis_response(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Valida y formatea la respuesta de análisis"""
        
        # Campos requeridos
        required_fields = ['resumen', 'cambios_principales', 'impacto_estimado', 'areas_afectadas']
        
        validated_result = {}
        
        # Validar campos requeridos
        for field in required_fields:
            if field not in analysis_result:
                logger.warning(f"Campo requerido '{field}' no encontrado, usando valor por defecto")
                
                if field == 'resumen':
                    validated_result[field] = 'No se pudo generar resumen'
                elif field == 'cambios_principales':
                    validated_result[field] = []
                elif field == 'impacto_estimado':
                    validated_result[field] = 'No se pudo estimar impacto'
                elif field == 'areas_afectadas':
                    validated_result[field] = ['otros']
            else:
                validated_result[field] = analysis_result[field]
        
        # Validar tipos de datos
        if not isinstance(validated_result['cambios_principales'], list):
            validated_result['cambios_principales'] = []
        
        if not isinstance(validated_result['areas_afectadas'], list):
            validated_result['areas_afectadas'] = ['otros']
        
        # Normalizar áreas afectadas a minúsculas
        validated_result['areas_afectadas'] = [area.lower() for area in validated_result['areas_afectadas']]
        
        # Validar cambios principales
        validated_cambios = []
        for cambio in validated_result['cambios_principales']:
            if isinstance(cambio, dict):
                validated_cambio = {
                    'tipo': cambio.get('tipo', 'otro'),
                    'numero': cambio.get('numero', 'No especificado'),
                    'rotulo': cambio.get('rotulo','No especificado'),
                    'titulo': cambio.get('titulo', 'No especificado'),
                    'descripcion': cambio.get('descripcion', 'No especificado'),
                    'impacto': cambio.get('impacto', 'medio'),
                    'justificacion_impacto': cambio.get('justificacion_impacto', 'No especificado')
                }
                validated_cambios.append(validated_cambio)
        
        validated_result['cambios_principales'] = validated_cambios
        
        # Mantener resumen completo (sin truncar)
        
        logger.info(f"Respuesta validada: {len(validated_cambios)} cambios principales identificados")
        return validated_result
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Crea una respuesta de error estructurada"""
        return {
            'resumen': f'Error en el análisis: {error_message}',
            'cambios_principales': [],
            'impacto_estimado': 'No se pudo determinar debido a error',
            'areas_afectadas': ['error'],
            'error': True,
            'error_message': error_message
        }
    
    def _parse_expert_opinions_response(self, response_text: str) -> list:
        """Parsea la respuesta de opiniones de expertos"""
        try:
            # Limpiar la respuesta
            cleaned_response = response_text.strip()
            
            # Buscar el JSON array en la respuesta
            start_idx = cleaned_response.find('[')
            end_idx = cleaned_response.rfind(']') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.warning("No se encontró JSON array válido en la respuesta de opiniones")
                return []
            
            json_str = cleaned_response[start_idx:end_idx]
            
            # Parsear JSON
            parsed_opinions = json.loads(json_str)
            
            # Validar que sea una lista
            if not isinstance(parsed_opinions, list):
                logger.warning("La respuesta de opiniones no es una lista válida")
                return []
            
            # Validar y limpiar cada opinión
            validated_opinions = []
            for opinion in parsed_opinions:
                if isinstance(opinion, dict):
                    validated_opinion = {
                        'medio': opinion.get('medio', 'No especificado'),
                        'url': opinion.get('url', ''),
                        'autor': opinion.get('autor', 'No especificado'),
                        'titulo': opinion.get('titulo', 'No especificado'),
                        'opinion_resumen': opinion.get('opinion_resumen', 'No disponible'),
                        'fecha_publicacion': opinion.get('fecha_publicacion', 'No especificada'),
                        'relevancia': opinion.get('relevancia', 'media')
                    }
                    
                    # Validar relevancia
                    if validated_opinion['relevancia'] not in ['alta', 'media', 'baja']:
                        validated_opinion['relevancia'] = 'media'
                    
                    # Mantener opinión completa (sin truncar)
                    
                    validated_opinions.append(validated_opinion)
            
            logger.info(f"Opiniones de expertos parseadas: {len(validated_opinions)} opiniones válidas")
            return validated_opinions[:10]  # Limitar a máximo 10 opiniones
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando JSON de opiniones: {str(e)}")
            logger.error(f"Respuesta problemática: {response_text[:300]}...")
            return []
        except Exception as e:
            logger.error(f"Error inesperado parseando opiniones: {str(e)}")
            return []