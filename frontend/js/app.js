// Aplicación principal del Boletín Oficial

class BoletinApp {
  constructor() {
    this.api = window.apiClient;
    this.telegram = null;
    this.currentAnalysis = null;
    this.isLoading = false;

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
    // Botón de análisis
    const analyzeBtn = document.getElementById('analyze-btn');
    analyzeBtn.addEventListener('click', () => this.handleAnalyze());

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
    const analyzeBtn = document.getElementById('analyze-btn');
    const date = datePicker.value;

    // Validar fecha
    const isValid = Utils.isValidDate(date);

    // Habilitar/deshabilitar botón
    analyzeBtn.disabled = !isValid;

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
  async handleAnalyze() {
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
      console.log('Iniciando análisis para fecha:', date, 'Forzar reanálisis:', forceReanalysis);

      this.isLoading = true;
      this.showLoading();

      // Ocultar resultados anteriores
      this.hideResults();

      // Feedback háptico
      if (this.telegram) {
        this.telegram.hapticFeedback('impact');
        this.telegram.hideMainButton();
        this.telegram.showBackButton();
      }

      // Realizar análisis con opción de forzar reanálisis
      const analysis = await this.api.analyzeDate(date, forceReanalysis);

      console.log('Análisis completado:', analysis);

      this.currentAnalysis = analysis;
      this.displayResults(analysis);

      // Feedback de éxito
      if (this.telegram) {
        this.telegram.hapticFeedback('notification', 'success');
      }

    } catch (error) {
      console.error('Error en análisis:', error);

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

    // Ocultar resultados
    this.hideResults();

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
      this.handleAnalyze();
    }, 500);
  }

  /**
   * Muestra el overlay de carga
   */
  showLoading() {
    const loadingOverlay = document.getElementById('loading-overlay');
    loadingOverlay.classList.remove('hidden');

    // Deshabilitar scroll del body
    document.body.style.overflow = 'hidden';

    console.log('Loading mostrado');
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