# API Documentation - Boletín Oficial Telegram App

## Descripción General

La API del Boletín Oficial Telegram App proporciona un endpoint REST para analizar automáticamente la normativa publicada en el Boletín Oficial de la República Argentina. Utiliza inteligencia artificial para generar análisis detallados y opiniones de expertos.

## Base URL

```
https://[api-gateway-id].execute-api.[region].amazonaws.com/[stage]
```

Ejemplo:
```
https://abc123def.execute-api.us-east-1.amazonaws.com/v1
```

## Autenticación

La API actualmente no requiere autenticación, pero implementa rate limiting para prevenir abuso.

## Rate Limiting

- **Límite por defecto**: 100 requests por minuto por IP
- **Burst limit**: 200 requests
- **Headers de respuesta**:
  - `X-RateLimit-Limit`: Límite de requests
  - `X-RateLimit-Remaining`: Requests restantes
  - `X-RateLimit-Reset`: Timestamp de reset

## Endpoints

### POST /analyze

Analiza la normativa del Boletín Oficial para una fecha específica.

#### Request

**URL**: `POST /analyze`

**Headers**:
```http
Content-Type: application/json
```

**Body**:
```json
{
  "fecha": "2024-01-15",
  "forzar_reanalisis": false
}
```

#### Parámetros

| Parámetro | Tipo | Descripción | Requerido | Default |
|-----------|------|-------------|-----------|---------|
| `fecha` | string | Fecha en formato YYYY-MM-DD | No | Fecha actual |
| `forzar_reanalisis` | boolean | Forzar nuevo análisis ignorando cache | No | `false` |

#### Validaciones

- **fecha**: Debe estar en formato YYYY-MM-DD
- **fecha**: No puede ser una fecha futura
- **fecha**: Debe ser una fecha válida
- **forzar_reanalisis**: Debe ser un valor boolean

#### Response Exitosa

**Status Code**: `200 OK`

**Headers**:
```http
Content-Type: application/json
Access-Control-Allow-Origin: *
```

**Body**:
```json
{
  "success": true,
  "data": {
    "fecha": "2024-01-15",
    "seccion": "legislacion_avisos_oficiales",
    "contenido_original": "Texto completo extraído del PDF...",
    "analisis": {
      "resumen": "Resumen ejecutivo de los cambios normativos del día. Se destacan modificaciones en el régimen tributario para PYMES y nuevas regulaciones en el sector financiero.",
      "cambios_principales": [
        {
          "tipo": "decreto",
          "numero": "123/2024",
          "titulo": "Modificación del régimen tributario para PYMES",
          "descripcion": "Establece nuevas alícuotas reducidas para empresas con facturación menor a $100M anuales",
          "impacto": "alto"
        },
        {
          "tipo": "resolucion",
          "numero": "456/2024",
          "titulo": "Nuevas normas de transparencia financiera",
          "descripcion": "Implementa requisitos adicionales de reporting para entidades financieras",
          "impacto": "medio"
        }
      ],
      "impacto_estimado": "Alto impacto en el sector PYME y medio impacto en el sector financiero. Se estima que afectará aproximadamente 50,000 empresas pequeñas y medianas.",
      "areas_afectadas": [
        "tributario",
        "pymes",
        "financiero",
        "comercial"
      ]
    },
    "opiniones_expertos": [
      {
        "fuente": "Dr. Juan Pérez - Especialista en Derecho Tributario",
        "opinion": "Esta medida representa un alivio significativo para las PYMES argentinas, especialmente en el contexto económico actual. La reducción de alícuotas podría incentivar la formalización de empresas.",
        "fecha_opinion": "2024-01-15",
        "relevancia": "alta"
      },
      {
        "fuente": "Lic. María González - Consultora Financiera",
        "opinion": "Las nuevas normas de transparencia, aunque necesarias, implicarán costos adicionales de compliance para las entidades financieras.",
        "fecha_opinion": "2024-01-15",
        "relevancia": "media"
      }
    ],
    "metadatos": {
      "fecha_creacion": "2024-01-15T10:30:00Z",
      "version_analisis": "1.0",
      "modelo_llm_usado": "gemini-2.5-pro",
      "tiempo_procesamiento": 25.5,
      "estado": "completado",
      "desde_cache": false,
      "pdf_size_bytes": 2048576,
      "text_length": 15420
    }
  },
  "message": "Análisis completado exitosamente"
}
```

#### Response de Error

**Status Codes**: `400`, `404`, `500`, `503`

**Body**:
```json
{
  "success": false,
  "error": {
    "code": "PDF_001",
    "message": "No se encontró PDF para la fecha especificada",
    "details": "No existe publicación del Boletín Oficial para la fecha 2024-01-15 o la sección de Legislación y Avisos Oficiales está vacía."
  },
  "message": "Error en el procesamiento"
}
```

## Códigos de Error

### Errores de Validación (400)

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| `VALIDATION_001` | Formato de fecha inválido | La fecha no está en formato YYYY-MM-DD |
| `VALIDATION_002` | Fecha futura no permitida | No se pueden analizar fechas futuras |
| `VALIDATION_003` | Parámetros inválidos | Los parámetros del request no son válidos |

### Errores de PDF (404/500)

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| `PDF_001` | PDF no encontrado | No existe PDF para la fecha especificada |
| `PDF_002` | Error procesando PDF | Error al descargar o procesar el PDF |
| `PDF_003` | Sección no encontrada | La sección de legislación no existe en el PDF |

### Errores de LLM (503)

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| `LLM_001` | Error en servicio de IA | Error al comunicarse con Google Gemini |
| `LLM_002` | Respuesta inválida del LLM | La respuesta del LLM no pudo ser procesada |
| `LLM_003` | Límite de tokens excedido | El texto es demasiado largo para procesar |

### Errores de Base de Datos (500)

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| `DB_001` | Error de conexión | No se pudo conectar a MongoDB |
| `DB_002` | Error de consulta | Error al ejecutar consulta en la base de datos |
| `DB_003` | Error de escritura | Error al guardar datos en la base de datos |

### Errores de Sistema (500)

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| `TIMEOUT_001` | Timeout de procesamiento | El procesamiento excedió el tiempo límite |
| `MEMORY_001` | Memoria insuficiente | No hay suficiente memoria para procesar |
| `UNKNOWN_001` | Error interno | Error interno no especificado |

## Ejemplos de Uso

### Ejemplo 1: Análisis de fecha específica

**Request**:
```bash
curl -X POST https://abc123def.execute-api.us-east-1.amazonaws.com/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "fecha": "2024-01-15"
  }'
```

**Response**:
```json
{
  "success": true,
  "data": {
    "fecha": "2024-01-15",
    "analisis": {
      "resumen": "Se publicaron 3 decretos y 2 resoluciones...",
      "cambios_principales": [...],
      "areas_afectadas": ["tributario", "laboral"]
    },
    "metadatos": {
      "tiempo_procesamiento": 18.2,
      "desde_cache": false
    }
  }
}
```

### Ejemplo 2: Forzar nuevo análisis

**Request**:
```bash
curl -X POST https://abc123def.execute-api.us-east-1.amazonaws.com/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "fecha": "2024-01-15",
    "forzar_reanalisis": true
  }'
```

### Ejemplo 3: Análisis de fecha actual

**Request**:
```bash
curl -X POST https://abc123def.execute-api.us-east-1.amazonaws.com/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Ejemplo 4: Manejo de errores

**Request con fecha futura**:
```bash
curl -X POST https://abc123def.execute-api.us-east-1.amazonaws.com/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "fecha": "2025-12-31"
  }'
```

**Response de error**:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_002",
    "message": "Fecha futura no permitida",
    "details": "No se pueden analizar fechas futuras. La fecha 2025-12-31 es posterior a la fecha actual."
  },
  "message": "Error de validación"
}
```

## Integración con JavaScript

### Ejemplo básico con fetch

```javascript
async function analizarBoletin(fecha) {
  const apiUrl = 'https://abc123def.execute-api.us-east-1.amazonaws.com/v1';
  
  try {
    const response = await fetch(`${apiUrl}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        fecha: fecha
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      console.log('Análisis completado:', data.data);
      return data.data;
    } else {
      console.error('Error en análisis:', data.error);
      throw new Error(data.error.message);
    }
  } catch (error) {
    console.error('Error de red:', error);
    throw error;
  }
}

// Uso
analizarBoletin('2024-01-15')
  .then(analisis => {
    console.log('Resumen:', analisis.analisis.resumen);
    console.log('Cambios:', analisis.analisis.cambios_principales.length);
  })
  .catch(error => {
    console.error('Error:', error.message);
  });
```

### Ejemplo con manejo de errores avanzado

```javascript
class BoletinAPI {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }
  
  async analyze(fecha, forzarReanalisis = false) {
    const url = `${this.baseUrl}/analyze`;
    const payload = { fecha };
    
    if (forzarReanalisis) {
      payload.forzar_reanalisis = true;
    }
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new APIError(data.error, response.status);
      }
      
      return data.data;
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError({
        code: 'NETWORK_ERROR',
        message: 'Error de conexión',
        details: error.message
      }, 0);
    }
  }
}

class APIError extends Error {
  constructor(errorData, statusCode) {
    super(errorData.message);
    this.code = errorData.code;
    this.details = errorData.details;
    this.statusCode = statusCode;
  }
}

// Uso
const api = new BoletinAPI('https://abc123def.execute-api.us-east-1.amazonaws.com/v1');

api.analyze('2024-01-15')
  .then(data => {
    console.log('Análisis exitoso:', data);
  })
  .catch(error => {
    if (error instanceof APIError) {
      switch (error.code) {
        case 'PDF_001':
          console.log('No hay datos para esta fecha');
          break;
        case 'VALIDATION_002':
          console.log('Fecha inválida');
          break;
        default:
          console.error('Error de API:', error.message);
      }
    } else {
      console.error('Error desconocido:', error);
    }
  });
```

## Integración con Python

### Ejemplo básico con requests

```python
import requests
import json
from datetime import datetime

class BoletinAPI:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def analyze(self, fecha=None, forzar_reanalisis=False):
        """
        Analizar boletín oficial para una fecha específica
        
        Args:
            fecha (str): Fecha en formato YYYY-MM-DD
            forzar_reanalisis (bool): Forzar nuevo análisis
            
        Returns:
            dict: Datos del análisis
            
        Raises:
            APIError: Error en la API
        """
        url = f"{self.base_url}/analyze"
        
        payload = {}
        if fecha:
            payload['fecha'] = fecha
        if forzar_reanalisis:
            payload['forzar_reanalisis'] = True
        
        try:
            response = self.session.post(url, json=payload, timeout=60)
            data = response.json()
            
            if not response.ok:
                raise APIError(data['error'], response.status_code)
            
            return data['data']
            
        except requests.exceptions.RequestException as e:
            raise APIError({
                'code': 'NETWORK_ERROR',
                'message': 'Error de conexión',
                'details': str(e)
            }, 0)

class APIError(Exception):
    def __init__(self, error_data, status_code):
        super().__init__(error_data['message'])
        self.code = error_data['code']
        self.details = error_data.get('details', '')
        self.status_code = status_code

# Uso
api = BoletinAPI('https://abc123def.execute-api.us-east-1.amazonaws.com/v1')

try:
    # Análisis de fecha específica
    resultado = api.analyze('2024-01-15')
    
    print(f"Fecha: {resultado['fecha']}")
    print(f"Resumen: {resultado['analisis']['resumen']}")
    print(f"Cambios principales: {len(resultado['analisis']['cambios_principales'])}")
    print(f"Tiempo de procesamiento: {resultado['metadatos']['tiempo_procesamiento']}s")
    
    # Mostrar cambios principales
    for cambio in resultado['analisis']['cambios_principales']:
        print(f"- {cambio['tipo'].upper()} {cambio['numero']}: {cambio['titulo']}")
    
except APIError as e:
    print(f"Error de API ({e.code}): {e}")
    if e.details:
        print(f"Detalles: {e.details}")
except Exception as e:
    print(f"Error inesperado: {e}")
```

## Mejores Prácticas

### 1. Manejo de Rate Limiting

```javascript
class RateLimitedAPI {
  constructor(baseUrl, maxRetries = 3) {
    this.baseUrl = baseUrl;
    this.maxRetries = maxRetries;
  }
  
  async makeRequest(url, options, retryCount = 0) {
    try {
      const response = await fetch(url, options);
      
      if (response.status === 429) { // Rate limited
        if (retryCount < this.maxRetries) {
          const retryAfter = response.headers.get('Retry-After') || 60;
          await this.sleep(retryAfter * 1000);
          return this.makeRequest(url, options, retryCount + 1);
        }
        throw new Error('Rate limit exceeded');
      }
      
      return response;
    } catch (error) {
      if (retryCount < this.maxRetries && this.isRetryableError(error)) {
        await this.sleep(Math.pow(2, retryCount) * 1000); // Exponential backoff
        return this.makeRequest(url, options, retryCount + 1);
      }
      throw error;
    }
  }
  
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  
  isRetryableError(error) {
    return error.name === 'TypeError' || // Network error
           error.message.includes('fetch');
  }
}
```

### 2. Cache del lado del cliente

```javascript
class CachedBoletinAPI {
  constructor(baseUrl, cacheTimeout = 3600000) { // 1 hora
    this.api = new BoletinAPI(baseUrl);
    this.cache = new Map();
    this.cacheTimeout = cacheTimeout;
  }
  
  async analyze(fecha, forzarReanalisis = false) {
    const cacheKey = `analyze_${fecha}`;
    
    if (!forzarReanalisis && this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data;
      }
    }
    
    const data = await this.api.analyze(fecha, forzarReanalisis);
    
    this.cache.set(cacheKey, {
      data: data,
      timestamp: Date.now()
    });
    
    return data;
  }
}
```

### 3. Validación de entrada

```javascript
function validateFecha(fecha) {
  if (!fecha) return null;
  
  const fechaRegex = /^\d{4}-\d{2}-\d{2}$/;
  if (!fechaRegex.test(fecha)) {
    throw new Error('Formato de fecha inválido. Use YYYY-MM-DD');
  }
  
  const fechaObj = new Date(fecha);
  if (isNaN(fechaObj.getTime())) {
    throw new Error('Fecha inválida');
  }
  
  if (fechaObj > new Date()) {
    throw new Error('No se pueden analizar fechas futuras');
  }
  
  return fecha;
}
```

## Límites y Consideraciones

### Límites de la API

- **Timeout**: 5 minutos máximo por request
- **Tamaño de respuesta**: Hasta 6MB
- **Rate limiting**: 100 requests/minuto por IP
- **Fechas**: Solo fechas pasadas y actuales

### Consideraciones de Performance

- **Cache**: Los análisis se cachean automáticamente
- **Tiempo de respuesta**: 15-60 segundos para análisis nuevos
- **Tiempo de respuesta**: 1-3 segundos para análisis cacheados
- **Disponibilidad**: El Boletín Oficial puede no tener datos todos los días

### Recomendaciones

1. **Implementar retry logic** para manejar errores temporales
2. **Usar cache del lado del cliente** para mejorar performance
3. **Validar fechas** antes de enviar requests
4. **Manejar todos los códigos de error** apropiadamente
5. **Implementar timeouts** en el cliente
6. **Monitorear rate limits** y implementar backoff

## Changelog

### v1.0.0 (2024-01-15)
- Lanzamiento inicial de la API
- Endpoint `/analyze` con análisis completo
- Soporte para cache automático
- Integración con Google Gemini LLM
- Manejo de errores estructurado

---

Para más información o soporte, consultar el [README principal](README.md) o crear un issue en el repositorio.