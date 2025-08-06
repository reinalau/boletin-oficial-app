# Documento de Diseño

## Visión General

La aplicación AppBoletinOficial consiste en un backend serverless implementado en AWS Lambda que procesa automáticamente el Boletín Oficial de Argentina, extrae normativa de la sección "Legislación y Avisos Oficiales", y utiliza inteligencia artificial para generar análisis detallados. El sistema está diseñado para ser escalable, eficiente y fácil de mantener.

## Arquitectura

### Arquitectura General del Sistema

```mermaid
graph TB
    A[Telegram Mini App] --> B[API Gateway]
    B --> C[AWS Lambda Handler]
    C --> D[PDF Scraper Service]
    C --> E[LangChain LLM Service]
    C --> F[MongoDB Service]
    D --> G[Boletín Oficial Website]
    E --> H[Google Gemini API]
    F --> I[MongoDB Atlas]
    
    subgraph "AWS Lambda Function"
        C
        D
        E
        F
        J[Error Handler]
        K[Response Formatter]
    end
```

### Arquitectura del Backend Lambda

La Lambda function está estructurada en capas siguiendo el patrón de arquitectura hexagonal:

- **Handler Layer**: Maneja las requests HTTP y responses
- **Service Layer**: Lógica de negocio principal
- **Repository Layer**: Acceso a datos (MongoDB)
- **External Services Layer**: Integración con APIs externas (LLM, web scraping)

## Componentes e Interfaces

### 1. Lambda Handler Principal

**Archivo**: `lambda_function.py`

```python
# Interfaz principal de la Lambda
def lambda_handler(event, context):
    """
    Punto de entrada principal de la Lambda function
    
    Args:
        event: Evento HTTP de API Gateway
        context: Contexto de ejecución de Lambda
        
    Returns:
        dict: Respuesta HTTP estructurada
    """
```

**Responsabilidades**:
- Parsear requests HTTP de API Gateway
- Validar parámetros de entrada
- Coordinar servicios
- Formatear respuestas HTTP
- Manejo de errores global

### 2. PDF Scraper Service

**Archivo**: `services/pdf_scraper.py`

```python
class BoletinScraperService:
    def get_boletin_pdf_url(self, date: str) -> str:
        """Obtiene la URL del PDF para una fecha específica"""
        
    def download_pdf(self, pdf_url: str) -> bytes:
        """Descarga el PDF del boletín oficial"""
        
    def extract_seccion_legislacion(self, pdf_content: bytes) -> str:
        """Extrae el texto de la sección Legislación y Avisos Oficiales"""
```

**Dependencias**:
- `requests`: Para HTTP requests
- `PyPDF2` o `pdfplumber`: Para extracción de texto de PDFs
- `beautifulsoup4`: Para parsing HTML del sitio web

### 3. LangChain LLM Service

**Archivo**: `services/llm_service.py`

```python
class LLMAnalysisService:
    def __init__(self):
        """Inicializa LangChain con el modelo LLM configurado"""
        
    def analyze_normativa(self, text_content: str, date: str) -> dict:
        """
        Analiza el contenido normativo usando LLM
        
        Returns:
            dict: {
                'resumen': str,
                'cambios_principales': list,
                'impacto_estimado': str,
                'areas_afectadas': list
            }
        """
        
    def get_expert_opinions(self, normativa_summary: str) -> list:
        """Genera opiniones de expertos simuladas o busca opiniones reales"""
```

**Configuración LangChain**:
- Modelo: Google Gemini (capa gratuita)
- Prompts estructurados para análisis legal
- Chain para procesamiento secuencial
- Memory para contexto de conversación

### 4. MongoDB Service

**Archivo**: `services/database_service.py`

```python
class MongoDBService:
    def __init__(self):
        """Inicializa conexión a MongoDB Atlas"""
        
    def save_analysis(self, analysis_data: dict) -> str:
        """Guarda análisis en la base de datos"""
        
    def get_analysis_by_date(self, date: str) -> dict:
        """Recupera análisis existente por fecha"""
        
    def analysis_exists(self, date: str) -> bool:
        """Verifica si ya existe análisis para una fecha"""
```

### 5. Error Handler

**Archivo**: `utils/error_handler.py`

```python
class ErrorHandler:
    @staticmethod
    def handle_pdf_error(error: Exception) -> dict:
        """Maneja errores de descarga/procesamiento de PDF"""
        
    @staticmethod
    def handle_llm_error(error: Exception) -> dict:
        """Maneja errores de LLM/LangChain"""
        
    @staticmethod
    def handle_database_error(error: Exception) -> dict:
        """Maneja errores de base de datos"""
```

## Modelos de Datos

### Esquema MongoDB

**Colección**: `boletin_analysis`

```json
{
  "_id": "ObjectId",
  "fecha": "2024-01-15",
  "seccion": "legislacion_avisos_oficiales",
  "pdf_url": "https://otslist.boletinoficial.gob.ar/ots/...",
  "contenido_original": "texto completo extraído del PDF",
  "analisis": {
    "resumen": "Resumen ejecutivo de los cambios normativos",
    "cambios_principales": [
      {
        "tipo": "decreto",
        "numero": "123/2024",
        "titulo": "Modificación de...",
        "descripcion": "Descripción del cambio",
        "impacto": "alto|medio|bajo"
      }
    ],
    "impacto_estimado": "Análisis del impacto general",
    "areas_afectadas": ["tributario", "laboral", "comercial"]
  },
  "opiniones_expertos": [
    {
      "fuente": "Nombre del experto o institución",
      "opinion": "Texto de la opinión",
      "fecha_opinion": "2024-01-15",
      "relevancia": "alta|media|baja"
    }
  ],
  "metadatos": {
    "fecha_creacion": "2024-01-15T10:30:00Z",
    "version_analisis": "1.0",
    "modelo_llm_usado": "gpt-4",
    "tiempo_procesamiento": 25.5,
    "estado": "completado|error|procesando"
  }
}
```

### Modelo de Request API

```json
{
  "fecha": "2024-01-15",
  "forzar_reanalisis": false
}
```

### Modelo de Response API

```json
{
  "success": true,
  "data": {
    "fecha": "2024-01-15",
    "analisis": {
      "resumen": "...",
      "cambios_principales": [...],
      "impacto_estimado": "...",
      "areas_afectadas": [...]
    },
    "opiniones_expertos": [...],
    "metadatos": {
      "fecha_creacion": "...",
      "tiempo_procesamiento": 25.5,
      "desde_cache": true
    }
  },
  "message": "Análisis completado exitosamente"
}
```

## Manejo de Errores

### Estrategia de Reintentos

1. **PDF Download Failures**: 3 reintentos con backoff exponencial
2. **LLM API Failures**: 2 reintentos con delay fijo
3. **Database Failures**: 3 reintentos con backoff exponencial

### Tipos de Error y Responses

```python
ERROR_CODES = {
    'PDF_NOT_FOUND': {
        'code': 'PDF_001',
        'message': 'No se encontró PDF para la fecha especificada',
        'http_status': 404
    },
    'PDF_PROCESSING_ERROR': {
        'code': 'PDF_002', 
        'message': 'Error procesando el contenido del PDF',
        'http_status': 500
    },
    'LLM_API_ERROR': {
        'code': 'LLM_001',
        'message': 'Error en el servicio de análisis de IA',
        'http_status': 503
    },
    'DATABASE_ERROR': {
        'code': 'DB_001',
        'message': 'Error de conexión con la base de datos',
        'http_status': 500
    }
}
```

## Estrategia de Testing

### Unit Tests

**Archivo**: `tests/test_services.py`

```python
class TestBoletinScraperService:
    def test_get_pdf_url_valid_date(self):
        """Test obtención de URL con fecha válida"""
        
    def test_extract_seccion_legislacion(self):
        """Test extracción de texto de PDF"""

class TestLLMAnalysisService:
    def test_analyze_normativa_with_mock_llm(self):
        """Test análisis con LLM mockeado"""
        
class TestMongoDBService:
    def test_save_and_retrieve_analysis(self):
        """Test guardado y recuperación de análisis"""
```

### Integration Tests

**Archivo**: `tests/test_integration.py`

```python
class TestLambdaIntegration:
    def test_full_analysis_flow(self):
        """Test del flujo completo de análisis"""
        
    def test_cached_analysis_retrieval(self):
        """Test recuperación de análisis cacheado"""
```

### Performance Tests

- Tiempo de respuesta < 30 segundos (requerimiento)
- Memory usage < 1GB (límite Lambda)
- Concurrent requests handling

## Configuración y Despliegue

### Variables de Entorno

```bash
# LLM Configuration
GOOGLE_API_KEY=your-gemini-api-key
LANGCHAIN_MODEL=gemini-2.5-pro
LANGCHAIN_TEMPERATURE=1

# MongoDB Configuration  
MONGODB_CONNECTION_STRING=mongodb+srv://[username]:[password]@cluster0.8koognb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
MONGODB_DATABASE=BoletinOficial
MONGODB_COLLECTION=boletin-oficial

# Application Configuration
MAX_RETRY_ATTEMPTS=3
PDF_DOWNLOAD_TIMEOUT=30
LLM_REQUEST_TIMEOUT=60
```

### Dependencias (requirements.txt)

```txt
langchain==0.1.0
langchain-google-genai==1.0.0
google-generativeai==0.3.0
pymongo==4.6.0
requests==2.31.0
pdfplumber==0.9.0
beautifulsoup4==4.12.0
python-dateutil==2.8.2
```

### Configuración AWS Lambda

```yaml
Runtime: python3.11
Memory: 1024 MB
Timeout: 300 seconds (5 minutos)
Environment Variables: [configuradas arriba]
IAM Role: LambdaExecutionRole con permisos básicos
```

### API Gateway Configuration

```yaml
Resource: /analyze
Method: POST
Integration: Lambda Proxy Integration
CORS: Enabled para dominios de Vercel
Rate Limiting: 100 requests/minute por IP
```

## Optimizaciones de Performance

### Caching Strategy

1. **Database Caching**: Análisis previos se almacenan y reutilizan
2. **PDF Caching**: PDFs descargados se pueden cachear temporalmente
3. **LLM Response Caching**: Respuestas similares se pueden cachear

### Memory Management

1. **Streaming PDF Processing**: Procesar PDFs en chunks para reducir memoria
2. **Lazy Loading**: Cargar servicios solo cuando se necesiten
3. **Connection Pooling**: Reutilizar conexiones MongoDB

### Cold Start Optimization

1. **Provisioned Concurrency**: Para reducir cold starts
2. **Lightweight Dependencies**: Minimizar el tamaño del deployment package
3. **Connection Reuse**: Mantener conexiones entre invocaciones

## Seguridad

### API Security

1. **API Key Authentication**: Para acceso a la Lambda
2. **Rate Limiting**: Prevenir abuso
3. **Input Validation**: Validar todos los parámetros de entrada
4. **CORS Configuration**: Restringir orígenes permitidos

### Data Security

1. **Encryption at Rest**: MongoDB Atlas con encriptación
2. **Encryption in Transit**: HTTPS para todas las comunicaciones
3. **API Key Management**: Usar AWS Secrets Manager
4. **Data Sanitization**: Limpiar datos antes de almacenar

## Monitoreo y Logging

### CloudWatch Metrics

1. **Invocation Count**: Número de invocaciones
2. **Duration**: Tiempo de ejecución
3. **Error Rate**: Tasa de errores
4. **Memory Usage**: Uso de memoria

### Custom Metrics

1. **PDF Processing Time**: Tiempo de descarga y procesamiento
2. **LLM Response Time**: Tiempo de respuesta del LLM
3. **Database Query Time**: Tiempo de queries a MongoDB
4. **Cache Hit Rate**: Tasa de aciertos de cache

### Structured Logging

```python
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def log_analysis_start(date: str):
    logger.info(json.dumps({
        'event': 'analysis_start',
        'date': date,
        'timestamp': datetime.utcnow().isoformat()
    }))
```

## Escalabilidad

### Horizontal Scaling

1. **Lambda Concurrency**: Auto-scaling basado en demanda
2. **Database Scaling**: MongoDB Atlas auto-scaling
3. **API Gateway**: Maneja múltiples requests concurrentes

### Vertical Scaling

1. **Memory Configuration**: Ajustable según necesidades
2. **Timeout Configuration**: Configurable por tipo de operación
3. **Connection Limits**: Configurables por servicio

Este diseño proporciona una base sólida para implementar el backend de la aplicación, enfocándose en la escalabilidad, mantenibilidad y performance requeridas para procesar eficientemente el Boletín Oficial de Argentina.