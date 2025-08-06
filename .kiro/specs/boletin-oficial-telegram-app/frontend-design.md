# Diseño Frontend - Telegram Mini App

## Visión General

La Telegram Mini App para el Boletín Oficial será una aplicación web responsive que replica el estilo visual de https://www.boletinoficial.gob.ar/ pero adaptada con una paleta de colores celestes para una mejor experiencia en Telegram. La aplicación será desarrollada con tecnologías web estándar y desplegada en Vercel.

## Arquitectura Frontend

### Stack Tecnológico

- **HTML5**: Estructura semántica
- **CSS3**: Estilos con CSS Grid y Flexbox
- **JavaScript Vanilla**: Lógica de aplicación sin frameworks pesados
- **Telegram Web App SDK**: Integración nativa con Telegram
- **Vercel**: Hosting y despliegue

### Estructura de Archivos

```
frontend/
├── index.html              # Página principal
├── css/
│   ├── styles.css         # Estilos principales
│   ├── telegram.css       # Estilos específicos de Telegram
│   └── responsive.css     # Media queries
├── js/
│   ├── app.js            # Lógica principal
│   ├── api.js            # Comunicación con backend
│   ├── telegram.js       # Integración Telegram SDK
│   └── utils.js          # Utilidades
├── assets/
│   ├── icons/            # Iconos SVG
│   └── images/           # Imágenes
└── vercel.json           # Configuración de despliegue
```

## Diseño Visual

### Paleta de Colores Celestes

```css
:root {
  /* Colores principales */
  --primary-blue: #0088cc;        /* Azul principal */
  --primary-light: #33a3d9;      /* Azul claro */
  --primary-dark: #006699;       /* Azul oscuro */
  
  /* Colores secundarios */
  --secondary-blue: #e6f3ff;     /* Azul muy claro para fondos */
  --accent-blue: #0066cc;        /* Azul de acento */
  --text-blue: #003d66;          /* Azul para texto */
  
  /* Colores neutros */
  --white: #ffffff;
  --light-gray: #f8f9fa;
  --gray: #6c757d;
  --dark-gray: #343a40;
  
  /* Estados */
  --success: #28a745;
  --warning: #ffc107;
  --error: #dc3545;
  --info: #17a2b8;
}
```

### Tipografía

```css
/* Fuentes del sistema para mejor rendimiento */
--font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
               'Helvetica Neue', Arial, sans-serif;
--font-size-xs: 0.75rem;    /* 12px */
--font-size-sm: 0.875rem;   /* 14px */
--font-size-base: 1rem;     /* 16px */
--font-size-lg: 1.125rem;   /* 18px */
--font-size-xl: 1.25rem;    /* 20px */
--font-size-2xl: 1.5rem;    /* 24px */
--font-size-3xl: 1.875rem;  /* 30px */
```

## Componentes de UI

### 1. Header Component

```html
<header class="app-header">
  <div class="header-content">
    <div class="logo-section">
      <img src="assets/icons/boletin-logo.svg" alt="Boletín Oficial" class="logo">
      <h1 class="app-title">Boletín Oficial Argentina</h1>
    </div>
    <div class="header-subtitle">
      <p>Análisis Inteligente de 1ra Sección-Legislación y Avisos Oficiales</p>
    </div>
  </div>
</header>
```

```css
.app-header {
  background: linear-gradient(135deg, var(--primary-blue), var(--primary-light));
  color: var(--white);
  padding: 1rem;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 136, 204, 0.2);
}

.logo-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.logo {
  width: 32px;
  height: 32px;
}

.app-title {
  font-size: var(--font-size-xl);
  font-weight: 600;
  margin: 0;
}

.header-subtitle p {
  font-size: var(--font-size-sm);
  opacity: 0.9;
  margin: 0;
}
```

### 2. Date Selector Component

```html
<section class="date-selector">
  <div class="selector-header">
    <h2>Seleccionar Fecha</h2>
    <p>Elige la fecha del boletín que deseas analizar</p>
  </div>
  
  <div class="date-input-container">
    <label for="date-picker" class="date-label">
      <svg class="calendar-icon" viewBox="0 0 24 24">
        <path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z"/>
      </svg>
      Fecha del Boletín
    </label>
    <input 
      type="date" 
      id="date-picker" 
      class="date-input"
      max="" 
      value=""
    >
  </div>
  
  <button id="analyze-btn" class="analyze-button" disabled>
    <span class="button-text">Analizar Boletín</span>
    <svg class="button-icon" viewBox="0 0 24 24">
      <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
    </svg>
  </button>
</section>
```

```css
.date-selector {
  background: var(--white);
  border-radius: 12px;
  padding: 1.5rem;
  margin: 1rem;
  box-shadow: 0 2px 12px rgba(0, 136, 204, 0.1);
  border: 1px solid var(--secondary-blue);
}

.selector-header h2 {
  color: var(--text-blue);
  font-size: var(--font-size-lg);
  margin: 0 0 0.5rem 0;
}

.selector-header p {
  color: var(--gray);
  font-size: var(--font-size-sm);
  margin: 0 0 1.5rem 0;
}

.date-input-container {
  margin-bottom: 1.5rem;
}

.date-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-blue);
  font-weight: 500;
  margin-bottom: 0.75rem;
  font-size: var(--font-size-sm);
}

.calendar-icon {
  width: 18px;
  height: 18px;
  fill: var(--primary-blue);
}

.date-input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid var(--secondary-blue);
  border-radius: 8px;
  font-size: var(--font-size-base);
  transition: border-color 0.2s ease;
}

.date-input:focus {
  outline: none;
  border-color: var(--primary-blue);
  box-shadow: 0 0 0 3px rgba(0, 136, 204, 0.1);
}

.analyze-button {
  width: 100%;
  background: linear-gradient(135deg, var(--primary-blue), var(--primary-light));
  color: var(--white);
  border: none;
  border-radius: 8px;
  padding: 1rem;
  font-size: var(--font-size-base);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.analyze-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 136, 204, 0.3);
}

.analyze-button:disabled {
  background: var(--gray);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.button-icon {
  width: 20px;
  height: 20px;
  fill: currentColor;
}
```

### 3. Loading Component

```html
<div id="loading-overlay" class="loading-overlay hidden">
  <div class="loading-content">
    <div class="loading-spinner">
      <div class="spinner-ring"></div>
      <div class="spinner-ring"></div>
      <div class="spinner-ring"></div>
    </div>
    <h3 class="loading-title">Analizando Boletín</h3>
    <p class="loading-message">Procesando normativa con IA...</p>
    <div class="loading-progress">
      <div class="progress-bar">
        <div class="progress-fill"></div>
      </div>
      <span class="progress-text">Estimado: 30-60 segundos</span>
    </div>
  </div>
</div>
```

```css
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-content {
  text-align: center;
  padding: 2rem;
  max-width: 300px;
}

.loading-spinner {
  position: relative;
  width: 60px;
  height: 60px;
  margin: 0 auto 1.5rem;
}

.spinner-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border: 3px solid transparent;
  border-top: 3px solid var(--primary-blue);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.spinner-ring:nth-child(2) {
  animation-delay: -0.3s;
  border-top-color: var(--primary-light);
}

.spinner-ring:nth-child(3) {
  animation-delay: -0.6s;
  border-top-color: var(--accent-blue);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-title {
  color: var(--text-blue);
  font-size: var(--font-size-lg);
  margin: 0 0 0.5rem 0;
}

.loading-message {
  color: var(--gray);
  font-size: var(--font-size-sm);
  margin: 0 0 1.5rem 0;
}

.progress-bar {
  width: 100%;
  height: 4px;
  background: var(--secondary-blue);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary-blue), var(--primary-light));
  border-radius: 2px;
  animation: progress 2s ease-in-out infinite;
}

@keyframes progress {
  0% { width: 0%; }
  50% { width: 70%; }
  100% { width: 100%; }
}

.progress-text {
  font-size: var(--font-size-xs);
  color: var(--gray);
}
```

### 4. Results Component

```html
<section id="results-section" class="results-section hidden">
  <div class="results-header">
    <h2>Análisis del Boletín</h2>
    <div class="results-meta">
      <span class="date-badge" id="results-date"></span>
      <span class="cache-badge" id="cache-status"></span>
    </div>
  </div>

  <!-- Resumen Ejecutivo -->
  <div class="analysis-card">
    <div class="card-header">
      <h3>
        <svg class="card-icon" viewBox="0 0 24 24">
          <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
        </svg>
        Resumen Ejecutivo
      </h3>
    </div>
    <div class="card-content">
      <p id="analysis-summary"></p>
    </div>
  </div>

  <!-- Cambios Principales -->
  <div class="analysis-card">
    <div class="card-header">
      <h3>
        <svg class="card-icon" viewBox="0 0 24 24">
          <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M11,16.5L6.5,12L7.91,10.59L11,13.67L16.59,8.09L18,9.5L11,16.5Z"/>
        </svg>
        Cambios Principales
      </h3>
    </div>
    <div class="card-content">
      <div id="main-changes" class="changes-list"></div>
    </div>
  </div>

  <!-- Áreas Afectadas -->
  <div class="analysis-card">
    <div class="card-header">
      <h3>
        <svg class="card-icon" viewBox="0 0 24 24">
          <path d="M12,2L13.09,8.26L22,9L13.09,9.74L12,16L10.91,9.74L2,9L10.91,8.26L12,2Z"/>
        </svg>
        Áreas Afectadas
      </h3>
    </div>
    <div class="card-content">
      <div id="affected-areas" class="areas-tags"></div>
    </div>
  </div>

  <!-- Impacto Estimado -->
  <div class="analysis-card">
    <div class="card-header">
      <h3>
        <svg class="card-icon" viewBox="0 0 24 24">
          <path d="M13,9H11V7H13M13,17H11V11H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z"/>
        </svg>
        Impacto Estimado
      </h3>
    </div>
    <div class="card-content">
      <p id="estimated-impact"></p>
    </div>
  </div>

  <!-- Opiniones de Expertos -->
  <div class="analysis-card" id="expert-opinions-card">
    <div class="card-header">
      <h3>
        <svg class="card-icon" viewBox="0 0 24 24">
          <path d="M12,2A3,3 0 0,1 15,5V11A3,3 0 0,1 12,14A3,3 0 0,1 9,11V5A3,3 0 0,1 12,2M19,11C19,14.53 16.39,17.44 13,17.93V21H11V17.93C7.61,17.44 5,14.53 5,11H7A5,5 0 0,0 12,16A5,5 0 0,0 17,11H19Z"/>
        </svg>
        Opiniones de Expertos
      </h3>
    </div>
    <div class="card-content">
      <div id="expert-opinions" class="opinions-list"></div>
    </div>
  </div>

  <!-- Acciones -->
  <div class="results-actions">
    <button id="share-btn" class="action-button secondary">
      <svg class="button-icon" viewBox="0 0 24 24">
        <path d="M18,16.08C17.24,16.08 16.56,16.38 16.04,16.85L8.91,12.7C8.96,12.47 9,12.24 9,12C9,11.76 8.96,11.53 8.91,11.3L15.96,7.19C16.5,7.69 17.21,8 18,8A3,3 0 0,0 21,5A3,3 0 0,0 18,2A3,3 0 0,0 15,5C15,5.24 15.04,5.47 15.09,5.7L8.04,9.81C7.5,9.31 6.79,9 6,9A3,3 0 0,0 3,12A3,3 0 0,0 6,15C6.79,15 7.5,14.69 8.04,14.19L15.16,18.34C15.11,18.55 15.08,18.77 15.08,19C15.08,20.61 16.39,21.91 18,21.91C19.61,21.91 20.92,20.61 20.92,19A2.92,2.92 0 0,0 18,16.08Z"/>
      </svg>
      Compartir
    </button>
    <button id="new-analysis-btn" class="action-button primary">
      <svg class="button-icon" viewBox="0 0 24 24">
        <path d="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z"/>
      </svg>
      Nuevo Análisis
    </button>
  </div>
</section>
```

```css
.results-section {
  padding: 1rem;
}

.results-header {
  margin-bottom: 1.5rem;
}

.results-header h2 {
  color: var(--text-blue);
  font-size: var(--font-size-2xl);
  margin: 0 0 0.75rem 0;
}

.results-meta {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.date-badge, .cache-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: var(--font-size-xs);
  font-weight: 500;
}

.date-badge {
  background: var(--secondary-blue);
  color: var(--text-blue);
}

.cache-badge {
  background: var(--success);
  color: var(--white);
}

.analysis-card {
  background: var(--white);
  border-radius: 12px;
  margin-bottom: 1rem;
  box-shadow: 0 2px 8px rgba(0, 136, 204, 0.1);
  border: 1px solid var(--secondary-blue);
  overflow: hidden;
}

.card-header {
  background: linear-gradient(135deg, var(--secondary-blue), rgba(51, 163, 217, 0.1));
  padding: 1rem;
  border-bottom: 1px solid var(--secondary-blue);
}

.card-header h3 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-blue);
  font-size: var(--font-size-lg);
  margin: 0;
}

.card-icon {
  width: 20px;
  height: 20px;
  fill: var(--primary-blue);
}

.card-content {
  padding: 1.5rem;
}

.changes-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.change-item {
  padding: 1rem;
  background: var(--light-gray);
  border-radius: 8px;
  border-left: 4px solid var(--primary-blue);
}

.change-header {
  display: flex;
  justify-content: between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.change-title {
  font-weight: 600;
  color: var(--text-blue);
  font-size: var(--font-size-base);
}

.impact-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: var(--font-size-xs);
  font-weight: 500;
}

.impact-alto { background: var(--error); color: var(--white); }
.impact-medio { background: var(--warning); color: var(--dark-gray); }
.impact-bajo { background: var(--success); color: var(--white); }

.areas-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.area-tag {
  padding: 0.5rem 1rem;
  background: var(--primary-blue);
  color: var(--white);
  border-radius: 20px;
  font-size: var(--font-size-sm);
  font-weight: 500;
}

.opinions-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.opinion-item {
  padding: 1rem;
  background: var(--light-gray);
  border-radius: 8px;
  border-left: 4px solid var(--accent-blue);
}

.opinion-source {
  font-weight: 600;
  color: var(--text-blue);
  margin-bottom: 0.5rem;
}

.opinion-text {
  color: var(--dark-gray);
  line-height: 1.5;
  margin-bottom: 0.5rem;
}

.opinion-date {
  font-size: var(--font-size-xs);
  color: var(--gray);
}

.results-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--secondary-blue);
}

.action-button {
  flex: 1;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: var(--font-size-base);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border: none;
}

.action-button.primary {
  background: linear-gradient(135deg, var(--primary-blue), var(--primary-light));
  color: var(--white);
}

.action-button.secondary {
  background: var(--white);
  color: var(--primary-blue);
  border: 2px solid var(--primary-blue);
}

.action-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 136, 204, 0.2);
}
```

### 5. Error Component

```html
<div id="error-modal" class="error-modal hidden">
  <div class="error-content">
    <div class="error-icon">
      <svg viewBox="0 0 24 24">
        <path d="M13,13H11V7H13M13,17H11V15H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z"/>
      </svg>
    </div>
    <h3 id="error-title">Error</h3>
    <p id="error-message">Ha ocurrido un error inesperado</p>
    <div class="error-actions">
      <button id="retry-btn" class="error-button primary">Reintentar</button>
      <button id="close-error-btn" class="error-button secondary">Cerrar</button>
    </div>
  </div>
</div>
```

```css
.error-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
  padding: 1rem;
}

.error-content {
  background: var(--white);
  border-radius: 12px;
  padding: 2rem;
  max-width: 400px;
  width: 100%;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.error-icon {
  width: 60px;
  height: 60px;
  margin: 0 auto 1rem;
  background: var(--error);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-icon svg {
  width: 30px;
  height: 30px;
  fill: var(--white);
}

.error-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.error-button {
  flex: 1;
  padding: 0.75rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;
}

.error-button.primary {
  background: var(--primary-blue);
  color: var(--white);
}

.error-button.secondary {
  background: var(--light-gray);
  color: var(--dark-gray);
}
```

## Lógica de Aplicación

### app.js - Controlador Principal

```javascript
class BoletinApp {
  constructor() {
    this.api = new APIClient();
    this.telegram = new TelegramIntegration();
    this.currentAnalysis = null;
    
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.setupDatePicker();
    this.telegram.init();
  }

  setupEventListeners() {
    const analyzeBtn = document.getElementById('analyze-btn');
    const datePicker = document.getElementById('date-picker');
    const shareBtn = document.getElementById('share-btn');
    const newAnalysisBtn = document.getElementById('new-analysis-btn');

    analyzeBtn.addEventListener('click', () => this.handleAnalyze());
    datePicker.addEventListener('change', () => this.handleDateChange());
    shareBtn.addEventListener('click', () => this.handleShare());
    newAnalysisBtn.addEventListener('click', () => this.handleNewAnalysis());
  }

  setupDatePicker() {
    const datePicker = document.getElementById('date-picker');
    const today = new Date().toISOString().split('T')[0];
    
    datePicker.max = today;
    datePicker.value = today;
    
    this.handleDateChange();
  }

  handleDateChange() {
    const datePicker = document.getElementById('date-picker');
    const analyzeBtn = document.getElementById('analyze-btn');
    
    analyzeBtn.disabled = !datePicker.value;
  }

  async handleAnalyze() {
    const date = document.getElementById('date-picker').value;
    
    if (!date) return;

    try {
      this.showLoading();
      
      const analysis = await this.api.analyzeDate(date);
      
      this.currentAnalysis = analysis;
      this.displayResults(analysis);
      
    } catch (error) {
      this.showError(error);
    } finally {
      this.hideLoading();
    }
  }

  displayResults(analysis) {
    const resultsSection = document.getElementById('results-section');
    
    // Mostrar fecha
    document.getElementById('results-date').textContent = 
      this.formatDate(analysis.fecha);
    
    // Mostrar estado de cache
    const cacheStatus = document.getElementById('cache-status');
    cacheStatus.textContent = analysis.metadatos.desde_cache ? 
      'Desde caché' : 'Análisis nuevo';
    
    // Mostrar resumen
    document.getElementById('analysis-summary').textContent = 
      analysis.analisis.resumen;
    
    // Mostrar cambios principales
    this.displayMainChanges(analysis.analisis.cambios_principales);
    
    // Mostrar áreas afectadas
    this.displayAffectedAreas(analysis.analisis.areas_afectadas);
    
    // Mostrar impacto
    document.getElementById('estimated-impact').textContent = 
      analysis.analisis.impacto_estimado;
    
    // Mostrar opiniones de expertos
    this.displayExpertOpinions(analysis.opiniones_expertos);
    
    // Mostrar sección de resultados
    resultsSection.classList.remove('hidden');
    
    // Scroll suave a resultados
    resultsSection.scrollIntoView({ behavior: 'smooth' });
  }

  displayMainChanges(changes) {
    const container = document.getElementById('main-changes');
    container.innerHTML = '';
    
    changes.forEach(change => {
      const changeElement = document.createElement('div');
      changeElement.className = 'change-item';
      
      changeElement.innerHTML = `
        <div class="change-header">
          <div class="change-title">${change.titulo}</div>
          <span class="impact-badge impact-${change.impacto}">${change.impacto.toUpperCase()}</span>
        </div>
        <div class="change-description">${change.descripcion}</div>
        <div class="change-meta">
          <span class="change-type">${change.tipo.toUpperCase()}</span>
          <span class="change-number">${change.numero}</span>
        </div>
      `;
      
      container.appendChild(changeElement);
    });
  }

  displayAffectedAreas(areas) {
    const container = document.getElementById('affected-areas');
    container.innerHTML = '';
    
    areas.forEach(area => {
      const areaElement = document.createElement('span');
      areaElement.className = 'area-tag';
      areaElement.textContent = area.charAt(0).toUpperCase() + area.slice(1);
      container.appendChild(areaElement);
    });
  }

  displayExpertOpinions(opinions) {
    const container = document.getElementById('expert-opinions');
    const card = document.getElementById('expert-opinions-card');
    
    if (!opinions || opinions.length === 0) {
      card.style.display = 'none';
      return;
    }
    
    card.style.display = 'block';
    container.innerHTML = '';
    
    opinions.forEach(opinion => {
      const opinionElement = document.createElement('div');
      opinionElement.className = 'opinion-item';
      
      opinionElement.innerHTML = `
        <div class="opinion-source">${opinion.fuente}</div>
        <div class="opinion-text">${opinion.opinion}</div>
        <div class="opinion-date">${this.formatDate(opinion.fecha_opinion)}</div>
      `;
      
      container.appendChild(opinionElement);
    });
  }

  handleShare() {
    if (!this.currentAnalysis) return;
    
    const shareData = {
      title: 'Análisis del Boletín Oficial',
      text: `Análisis del ${this.formatDate(this.currentAnalysis.fecha)}: ${this.currentAnalysis.analisis.resumen.substring(0, 100)}...`,
      url: window.location.href
    };
    
    this.telegram.shareData(shareData);
  }

  handleNewAnalysis() {
    // Ocultar resultados
    document.getElementById('results-section').classList.add('hidden');
    
    // Limpiar análisis actual
    this.currentAnalysis = null;
    
    // Scroll al selector de fecha
    document.querySelector('.date-selector').scrollIntoView({ 
      behavior: 'smooth' 
    });
  }

  showLoading() {
    document.getElementById('loading-overlay').classList.remove('hidden');
  }

  hideLoading() {
    document.getElementById('loading-overlay').classList.add('hidden');
  }

  showError(error) {
    const modal = document.getElementById('error-modal');
    const title = document.getElementById('error-title');
    const message = document.getElementById('error-message');
    
    title.textContent = error.title || 'Error';
    message.textContent = error.message || 'Ha ocurrido un error inesperado';
    
    modal.classList.remove('hidden');
  }

  formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-AR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
}

// Inicializar aplicación
document.addEventListener('DOMContentLoaded', () => {
  new BoletinApp();
});
```

### api.js - Cliente API

```javascript
class APIClient {
  constructor() {
    this.baseURL = 'https://your-api-gateway-url.amazonaws.com/prod';
    this.timeout = 60000; // 60 segundos
  }

  async analyzeDate(date) {
    const response = await this.makeRequest('/analyze', {
      method: 'POST',
      body: JSON.stringify({
        fecha: date,
        forzar_reanalisis: false
      })
    });

    if (!response.success) {
      throw new Error(response.message || 'Error en el análisis');
    }

    return response.data;
  }

  async makeRequest(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const defaultOptions = {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: this.timeout
    };

    const finalOptions = { ...defaultOptions, ...options };

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), finalOptions.timeout);

      const response = await fetch(url, {
        ...finalOptions,
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();

    } catch (error) {
      if (error.name === 'AbortError') {
        throw new Error('La solicitud ha tardado demasiado tiempo');
      }
      
      throw new Error(`Error de conexión: ${error.message}`);
    }
  }
}
```

### telegram.js - Integración Telegram

```javascript
class TelegramIntegration {
  constructor() {
    this.tg = window.Telegram?.WebApp;
    this.isReady = false;
  }

  init() {
    if (!this.tg) {
      console.warn('Telegram WebApp no disponible');
      return;
    }

    // Configurar tema
    this.setupTheme();
    
    // Configurar botones
    this.setupMainButton();
    
    // Expandir aplicación
    this.tg.expand();
    
    // Marcar como listo
    this.tg.ready();
    this.isReady = true;
  }

  setupTheme() {
    if (!this.tg) return;

    const themeParams = this.tg.themeParams;
    
    // Aplicar colores del tema de Telegram si están disponibles
    if (themeParams.bg_color) {
      document.documentElement.style.setProperty('--telegram-bg', themeParams.bg_color);
    }
    
    if (themeParams.text_color) {
      document.documentElement.style.setProperty('--telegram-text', themeParams.text_color);
    }
  }

  setupMainButton() {
    if (!this.tg) return;

    // Configurar botón principal de Telegram
    this.tg.MainButton.setText('Analizar Boletín');
    this.tg.MainButton.color = '#0088cc';
    
    this.tg.MainButton.onClick(() => {
      const analyzeBtn = document.getElementById('analyze-btn');
      if (!analyzeBtn.disabled) {
        analyzeBtn.click();
      }
    });
  }

  showMainButton() {
    if (this.tg?.MainButton) {
      this.tg.MainButton.show();
    }
  }

  hideMainButton() {
    if (this.tg?.MainButton) {
      this.tg.MainButton.hide();
    }
  }

  shareData(data) {
    if (!this.tg) {
      // Fallback para navegadores normales
      if (navigator.share) {
        navigator.share(data);
      } else {
        // Copiar al portapapeles
        navigator.clipboard.writeText(`${data.title}\n${data.text}\n${data.url}`);
        this.showAlert('Información copiada al portapapeles');
      }
      return;
    }

    // Usar API de Telegram para compartir
    this.tg.switchInlineQuery(data.text, ['users', 'groups']);
  }

  showAlert(message) {
    if (this.tg) {
      this.tg.showAlert(message);
    } else {
      alert(message);
    }
  }

  hapticFeedback(type = 'impact') {
    if (this.tg?.HapticFeedback) {
      this.tg.HapticFeedback.impactOccurred(type);
    }
  }
}
```

## Responsive Design

### responsive.css

```css
/* Mobile First - Base styles ya están optimizados para móvil */

/* Tablet */
@media (min-width: 768px) {
  .app-header {
    padding: 2rem 1rem;
  }
  
  .date-selector {
    margin: 2rem auto;
    max-width: 500px;
  }
  
  .results-section {
    padding: 2rem;
    max-width: 800px;
    margin: 0 auto;
  }
  
  .results-actions {
    max-width: 400px;
    margin: 2rem auto 0;
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .app-header {
    padding: 3rem 2rem;
  }
  
  .date-selector {
    max-width: 600px;
  }
  
  .results-section {
    max-width: 900px;
  }
  
  .analysis-card {
    margin-bottom: 1.5rem;
  }
  
  .card-content {
    padding: 2rem;
  }
}

/* Landscape móvil */
@media (max-height: 500px) and (orientation: landscape) {
  .app-header {
    padding: 1rem;
  }
  
  .loading-overlay .loading-content {
    padding: 1rem;
  }
}
```

## Configuración de Despliegue

### vercel.json

```json
{
  "version": 2,
  "builds": [
    {
      "src": "index.html",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Frame-Options",
          "value": "ALLOWALL"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        }
      ]
    }
  ]
}
```

### package.json (opcional para dependencias de desarrollo)

```json
{
  "name": "boletin-oficial-telegram-app",
  "version": "1.0.0",
  "description": "Telegram Mini App para análisis del Boletín Oficial",
  "scripts": {
    "dev": "python -m http.server 3000",
    "build": "echo 'No build step required for vanilla JS'",
    "deploy": "vercel --prod"
  },
  "devDependencies": {
    "vercel": "^32.0.0"
  }
}
```

## Optimizaciones de Performance

### Lazy Loading de Componentes

```javascript
// Cargar componentes solo cuando se necesiten
const loadComponent = async (componentName) => {
  const module = await import(`./components/${componentName}.js`);
  return module.default;
};
```

### Service Worker para Cache

```javascript
// sw.js
const CACHE_NAME = 'boletin-oficial-v1';
const urlsToCache = [
  '/',
  '/css/styles.css',
  '/js/app.js',
  '/js/api.js',
  '/js/telegram.js'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        return response || fetch(event.request);
      })
  );
});
```

## Testing

### Pruebas de Integración con Telegram

```javascript
// test-telegram.js
class TelegramTester {
  static testWebAppAPI() {
    if (window.Telegram?.WebApp) {
      console.log('✅ Telegram WebApp API disponible');
      console.log('Theme:', window.Telegram.WebApp.themeParams);
      console.log('User:', window.Telegram.WebApp.initDataUnsafe.user);
    } else {
      console.log('❌ Telegram WebApp API no disponible');
    }
  }
  
  static testMainButton() {
    const tg = window.Telegram?.WebApp;
    if (tg?.MainButton) {
      tg.MainButton.setText('Test Button');
      tg.MainButton.show();
      console.log('✅ Main Button funcional');
    }
  }
}
```

Este diseño frontend proporciona una experiencia de usuario completa y optimizada para Telegram Mini Apps, manteniendo el estilo visual del Boletín Oficial pero con una paleta de colores celestes moderna y atractiva.