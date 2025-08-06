// Utilidades generales para la aplicación

class Utils {
  /**
   * Formatea una fecha en formato español
   * @param {string} dateString - Fecha en formato ISO
   * @returns {string} Fecha formateada
   */
  static formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-AR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }

  /**
   * Formatea una fecha para mostrar en formato corto
   * @param {string} dateString - Fecha en formato ISO
   * @returns {string} Fecha formateada corta
   */
  static formatDateShort(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-AR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  }

  /**
   * Obtiene la fecha actual en formato YYYY-MM-DD
   * @returns {string} Fecha actual
   */
  static getCurrentDate() {
    return new Date().toISOString().split('T')[0];
  }

  /**
   * Valida si una fecha es válida y no es futura
   * @param {string} dateString - Fecha a validar
   * @returns {boolean} True si es válida
   */
  static isValidDate(dateString) {
    if (!dateString) return false;
    
    const date = new Date(dateString);
    const today = new Date();
    
    // Verificar que sea una fecha válida
    if (isNaN(date.getTime())) return false;
    
    // Verificar que no sea futura
    if (date > today) return false;
    
    return true;
  }

  /**
   * Capitaliza la primera letra de una cadena
   * @param {string} str - Cadena a capitalizar
   * @returns {string} Cadena capitalizada
   */
  static capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  /**
   * Trunca un texto a una longitud específica
   * @param {string} text - Texto a truncar
   * @param {number} maxLength - Longitud máxima
   * @returns {string} Texto truncado
   */
  static truncateText(text, maxLength = 100) {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  }

  /**
   * Debounce function para limitar la frecuencia de ejecución
   * @param {Function} func - Función a ejecutar
   * @param {number} wait - Tiempo de espera en ms
   * @returns {Function} Función debounced
   */
  static debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  /**
   * Throttle function para limitar la frecuencia de ejecución
   * @param {Function} func - Función a ejecutar
   * @param {number} limit - Límite de tiempo en ms
   * @returns {Function} Función throttled
   */
  static throttle(func, limit) {
    let inThrottle;
    return function(...args) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }

  /**
   * Genera un ID único
   * @returns {string} ID único
   */
  static generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  }

  /**
   * Copia texto al portapapeles
   * @param {string} text - Texto a copiar
   * @returns {Promise<boolean>} True si se copió exitosamente
   */
  static async copyToClipboard(text) {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        return true;
      } else {
        // Fallback para navegadores más antiguos
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        const result = document.execCommand('copy');
        document.body.removeChild(textArea);
        return result;
      }
    } catch (error) {
      console.error('Error copying to clipboard:', error);
      return false;
    }
  }

  /**
   * Detecta si el dispositivo es móvil
   * @returns {boolean} True si es móvil
   */
  static isMobile() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  }

  /**
   * Detecta si está en Telegram
   * @returns {boolean} True si está en Telegram
   */
  static isTelegram() {
    return window.Telegram && window.Telegram.WebApp;
  }

  /**
   * Scroll suave a un elemento
   * @param {string|Element} target - Selector o elemento
   * @param {number} offset - Offset en pixels
   */
  static smoothScrollTo(target, offset = 0) {
    const element = typeof target === 'string' ? document.querySelector(target) : target;
    if (!element) return;

    const elementPosition = element.getBoundingClientRect().top;
    const offsetPosition = elementPosition + window.pageYOffset - offset;

    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    });
  }

  /**
   * Maneja errores de forma consistente
   * @param {Error} error - Error a manejar
   * @returns {Object} Objeto de error normalizado
   */
  static handleError(error) {
    console.error('Error:', error);

    // Errores de red
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      return {
        title: 'Error de Conexión',
        message: 'No se pudo conectar con el servidor. Verifica tu conexión a internet.',
        code: 'NETWORK_ERROR'
      };
    }

    // Timeout
    if (error.name === 'AbortError' || error.message.includes('timeout')) {
      return {
        title: 'Tiempo Agotado',
        message: 'La solicitud tardó demasiado tiempo. Inténtalo nuevamente.',
        code: 'TIMEOUT_ERROR'
      };
    }

    // Error de API
    if (error.response) {
      return {
        title: 'Error del Servidor',
        message: error.response.message || 'El servidor respondió con un error.',
        code: error.response.code || 'API_ERROR'
      };
    }

    // Error genérico
    return {
      title: 'Error Inesperado',
      message: error.message || 'Ha ocurrido un error inesperado.',
      code: 'UNKNOWN_ERROR'
    };
  }

  /**
   * Valida un email
   * @param {string} email - Email a validar
   * @returns {boolean} True si es válido
   */
  static isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  /**
   * Sanitiza HTML para prevenir XSS
   * @param {string} html - HTML a sanitizar
   * @returns {string} HTML sanitizado
   */
  static sanitizeHtml(html) {
    const div = document.createElement('div');
    div.textContent = html;
    return div.innerHTML;
  }

  /**
   * Formatea números con separadores de miles
   * @param {number} num - Número a formatear
   * @returns {string} Número formateado
   */
  static formatNumber(num) {
    return new Intl.NumberFormat('es-AR').format(num);
  }

  /**
   * Calcula el tiempo transcurrido desde una fecha
   * @param {string} dateString - Fecha en formato ISO
   * @returns {string} Tiempo transcurrido
   */
  static timeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);

    if (diffInSeconds < 60) {
      return 'hace unos segundos';
    }

    const diffInMinutes = Math.floor(diffInSeconds / 60);
    if (diffInMinutes < 60) {
      return `hace ${diffInMinutes} minuto${diffInMinutes > 1 ? 's' : ''}`;
    }

    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) {
      return `hace ${diffInHours} hora${diffInHours > 1 ? 's' : ''}`;
    }

    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 30) {
      return `hace ${diffInDays} día${diffInDays > 1 ? 's' : ''}`;
    }

    return this.formatDate(dateString);
  }

  /**
   * Crea un elemento DOM con atributos
   * @param {string} tag - Tag del elemento
   * @param {Object} attributes - Atributos del elemento
   * @param {string} content - Contenido del elemento
   * @returns {Element} Elemento creado
   */
  static createElement(tag, attributes = {}, content = '') {
    const element = document.createElement(tag);
    
    Object.entries(attributes).forEach(([key, value]) => {
      if (key === 'className') {
        element.className = value;
      } else if (key === 'innerHTML') {
        element.innerHTML = value;
      } else {
        element.setAttribute(key, value);
      }
    });

    if (content) {
      element.textContent = content;
    }

    return element;
  }

  /**
   * Almacena datos en localStorage de forma segura
   * @param {string} key - Clave
   * @param {any} value - Valor a almacenar
   * @returns {boolean} True si se almacenó exitosamente
   */
  static setLocalStorage(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      console.error('Error saving to localStorage:', error);
      return false;
    }
  }

  /**
   * Obtiene datos de localStorage de forma segura
   * @param {string} key - Clave
   * @param {any} defaultValue - Valor por defecto
   * @returns {any} Valor almacenado o valor por defecto
   */
  static getLocalStorage(key, defaultValue = null) {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.error('Error reading from localStorage:', error);
      return defaultValue;
    }
  }

  /**
   * Elimina datos de localStorage
   * @param {string} key - Clave a eliminar
   * @returns {boolean} True si se eliminó exitosamente
   */
  static removeLocalStorage(key) {
    try {
      localStorage.removeItem(key);
      return true;
    } catch (error) {
      console.error('Error removing from localStorage:', error);
      return false;
    }
  }
}

// Exportar para uso global
window.Utils = Utils;