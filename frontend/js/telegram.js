// Integración con Telegram Web App SDK

class TelegramIntegration {
  constructor() {
    this.tg = window.Telegram?.WebApp;
    this.isReady = false;
    this.user = null;
    this.theme = null;
    
    this.init();
  }

  /**
   * Inicializa la integración con Telegram
   */
  init() {
    if (!this.tg) {
      console.warn('Telegram WebApp SDK no disponible');
      this.setupFallback();
      return;
    }

    console.log('Inicializando Telegram WebApp...');

    // Configurar tema
    this.setupTheme();
    
    // Obtener información del usuario
    this.setupUser();
    
    // Configurar botones
    this.setupMainButton();
    this.setupBackButton();
    
    // Configurar eventos
    this.setupEvents();
    
    // Expandir aplicación
    this.tg.expand();
    
    // Habilitar cierre por confirmación
    this.tg.enableClosingConfirmation();
    
    // Marcar como listo
    this.tg.ready();
    this.isReady = true;

    console.log('Telegram WebApp inicializado correctamente');
    console.log('Usuario:', this.user);
    console.log('Tema:', this.theme);
  }

  /**
   * Configura el tema de la aplicación basado en Telegram
   */
  setupTheme() {
    if (!this.tg) return;

    this.theme = this.tg.themeParams;
    
    // Aplicar colores del tema de Telegram si están disponibles
    const root = document.documentElement;
    
    if (this.theme.bg_color) {
      root.style.setProperty('--telegram-bg', this.theme.bg_color);
    }
    
    if (this.theme.text_color) {
      root.style.setProperty('--telegram-text', this.theme.text_color);
    }
    
    if (this.theme.hint_color) {
      root.style.setProperty('--telegram-hint', this.theme.hint_color);
    }
    
    if (this.theme.link_color) {
      root.style.setProperty('--telegram-link', this.theme.link_color);
    }
    
    if (this.theme.button_color) {
      root.style.setProperty('--telegram-button', this.theme.button_color);
    }
    
    if (this.theme.button_text_color) {
      root.style.setProperty('--telegram-button-text', this.theme.button_text_color);
    }

    // Aplicar tema oscuro si es necesario
    if (this.tg.colorScheme === 'dark') {
      document.body.classList.add('telegram-dark-theme');
    }
  }

  /**
   * Obtiene información del usuario de Telegram
   */
  setupUser() {
    if (!this.tg) return;

    const initData = this.tg.initDataUnsafe;
    
    if (initData.user) {
      this.user = {
        id: initData.user.id,
        firstName: initData.user.first_name,
        lastName: initData.user.last_name,
        username: initData.user.username,
        languageCode: initData.user.language_code,
        isPremium: initData.user.is_premium || false
      };
    }
  }

  /**
   * Configura el botón principal de Telegram
   */
  setupMainButton() {
    if (!this.tg?.MainButton) return;

    this.tg.MainButton.setText('Analizar Boletín');
    this.tg.MainButton.color = '#0088cc';
    this.tg.MainButton.textColor = '#ffffff';
    
    // Manejar click del botón principal
    this.tg.MainButton.onClick(() => {
      this.hapticFeedback('impact');
      
      const analyzeBtn = document.getElementById('analyze-btn');
      if (analyzeBtn && !analyzeBtn.disabled) {
        analyzeBtn.click();
      }
    });
  }

  /**
   * Configura el botón de retroceso de Telegram
   */
  setupBackButton() {
    if (!this.tg?.BackButton) return;

    this.tg.BackButton.onClick(() => {
      this.hapticFeedback('impact');
      
      // Si hay resultados visibles, volver al selector de fecha
      const resultsSection = document.getElementById('results-section');
      if (resultsSection && !resultsSection.classList.contains('hidden')) {
        const newAnalysisBtn = document.getElementById('new-analysis-btn');
        if (newAnalysisBtn) {
          newAnalysisBtn.click();
        }
      } else {
        // Cerrar la aplicación
        this.tg.close();
      }
    });
  }

  /**
   * Configura eventos de Telegram
   */
  setupEvents() {
    if (!this.tg) return;

    // Evento cuando cambia el viewport
    this.tg.onEvent('viewportChanged', () => {
      console.log('Viewport changed:', this.tg.viewportHeight);
      this.adjustLayout();
    });

    // Evento cuando cambia el tema
    this.tg.onEvent('themeChanged', () => {
      console.log('Theme changed');
      this.setupTheme();
    });

    // Evento cuando se cierra la aplicación
    this.tg.onEvent('mainButtonClicked', () => {
      console.log('Main button clicked');
    });
  }

  /**
   * Ajusta el layout basado en el viewport de Telegram
   */
  adjustLayout() {
    if (!this.tg) return;

    const viewportHeight = this.tg.viewportHeight;
    const isExpanded = this.tg.isExpanded;

    // Ajustar altura mínima del contenido
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
      mainContent.style.minHeight = `${viewportHeight - 120}px`;
    }

    console.log(`Layout adjusted - Height: ${viewportHeight}px, Expanded: ${isExpanded}`);
  }

  /**
   * Muestra el botón principal
   * @param {string} text - Texto del botón
   * @param {string} color - Color del botón
   */
  showMainButton(text = 'Analizar Boletín', color = '#0088cc') {
    if (!this.tg?.MainButton) return;

    this.tg.MainButton.setText(text);
    this.tg.MainButton.color = color;
    this.tg.MainButton.show();
  }

  /**
   * Oculta el botón principal
   */
  hideMainButton() {
    if (!this.tg?.MainButton) return;
    this.tg.MainButton.hide();
  }

  /**
   * Habilita el botón principal
   */
  enableMainButton() {
    if (!this.tg?.MainButton) return;
    this.tg.MainButton.enable();
  }

  /**
   * Deshabilita el botón principal
   */
  disableMainButton() {
    if (!this.tg?.MainButton) return;
    this.tg.MainButton.disable();
  }

  /**
   * Muestra el botón de retroceso
   */
  showBackButton() {
    if (!this.tg?.BackButton) return;
    this.tg.BackButton.show();
  }

  /**
   * Oculta el botón de retroceso
   */
  hideBackButton() {
    if (!this.tg?.BackButton) return;
    this.tg.BackButton.hide();
  }

  /**
   * Comparte datos usando la API de Telegram
   * @param {Object} data - Datos a compartir
   */
  shareData(data) {
    if (!this.tg) {
      this.fallbackShare(data);
      return;
    }

    const shareText = `${data.title}\n\n${data.text}`;
    
    try {
      // Usar API de Telegram para compartir
      this.tg.switchInlineQuery(shareText, ['users', 'groups', 'channels']);
    } catch (error) {
      console.error('Error sharing via Telegram:', error);
      this.fallbackShare(data);
    }
  }

  /**
   * Fallback para compartir en navegadores normales
   * @param {Object} data - Datos a compartir
   */
  async fallbackShare(data) {
    const shareText = `${data.title}\n${data.text}\n${data.url || window.location.href}`;

    if (navigator.share) {
      try {
        await navigator.share({
          title: data.title,
          text: data.text,
          url: data.url || window.location.href
        });
      } catch (error) {
        console.error('Error sharing:', error);
        this.copyToClipboard(shareText);
      }
    } else {
      this.copyToClipboard(shareText);
    }
  }

  /**
   * Copia texto al portapapeles y muestra notificación
   * @param {string} text - Texto a copiar
   */
  async copyToClipboard(text) {
    const success = await Utils.copyToClipboard(text);
    
    if (success) {
      this.showAlert('Información copiada al portapapeles');
      this.hapticFeedback('notification');
    } else {
      this.showAlert('No se pudo copiar la información');
    }
  }

  /**
   * Muestra una alerta
   * @param {string} message - Mensaje a mostrar
   */
  showAlert(message) {
    if (this.tg) {
      this.tg.showAlert(message);
    } else {
      alert(message);
    }
  }

  /**
   * Muestra un popup de confirmación
   * @param {string} message - Mensaje de confirmación
   * @param {Function} callback - Callback con el resultado
   */
  showConfirm(message, callback) {
    if (this.tg) {
      this.tg.showConfirm(message, callback);
    } else {
      const result = confirm(message);
      callback(result);
    }
  }

  /**
   * Muestra un popup con botones personalizados
   * @param {string} title - Título del popup
   * @param {string} message - Mensaje del popup
   * @param {Array} buttons - Array de botones
   * @param {Function} callback - Callback con el resultado
   */
  showPopup(title, message, buttons, callback) {
    if (this.tg) {
      this.tg.showPopup({
        title: title,
        message: message,
        buttons: buttons
      }, callback);
    } else {
      // Fallback simple
      const result = confirm(`${title}\n\n${message}`);
      callback(result ? buttons[0]?.id : null);
    }
  }

  /**
   * Proporciona feedback háptico
   * @param {string} type - Tipo de feedback ('impact', 'notification', 'selection')
   * @param {string} style - Estilo del feedback ('light', 'medium', 'heavy')
   */
  hapticFeedback(type = 'impact', style = 'medium') {
    if (!this.tg?.HapticFeedback) return;

    try {
      switch (type) {
        case 'impact':
          this.tg.HapticFeedback.impactOccurred(style);
          break;
        case 'notification':
          this.tg.HapticFeedback.notificationOccurred(style);
          break;
        case 'selection':
          this.tg.HapticFeedback.selectionChanged();
          break;
      }
    } catch (error) {
      console.error('Error with haptic feedback:', error);
    }
  }

  /**
   * Abre un enlace externo
   * @param {string} url - URL a abrir
   */
  openLink(url) {
    if (this.tg) {
      this.tg.openLink(url);
    } else {
      window.open(url, '_blank');
    }
  }

  /**
   * Cierra la aplicación
   */
  close() {
    if (this.tg) {
      this.tg.close();
    } else {
      window.close();
    }
  }

  /**
   * Configura fallback para cuando no está en Telegram
   */
  setupFallback() {
    console.log('Configurando fallback para navegador normal');
    
    // Simular usuario para testing
    this.user = {
      id: 'demo',
      firstName: 'Usuario',
      lastName: 'Demo',
      username: 'demo_user',
      languageCode: 'es',
      isPremium: false
    };

    // Configurar tema por defecto
    this.theme = {
      bg_color: '#ffffff',
      text_color: '#000000',
      hint_color: '#999999',
      link_color: '#0088cc',
      button_color: '#0088cc',
      button_text_color: '#ffffff'
    };

    this.isReady = true;
  }

  /**
   * Obtiene información del entorno
   * @returns {Object} Información del entorno
   */
  getEnvironmentInfo() {
    return {
      isTelegram: !!this.tg,
      isReady: this.isReady,
      user: this.user,
      theme: this.theme,
      platform: this.tg?.platform || 'web',
      version: this.tg?.version || 'unknown',
      colorScheme: this.tg?.colorScheme || 'light',
      viewportHeight: this.tg?.viewportHeight || window.innerHeight,
      isExpanded: this.tg?.isExpanded || false
    };
  }
}

// Crear instancia global
window.TelegramIntegration = TelegramIntegration;

// Inicializar automáticamente cuando se carga el DOM
document.addEventListener('DOMContentLoaded', () => {
  window.telegramApp = new TelegramIntegration();
});