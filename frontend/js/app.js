// Aplicación principal del Boletín Oficial

class BoletinApp {
  constructor() {
    this.api = window.apiClient;
    this.telegram = null;
    this.currentAnalysis = null;
    this.isLoading = false;
    this.lastAction = null; // Para rastrear la última acción realizada

    this.init();
  }

  /**
   * Inicializa la aplicación
   */
  init() {
    console.log('Inicializando Boletín Oficial App...');

    // Esperar a que Telegram esté listo
    this.waitForTelegram().then(() => {
      this.telegram = window.telegramApp;
      this.setupEventListeners();
      this.setupDatePicker();
      this.loadDemoData(); // Para testing visual

      console.log('App inicializada correctamente');
    });
  }

  /**
   * Espera a que Telegram esté disponible
   */
  async waitForTelegram() {
    return new Promise((resolve) => {
      const checkTelegram = () => {
        if (window.telegramApp) {
          resolve();
        } else {
          setTimeout(checkTelegram, 100);
        }
      };
      checkTelegram();
    });
  }

  /**
   * Configura los event listeners
   */
  setupEventListeners() {
    // Botón de análisis del boletín
    const analyzeBoletinBtn = document.getElementById('analyze-boletin-btn');
    analyzeBoletinBtn.addEventListener('click', () => this.handleAnalyzeBoletin());

    // Botón de análisis de opiniones de expertos
    const analyzeExpertsBtn = document.getElementById('analyze-experts-btn');
    analyzeExpertsBtn.addEventListener('click', () => this.handleAnalyzeExperts());

    // Selector de fecha
    const datePicker = document.getElementById('date-picker');
    datePicker.addEventListener('change', () => this.handleDateChange());

    // Botón de compartir
    const shareBtn = document.getElementById('share-btn');
    shareBtn.addEventListener('click', () => this.handleShare());

    // Botón de nuevo análisis
    const newAnalysisBtn = document.getElementById('new-analysis-btn');
    newAnalysisBtn.addEventListener('click', () => this.handleNewAnalysis());

    // Botones de error modal
    const retryBtn = document.getElementById('retry-btn');
    const closeErrorBtn = document.getElementById('close-error-btn');

    retryBtn.addEventListener('click', () => this.handleRetry());
    closeErrorBtn.addEventListener('click', () => this.hideError());

    // Cerrar modal de error al hacer click fuera
    const errorModal = document.getElementById('error-modal');
    errorModal.addEventListener('click', (e) => {
      if (e.target === errorModal) {
        this.hideError();
      }
    });

    console.log('Event listeners configurados');
  }

  /**
   * Configura el selector de fecha
   */
  setupDatePicker() {
    const datePicker = document.getElementById('date-picker');
    const today = Utils.getCurrentDate();

    // Configurar fecha máxima (hoy) y valor por defecto
    datePicker.max = today;
    datePicker.value = today;

    // Validar fecha inicial
    this.handleDateChange();

    console.log('Date picker configurado para:', today);
  }

  /**
   * Maneja el cambio de fecha
   */
  handleDateChange() {
    const datePicker = document.getElementById('date-picker');
    const date = datePicker.value;

    // Validar fecha
    const isValid = Utils.isValidDate(date);

    // Al cambiar fecha, limpiar análisis actual y resetear botón de expertos
    if (this.currentAnalysis && this.currentAnalysis.fecha !== date) {
      this.currentAnalysis = null;
      this.hideResults();
      
      // Resetear botón de expertos a estado inicial
      const analyzeExpertsBtn = document.getElementById('analyze-experts-btn');
      analyzeExpertsBtn.querySelector('.button-text').textContent = 'Analizar Opiniones de Expertos';
      analyzeExpertsBtn.classList.remove('update-mode');
    }

    // Solo actualizar estado de botones si no hay operación en curso
    if (!this.isLoading) {
      this.setButtonsState('idle');
    }

    // Actualizar botón de Telegram
    if (this.telegram) {
      if (isValid) {
        this.telegram.enableMainButton();
        this.telegram.showMainButton();
      } else {
        this.telegram.disableMainButton();
      }
    }

    console.log('Fecha seleccionada:', date, 'Válida:', isValid);
  }

  /**
   * Maneja el análisis del boletín
   */
  async handleAnalyzeBoletin() {
    const datePicker = document.getElementById('date-picker');
    const forceReanalysisCheckbox = document.getElementById('force-reanalysis');
    const date = datePicker.value;
    const forceReanalysis = forceReanalysisCheckbox ? forceReanalysisCheckbox.checked : false;

    if (!Utils.isValidDate(date)) {
      this.showError({
        title: 'Fecha Inválida',
        message: 'Por favor selecciona una fecha válida.'
      });
      return;
    }

    if (this.isLoading) {
      console.log('Ya hay un análisis en progreso');
      return;
    }

    try {
      console.log('Iniciando análisis del boletín para fecha:', date, 'Forzar reanálisis:', forceReanalysis);

      this.lastAction = 'analyze-boletin';
      this.isLoading = true;

      // Deshabilitar ambos botones durante el análisis del boletín
      this.setButtonsState('analyzing-boletin');

      this.showLoading('Analizando Boletín', 'Procesando normativa con IA...');

      // Ocultar resultados anteriores
      this.hideResults();

      // Feedback háptico
      if (this.telegram) {
        this.telegram.hapticFeedback('impact');
        this.telegram.hideMainButton();
        this.telegram.showBackButton();
      }

      // Realizar análisis del boletín solamente
      const analysis = await this.api.analyzeBoletin(date, forceReanalysis);

      console.log('Análisis del boletín completado:', analysis);

      this.currentAnalysis = analysis;
      this.displayBoletinResults(analysis);

      // Habilitar ambos botones después del análisis del boletín
      this.setButtonsState('boletin-completed');

      // Feedback de éxito
      if (this.telegram) {
        this.telegram.hapticFeedback('notification', 'success');
      }

    } catch (error) {
      console.error('Error en análisis del boletín:', error);

      const errorInfo = Utils.handleError(error);
      this.showError(errorInfo);

      // Feedback de error
      if (this.telegram) {
        this.telegram.hapticFeedback('notification', 'error');
        this.telegram.showMainButton();
        this.telegram.hideBackButton();
      }

    } finally {
      this.isLoading = false;
      this.hideLoading();
    }
  }

  /**
   * Maneja el análisis de opiniones de expertos
   */
  async handleAnalyzeExperts() {
    const datePicker = document.getElementById('date-picker');
    const analyzeExpertsBtn = document.getElementById('analyze-experts-btn');
    const date = datePicker.value;

    if (!Utils.isValidDate(date)) {
      this.showError({
        title: 'Fecha Inválida',
        message: 'Por favor selecciona una fecha válida.'
      });
      return;
    }

    if (this.isLoading) {
      console.log('Ya hay un análisis en progreso');
      return;
    }

    // Verificar si ya hay opiniones y preguntar si quiere actualizar
    // NOTA: El checkbox "forzar reanálisis" NO afecta a las opiniones de expertos
    const isUpdateMode = analyzeExpertsBtn.classList.contains('update-mode');
    if (isUpdateMode) {
      const shouldUpdate = await this.showUpdateConfirmation();
      if (!shouldUpdate) {
        console.log('Usuario canceló la actualización de opiniones');
        return;
      }
    }

    try {
      console.log('Iniciando análisis de opiniones de expertos para fecha:', date, 'Modo actualización:', isUpdateMode);

      this.lastAction = 'analyze-experts';
      this.isLoading = true;

      // Deshabilitar el botón "Analizar Boletín" mientras se obtienen opiniones
      this.setButtonsState('analyzing-experts');

      // Usar loading compacto para opiniones de expertos (no ocupar toda la pantalla)
      this.showCompactLoading(
        isUpdateMode ? 'Actualizando Opiniones...' : 'Obteniendo Opiniones...',
        analyzeExpertsBtn
      );

      // Feedback háptico
      if (this.telegram) {
        this.telegram.hapticFeedback('impact');
      }

      // Realizar análisis de opiniones de expertos (forzar actualización si es modo update)
      const expertOpinions = await this.api.getExpertOpinions(date, isUpdateMode);

      console.log('Análisis de opiniones completado:', expertOpinions);

      // Actualizar análisis actual con las opiniones
      if (this.currentAnalysis) {
        this.currentAnalysis.opiniones_expertos = expertOpinions.opiniones_expertos;
      }

      // Mostrar las opiniones de expertos
      this.displayExpertOpinions(expertOpinions.opiniones_expertos || []);

      // Mantener el botón en modo actualización
      analyzeExpertsBtn.disabled = false;
      analyzeExpertsBtn.querySelector('.button-text').textContent = 'Actualizar Opiniones de Expertos';
      analyzeExpertsBtn.classList.add('update-mode');

      // Habilitar ambos botones después del análisis de expertos
      this.setButtonsState('experts-completed');

      // Feedback de éxito
      if (this.telegram) {
        this.telegram.hapticFeedback('notification', 'success');
      }

    } catch (error) {
      console.error('Error en análisis de opiniones de expertos:', error);

      const errorInfo = Utils.handleError(error);
      this.showError(errorInfo);

      // Feedback de error
      if (this.telegram) {
        this.telegram.hapticFeedback('notification', 'error');
      }

    } finally {
      this.isLoading = false;
      this.hideCompactLoading(analyzeExpertsBtn);

      // Siempre rehabilitar ambos botones al finalizar (éxito o error)
      this.setButtonsState('experts-completed');
    }
  }

  /**
   * Muestra los resultados del análisis
   */
  displayResults(analysis) {
    console.log('Mostrando resultados:', analysis);

    const resultsSection = document.getElementById('results-section');

    // Mostrar fecha
    const resultsDate = document.getElementById('results-date');
    resultsDate.textContent = Utils.formatDate(analysis.fecha);

    // Mostrar estado de cache
    const cacheStatus = document.getElementById('cache-status');
    cacheStatus.textContent = analysis.metadatos?.desde_cache ?
      'Desde caché' : 'Análisis nuevo';
    cacheStatus.className = analysis.metadatos?.desde_cache ?
      'cache-badge' : 'cache-badge';

    // Mostrar resumen
    const analysisSummary = document.getElementById('analysis-summary');
    analysisSummary.textContent = analysis.analisis?.resumen || 'No hay resumen disponible';

    // Mostrar cambios principales
    this.displayMainChanges(analysis.analisis?.cambios_principales || []);

    // Mostrar áreas afectadas
    this.displayAffectedAreas(analysis.analisis?.areas_afectadas || []);

    // Mostrar impacto
    const estimatedImpact = document.getElementById('estimated-impact');
    estimatedImpact.textContent = analysis.analisis?.impacto_estimado || 'No hay información de impacto disponible';

    // Mostrar opiniones de expertos
    this.displayExpertOpinions(analysis.opiniones_expertos || []);

    // Mostrar sección de resultados
    resultsSection.classList.remove('hidden');

    // Scroll suave a resultados
    Utils.smoothScrollTo(resultsSection, 20);

    console.log('Resultados mostrados correctamente');
  }

  /**
   * Muestra los cambios principales
   */
  displayMainChanges(changes) {
    const container = document.getElementById('main-changes');
    container.innerHTML = '';

    if (!changes || changes.length === 0) {
      container.innerHTML = '<p class="no-data">No se encontraron cambios principales para esta fecha.</p>';
      return;
    }

    changes.forEach((change, index) => {
      const changeElement = Utils.createElement('div', { className: 'change-item' });

      changeElement.innerHTML = `
        <div class="change-header">
          <div class="change-title">${Utils.sanitizeHtml(change.titulo || 'Sin título')}</div>
          <span class="impact-badge impact-${change.impacto || 'medio'}">${(change.impacto || 'medio').toUpperCase()}</span>
        </div>
        ${change.rotulo && change.rotulo !== 'No especificado' ? `<div class="change-rotulo"><a href="https://www.google.com/search?q=${encodeURIComponent('*' + change.rotulo + '*')}" target="_blank" rel="noopener noreferrer" class="rotulo-link">${Utils.sanitizeHtml(change.rotulo)}</a></div>` : ''}
        <div class="change-description">${Utils.sanitizeHtml(change.descripcion || 'Sin descripción')}</div>
        <div class="change-meta">
          <span class="change-type">${Utils.sanitizeHtml((change.tipo || 'documento').toUpperCase())}</span>
          <span class="change-number">${Utils.sanitizeHtml(change.numero || 'S/N')}</span>
        </div>
      `;

      container.appendChild(changeElement);
    });

    console.log('Cambios principales mostrados:', changes.length);
  }

  /**
   * Muestra las áreas afectadas
   */
  displayAffectedAreas(areas) {
    const container = document.getElementById('affected-areas');
    container.innerHTML = '';

    if (!areas || areas.length === 0) {
      container.innerHTML = '<p class="no-data">No se identificaron áreas específicas afectadas.</p>';
      return;
    }

    areas.forEach(area => {
      const areaElement = Utils.createElement('span', { className: 'area-tag' });
      areaElement.textContent = Utils.capitalize(area);
      container.appendChild(areaElement);
    });

    console.log('Áreas afectadas mostradas:', areas.length);
  }

  /**
   * Muestra las opiniones de expertos
   */
  displayExpertOpinions(opinions) {
    const container = document.getElementById('expert-opinions');
    const card = document.getElementById('expert-opinions-card');

    if (!opinions || opinions.length === 0) {
      card.style.display = 'none';
      console.log('No hay opiniones de expertos');
      return;
    }

    card.style.display = 'block';
    container.innerHTML = '';

    opinions.forEach(opinion => {
      const opinionElement = Utils.createElement('div', { className: 'opinion-item' });

      // Manejar fecha de publicación
      let fechaPublicacion = opinion.fecha_publicacion || opinion.fecha_opinion;
      let fechaFormateada = 'Sin fecha';

      if (fechaPublicacion && fechaPublicacion !== 'No disponible' && Utils.isValidDate(fechaPublicacion)) {
        fechaFormateada = Utils.formatDate(fechaPublicacion);
      }

      // Determinar si hay URL disponible para crear enlace
      const medioName = opinion.medio || opinion.fuente || 'Fuente desconocida';
      const url = opinion.url;

      let medioHtml;
      if (url && url !== 'Sin URL' && url !== 'No disponible' && url.startsWith('http')) {
        // Crear enlace si hay URL válida
        medioHtml = `<a href="${Utils.sanitizeHtml(url)}" target="_blank" rel="noopener noreferrer" class="opinion-source-link">${Utils.sanitizeHtml(medioName)}</a>`;
      } else {
        // Solo texto si no hay URL
        medioHtml = Utils.sanitizeHtml(medioName);
      }

      opinionElement.innerHTML = `
        <div class="opinion-source">${medioHtml}</div>
        <div class="opinion-text">${Utils.sanitizeHtml(opinion.opinion_resumen || opinion.opinion || 'Sin opinión')}</div>
        <div class="opinion-date">${fechaFormateada}</div>
      `;

      container.appendChild(opinionElement);
    });

    console.log('Opiniones de expertos mostradas:', opinions.length);
  }

  /**
   * Maneja el compartir resultados
   */
  handleShare() {
    if (!this.currentAnalysis) {
      console.log('No hay análisis para compartir');
      return;
    }

    const shareData = {
      title: 'Análisis del Boletín Oficial',
      text: `Análisis del ${Utils.formatDate(this.currentAnalysis.fecha)}: ${Utils.truncateText(this.currentAnalysis.analisis?.resumen || '', 100)}`,
      url: window.location.href
    };

    if (this.telegram) {
      this.telegram.shareData(shareData);
      this.telegram.hapticFeedback('selection');
    } else {
      // Fallback para navegadores normales
      this.fallbackShare(shareData);
    }

    console.log('Compartiendo análisis:', shareData);
  }

  /**
   * Fallback para compartir sin Telegram
   */
  async fallbackShare(data) {
    if (navigator.share) {
      try {
        await navigator.share(data);
      } catch (error) {
        console.error('Error sharing:', error);
        await Utils.copyToClipboard(`${data.title}\n${data.text}\n${data.url}`);
        alert('Información copiada al portapapeles');
      }
    } else {
      await Utils.copyToClipboard(`${data.title}\n${data.text}\n${data.url}`);
      alert('Información copiada al portapapeles');
    }
  }

  /**
   * Maneja el nuevo análisis
   */
  handleNewAnalysis() {
    console.log('Iniciando nuevo análisis');

    // Limpiar análisis actual
    this.currentAnalysis = null;
    this.lastAction = null;

    // Ocultar resultados
    this.hideResults();

    // Resetear estado de botones
    const analyzeExpertsBtn = document.getElementById('analyze-experts-btn');

    // Limpiar cualquier estado de loading compacto
    this.hideCompactLoading(analyzeExpertsBtn);

    // Resetear texto y modo del botón de expertos
    analyzeExpertsBtn.querySelector('.button-text').textContent = 'Analizar Opiniones de Expertos';
    analyzeExpertsBtn.classList.remove('update-mode');

    // Resetear botones a estado normal (esto deshabilitará el botón de expertos)
    this.setButtonsState('idle');

    // Mostrar botón principal de Telegram
    if (this.telegram) {
      this.telegram.showMainButton();
      this.telegram.hideBackButton();
      this.telegram.hapticFeedback('selection');
    }

    // Scroll al selector de fecha
    Utils.smoothScrollTo('.date-selector', 20);
  }

  /**
   * Maneja el reintento después de error
   */
  handleRetry() {
    console.log('Reintentando análisis');

    this.hideError();

    // Esperar un momento antes de reintentar
    setTimeout(() => {
      // Reintentar la última acción realizada
      if (this.lastAction === 'analyze-experts') {
        this.handleAnalyzeExperts();
      } else {
        this.handleAnalyzeBoletin();
      }
    }, 500);
  }

  /**
   * Habilita el botón de opiniones de expertos
   */
  enableExpertOpinionsButton() {
    const analyzeExpertsBtn = document.getElementById('analyze-experts-btn');
    analyzeExpertsBtn.disabled = false;
    console.log('Botón de opiniones de expertos habilitado');
  }

  /**
   * Verifica si hay un análisis del boletín válido para la fecha actual
   * @returns {boolean} True si hay análisis del boletín válido
   */
  hasValidBoletinAnalysis() {
    const datePicker = document.getElementById('date-picker');
    const currentDate = datePicker.value;
    
    return this.currentAnalysis && 
           this.currentAnalysis.analisis && 
           this.currentAnalysis.fecha === currentDate;
  }

  /**
   * Maneja el estado de los botones durante operaciones
   */
  setButtonsState(state) {
    const analyzeBoletinBtn = document.getElementById('analyze-boletin-btn');
    const analyzeExpertsBtn = document.getElementById('analyze-experts-btn');

    switch (state) {
      case 'analyzing-boletin':
        // Durante análisis del boletín: deshabilitar ambos
        analyzeBoletinBtn.disabled = true;
        analyzeExpertsBtn.disabled = true;
        console.log('Botones deshabilitados - analizando boletín');
        break;

      case 'analyzing-experts':
        // Durante análisis de expertos: deshabilitar boletín, expertos en loading
        analyzeBoletinBtn.disabled = true;
        // analyzeExpertsBtn se maneja en showCompactLoading
        console.log('Botón boletín deshabilitado - analizando expertos');
        break;

      case 'idle':
        // Estado normal: habilitar boletín si hay fecha válida, expertos solo si hay análisis
        const datePicker = document.getElementById('date-picker');
        const isValidDate = Utils.isValidDate(datePicker.value);
        const hasBoletinAnalysis = this.hasValidBoletinAnalysis();

        analyzeBoletinBtn.disabled = !isValidDate;
        // El botón de expertos requiere fecha válida Y análisis del boletín para esa fecha
        analyzeExpertsBtn.disabled = !isValidDate || !hasBoletinAnalysis;
        
        console.log('Botones en estado normal - fecha válida:', isValidDate, 'tiene análisis:', hasBoletinAnalysis);
        break;

      case 'boletin-completed':
        // Después del análisis del boletín: habilitar ambos
        analyzeBoletinBtn.disabled = false;
        analyzeExpertsBtn.disabled = false;
        console.log('Botones habilitados - boletín completado');
        break;

      case 'experts-completed':
        // Después del análisis de expertos: habilitar ambos
        analyzeBoletinBtn.disabled = false;
        analyzeExpertsBtn.disabled = false;
        console.log('Botones habilitados - expertos completado');
        break;
    }
  }

  /**
   * Muestra confirmación para actualizar opiniones existentes
   */
  async showUpdateConfirmation() {
    return new Promise((resolve) => {
      // Crear modal de confirmación compacto para mini app
      const confirmModal = document.createElement('div');
      confirmModal.className = 'update-confirmation-modal';
      confirmModal.innerHTML = `
        <div class="update-confirmation-content">
          <div class="update-confirmation-header">
            <h3>Actualizar Opiniones</h3>
          </div>
          <div class="update-confirmation-body">
            <p>Ya tienes opiniones de expertos para esta fecha.</p>
            <p>¿Quieres buscar opiniones más recientes?</p>
          </div>
          <div class="update-confirmation-actions">
            <button id="update-cancel-btn" class="update-btn secondary">Cancelar</button>
            <button id="update-confirm-btn" class="update-btn primary">Actualizar</button>
          </div>
        </div>
      `;

      // Agregar al DOM
      document.body.appendChild(confirmModal);

      // Event listeners
      const cancelBtn = confirmModal.querySelector('#update-cancel-btn');
      const confirmBtn = confirmModal.querySelector('#update-confirm-btn');

      const cleanup = () => {
        document.body.removeChild(confirmModal);
        document.body.style.overflow = '';
      };

      cancelBtn.addEventListener('click', () => {
        cleanup();
        resolve(false);
      });

      confirmBtn.addEventListener('click', () => {
        cleanup();
        resolve(true);
      });

      // Cerrar al hacer click fuera (solo en el fondo)
      confirmModal.addEventListener('click', (e) => {
        if (e.target === confirmModal) {
          cleanup();
          resolve(false);
        }
      });

      // Deshabilitar scroll del body
      document.body.style.overflow = 'hidden';

      // Feedback háptico si está disponible
      if (this.telegram) {
        this.telegram.hapticFeedback('impact');
      }

      console.log('Modal de confirmación de actualización mostrado');
    });
  }

  /**
   * Muestra los resultados del análisis del boletín (incluyendo opiniones si están disponibles)
   */
  displayBoletinResults(analysis) {
    console.log('Mostrando resultados del boletín:', analysis);

    const resultsSection = document.getElementById('results-section');

    // Mostrar fecha
    const resultsDate = document.getElementById('results-date');
    resultsDate.textContent = Utils.formatDate(analysis.fecha);

    // Mostrar estado de cache
    const cacheStatus = document.getElementById('cache-status');
    cacheStatus.textContent = analysis.metadatos?.desde_cache ?
      'Desde caché' : 'Análisis nuevo';
    cacheStatus.className = analysis.metadatos?.desde_cache ?
      'cache-badge' : 'cache-badge';

    // Mostrar resumen
    const analysisSummary = document.getElementById('analysis-summary');
    analysisSummary.textContent = analysis.analisis?.resumen || 'No hay resumen disponible';

    // Mostrar cambios principales
    this.displayMainChanges(analysis.analisis?.cambios_principales || []);

    // Mostrar áreas afectadas
    this.displayAffectedAreas(analysis.analisis?.areas_afectadas || []);

    // Mostrar impacto
    const estimatedImpact = document.getElementById('estimated-impact');
    estimatedImpact.textContent = analysis.analisis?.impacto_estimado || 'No hay información de impacto disponible';

    // Mostrar opiniones de expertos si están disponibles
    const expertOpinions = analysis.opiniones_expertos || [];
    this.displayExpertOpinions(expertOpinions);

    // Si ya hay opiniones de expertos, cambiar el texto del botón
    const analyzeExpertsBtn = document.getElementById('analyze-experts-btn');
    if (expertOpinions.length > 0) {
      analyzeExpertsBtn.disabled = false;
      analyzeExpertsBtn.querySelector('.button-text').textContent = 'Actualizar Opiniones de Expertos';
      analyzeExpertsBtn.classList.add('update-mode');
      console.log('Botón de expertos en modo actualización - opiniones disponibles');
    } else {
      analyzeExpertsBtn.disabled = false;
      analyzeExpertsBtn.querySelector('.button-text').textContent = 'Analizar Opiniones de Expertos';
      analyzeExpertsBtn.classList.remove('update-mode');
      console.log('Botón de expertos habilitado - no hay opiniones');
    }

    // Mostrar sección de resultados
    resultsSection.classList.remove('hidden');

    // Scroll suave a resultados
    Utils.smoothScrollTo(resultsSection, 20);

    console.log('Resultados del boletín mostrados correctamente', {
      hasExpertOpinions: expertOpinions.length > 0,
      expertOpinionsCount: expertOpinions.length
    });
  }

  /**
   * Muestra el overlay de carga
   */
  showLoading(title = 'Analizando Boletín', message = 'Procesando normativa con IA...') {
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingTitle = document.querySelector('.loading-title');
    const loadingMessage = document.querySelector('.loading-message');

    loadingTitle.textContent = title;
    loadingMessage.textContent = message;

    loadingOverlay.classList.remove('hidden');

    // Deshabilitar scroll del body
    document.body.style.overflow = 'hidden';

    console.log('Loading mostrado:', title);
  }

  /**
   * Muestra loading compacto en el botón (no ocupa toda la pantalla)
   */
  showCompactLoading(message, button) {
    // Guardar texto original del botón
    const originalText = button.querySelector('.button-text').textContent;
    button.setAttribute('data-original-text', originalText);

    // Cambiar texto del botón
    button.querySelector('.button-text').textContent = message;

    // Agregar clase de loading
    button.classList.add('loading');
    button.disabled = true;

    // Cambiar icono por spinner
    const buttonIcon = button.querySelector('.button-icon');
    if (buttonIcon) {
      buttonIcon.style.display = 'none';

      // Crear spinner compacto
      const spinner = document.createElement('div');
      spinner.className = 'compact-spinner';
      spinner.innerHTML = '<div class="spinner-dot"></div><div class="spinner-dot"></div><div class="spinner-dot"></div>';
      button.insertBefore(spinner, button.querySelector('.button-text'));
    }

    console.log('Compact loading mostrado:', message);
  }

  /**
   * Oculta loading compacto del botón
   */
  hideCompactLoading(button) {
    // Restaurar texto original
    const originalText = button.getAttribute('data-original-text');
    if (originalText) {
      button.querySelector('.button-text').textContent = originalText;
      button.removeAttribute('data-original-text');
    }

    // Quitar clase de loading
    button.classList.remove('loading');
    button.disabled = false;

    // Restaurar icono
    const buttonIcon = button.querySelector('.button-icon');
    const spinner = button.querySelector('.compact-spinner');

    if (buttonIcon) {
      buttonIcon.style.display = '';
    }

    if (spinner) {
      button.removeChild(spinner);
    }

    console.log('Compact loading ocultado');
  }

  /**
   * Oculta el overlay de carga
   */
  hideLoading() {
    const loadingOverlay = document.getElementById('loading-overlay');
    loadingOverlay.classList.add('hidden');

    // Rehabilitar scroll del body
    document.body.style.overflow = '';

    console.log('Loading ocultado');
  }

  /**
   * Muestra un error
   */
  showError(error) {
    const errorModal = document.getElementById('error-modal');
    const errorTitle = document.getElementById('error-title');
    const errorMessage = document.getElementById('error-message');

    errorTitle.textContent = error.title || 'Error';
    errorMessage.textContent = error.message || 'Ha ocurrido un error inesperado';

    errorModal.classList.remove('hidden');

    // Deshabilitar scroll del body
    document.body.style.overflow = 'hidden';

    console.log('Error mostrado:', error);
  }

  /**
   * Oculta el error
   */
  hideError() {
    const errorModal = document.getElementById('error-modal');
    errorModal.classList.add('hidden');

    // Rehabilitar scroll del body
    document.body.style.overflow = '';

    console.log('Error ocultado');
  }

  /**
   * Oculta los resultados
   */
  hideResults() {
    const resultsSection = document.getElementById('results-section');
    resultsSection.classList.add('hidden');

    console.log('Resultados ocultados');
  }

  /**
   * Carga datos de demostración para testing visual
   */
  loadDemoData() {
    // Solo en desarrollo o para testing
    if (window.location.hostname === 'localhost' || window.location.search.includes('demo=true')) {
      console.log('Cargando datos de demostración...');

      // Simular análisis después de 2 segundos
      setTimeout(() => {
        if (window.location.search.includes('demo=true')) {
          this.loadDemoAnalysis();
        }
      }, 2000);
    }
  }

  /**
   * Carga un análisis de demostración
   */
  loadDemoAnalysis() {
    const demoAnalysis = {
      fecha: Utils.getCurrentDate(),
      analisis: {
        resumen: "Se publicaron importantes modificaciones en materia tributaria y laboral. Las nuevas disposiciones incluyen cambios en las alícuotas del impuesto a las ganancias y actualizaciones en el régimen de trabajo remoto.",
        cambios_principales: [
          {
            tipo: "decreto",
            numero: "123/2024",
            titulo: "Modificación del Impuesto a las Ganancias",
            descripcion: "Se establecen nuevas alícuotas para personas físicas y jurídicas, con vigencia a partir del próximo mes.",
            impacto: "alto"
          },
          {
            tipo: "resolución",
            numero: "456/2024",
            titulo: "Régimen de Trabajo Remoto",
            descripcion: "Actualización de las condiciones para el trabajo a distancia en el sector público.",
            impacto: "medio"
          }
        ],
        areas_afectadas: ["tributario", "laboral", "administrativo"],
        impacto_estimado: "Las modificaciones tendrán un impacto significativo en la planificación fiscal de empresas y particulares. Se recomienda revisar las estructuras tributarias actuales."
      },
      opiniones_expertos: [
        {
          fuente: "Dr. Juan Pérez - Especialista en Derecho Tributario",
          opinion: "Estos cambios representan una modernización necesaria del sistema tributario, aunque requerirán un período de adaptación.",
          fecha_opinion: Utils.getCurrentDate()
        }
      ],
      metadatos: {
        desde_cache: false,
        fecha_creacion: new Date().toISOString(),
        tiempo_procesamiento: 45.2
      }
    };

    this.currentAnalysis = demoAnalysis;
    this.displayResults(demoAnalysis);

    console.log('Análisis de demostración cargado');
  }
}

// Inicializar aplicación cuando se carga el DOM
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM cargado, inicializando aplicación...');
  window.boletinApp = new BoletinApp();
});