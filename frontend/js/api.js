// Cliente API para comunicación con el backend

class APIClient {
  constructor() {
    // URL base de la API - URL real de tu API Gateway
    this.baseURL = 'https://xf4vwg8gq7.execute-api.us-east-1.amazonaws.com/v1';
    this.timeout = 120000; // 120 segundos (para análisis largos)
    this.retryAttempts = 2; // Reducido porque los análisis son largos
    this.retryDelay = 2000; // 2 segundos
  }

  /**
   * Analiza el boletín para una fecha específica
   * @param {string} date - Fecha en formato YYYY-MM-DD
   * @param {boolean} forceReanalysis - Forzar reanálisis
   * @returns {Promise<Object>} Resultado del análisis
   */
  async analyzeDate(date, forceReanalysis = false) {
    console.log('🔍 APIClient.analyzeDate called with:', { date, forceReanalysis });
    
    const payload = {
      fecha: date,
      forzar_reanalisis: forceReanalysis
    };
    
    console.log('📤 Sending payload:', JSON.stringify(payload, null, 2));
    
    const response = await this.makeRequest('/analyze', {
      method: 'POST',
      body: JSON.stringify(payload)
    });

    if (!response.success) {
      throw new Error(response.message || 'Error en el análisis');
    }

    return response.data;
  }

  /**
   * Obtiene el estado de salud de la API
   * @returns {Promise<Object>} Estado de la API
   */
  async getHealthStatus() {
    try {
      const response = await this.makeRequest('/health', {
        method: 'GET'
      });
      return response;
    } catch (error) {
      return { status: 'error', message: error.message };
    }
  }

  /**
   * Realiza una petición HTTP con reintentos y manejo de errores
   * @param {string} endpoint - Endpoint de la API
   * @param {Object} options - Opciones de la petición
   * @returns {Promise<Object>} Respuesta de la API
   */
  async makeRequest(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;

    const defaultOptions = {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      timeout: this.timeout
    };

    const finalOptions = { ...defaultOptions, ...options };

    // Intentar la petición con reintentos
    for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
      try {
        const response = await this.fetchWithTimeout(url, finalOptions);

        if (!response.ok) {
          const errorData = await this.parseErrorResponse(response);
          throw new APIError(errorData.message, response.status, errorData.code);
        }

        const data = await response.json();
        return data;

      } catch (error) {
        console.error(`API request attempt ${attempt} failed:`, error);

        // Si es el último intento, lanzar el error
        if (attempt === this.retryAttempts) {
          throw this.normalizeError(error);
        }

        // Si es un error que no vale la pena reintentar, lanzar inmediatamente
        if (this.isNonRetryableError(error)) {
          throw this.normalizeError(error);
        }

        // Esperar antes del siguiente intento
        await this.delay(this.retryDelay * attempt);
      }
    }
  }

  /**
   * Fetch con timeout
   * @param {string} url - URL de la petición
   * @param {Object} options - Opciones de la petición
   * @returns {Promise<Response>} Respuesta HTTP
   */
  async fetchWithTimeout(url, options) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), options.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal
      });

      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }

  /**
   * Parsea la respuesta de error de la API
   * @param {Response} response - Respuesta HTTP
   * @returns {Promise<Object>} Datos del error
   */
  async parseErrorResponse(response) {
    try {
      const errorData = await response.json();
      return {
        message: errorData.message || `HTTP ${response.status}: ${response.statusText}`,
        code: errorData.code || `HTTP_${response.status}`,
        details: errorData.details || null
      };
    } catch (parseError) {
      return {
        message: `HTTP ${response.status}: ${response.statusText}`,
        code: `HTTP_${response.status}`,
        details: null
      };
    }
  }

  /**
   * Normaliza errores para manejo consistente
   * @param {Error} error - Error original
   * @returns {Error} Error normalizado
   */
  normalizeError(error) {
    if (error instanceof APIError) {
      return error;
    }

    if (error.name === 'AbortError') {
      return new APIError('La solicitud tardó demasiado tiempo', 408, 'TIMEOUT');
    }

    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      return new APIError('No se pudo conectar con el servidor', 0, 'NETWORK_ERROR');
    }

    return new APIError(error.message || 'Error desconocido', 500, 'UNKNOWN_ERROR');
  }

  /**
   * Determina si un error no vale la pena reintentar
   * @param {Error} error - Error a evaluar
   * @returns {boolean} True si no vale la pena reintentar
   */
  isNonRetryableError(error) {
    if (error instanceof APIError) {
      // Errores 4xx generalmente no valen la pena reintentar
      return error.status >= 400 && error.status < 500;
    }

    // Errores de red y timeout sí valen la pena reintentar
    return false;
  }

  /**
   * Delay para reintentos
   * @param {number} ms - Milisegundos a esperar
   * @returns {Promise} Promise que se resuelve después del delay
   */
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Configura la URL base de la API
   * @param {string} baseURL - Nueva URL base
   */
  setBaseURL(baseURL) {
    this.baseURL = baseURL;
  }

  /**
   * Configura el timeout de las peticiones
   * @param {number} timeout - Timeout en milisegundos
   */
  setTimeout(timeout) {
    this.timeout = timeout;
  }

  /**
   * Configura el número de reintentos
   * @param {number} attempts - Número de reintentos
   */
  setRetryAttempts(attempts) {
    this.retryAttempts = attempts;
  }
}

/**
 * Clase de error personalizada para la API
 */
class APIError extends Error {
  constructor(message, status = 500, code = 'API_ERROR', details = null) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.code = code;
    this.details = details;
  }

  /**
   * Convierte el error a un objeto plano
   * @returns {Object} Representación del error
   */
  toJSON() {
    return {
      name: this.name,
      message: this.message,
      status: this.status,
      code: this.code,
      details: this.details
    };
  }

  /**
   * Determina si el error es de red
   * @returns {boolean} True si es error de red
   */
  isNetworkError() {
    return this.code === 'NETWORK_ERROR' || this.status === 0;
  }

  /**
   * Determina si el error es de timeout
   * @returns {boolean} True si es error de timeout
   */
  isTimeoutError() {
    return this.code === 'TIMEOUT' || this.status === 408;
  }

  /**
   * Determina si el error es del servidor
   * @returns {boolean} True si es error del servidor
   */
  isServerError() {
    return this.status >= 500;
  }

  /**
   * Determina si el error es del cliente
   * @returns {boolean} True si es error del cliente
   */
  isClientError() {
    return this.status >= 400 && this.status < 500;
  }
}

/**
 * Configuración de la API basada en el entorno
 */
class APIConfig {
  static getConfig() {
    // Detectar entorno
    const hostname = window.location.hostname;

    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      // Desarrollo local - usar tu API Gateway real
      return {
        baseURL: 'https://xf4vwg8gq7.execute-api.us-east-1.amazonaws.com/v1',
        timeout: 120000, // 2 minutos para análisis largos
        retryAttempts: 2
      };
    } else if (hostname.includes('vercel.app') || hostname.includes('netlify.app')) {
      // Staging/Preview - usar la misma API
      return {
        baseURL: 'https://xf4vwg8gq7.execute-api.us-east-1.amazonaws.com/v1',
        timeout: 120000,
        retryAttempts: 2
      };
    } else {
      // Producción - usar la misma API
      return {
        baseURL: 'https://xf4vwg8gq7.execute-api.us-east-1.amazonaws.com/v1',
        timeout: 120000,
        retryAttempts: 2
      };
    }
  }

  static createClient() {
    const config = this.getConfig();
    const client = new APIClient();

    client.setBaseURL(config.baseURL);
    client.setTimeout(config.timeout);
    client.setRetryAttempts(config.retryAttempts);

    return client;
  }
}

// Crear instancia global del cliente API
window.APIClient = APIClient;
window.APIError = APIError;
window.APIConfig = APIConfig;

// Crear cliente configurado automáticamente
window.apiClient = APIConfig.createClient();