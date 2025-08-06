# Boletín Oficial - Telegram Mini App Frontend

Frontend de la aplicación Telegram Mini App para análisis inteligente del Boletín Oficial de Argentina.

## 🚀 Características

- **Diseño Responsive**: Optimizado para móviles y tablets
- **Integración Telegram**: SDK nativo para funcionalidades específicas
- **Colores Celestes**: Paleta inspirada en el sitio oficial pero modernizada
- **Performance**: Vanilla JS para carga rápida
- **Accesibilidad**: Cumple con estándares WCAG
- **PWA Ready**: Service Worker para cache offline

## 🎨 Diseño Visual

### Paleta de Colores
- **Azul Principal**: `#0088cc`
- **Azul Claro**: `#33a3d9`
- **Azul Oscuro**: `#006699`
- **Azul Secundario**: `#e6f3ff`
- **Azul de Texto**: `#003d66`

### Componentes
- Header con gradiente celeste
- Selector de fecha interactivo
- Cards de análisis con iconos SVG
- Loading spinner animado
- Modal de errores elegante
- Botones con efectos hover

## 📱 Funcionalidades

### Principales
- ✅ Selección de fecha con validación
- ✅ Análisis automático del boletín
- ✅ Visualización de resultados estructurados
- ✅ Compartir via Telegram
- ✅ Manejo de errores robusto

### Telegram Integration
- ✅ Main Button nativo
- ✅ Back Button
- ✅ Haptic Feedback
- ✅ Theme adaptation
- ✅ Share functionality
- ✅ User information

## 🛠️ Tecnologías

- **HTML5**: Estructura semántica
- **CSS3**: Grid, Flexbox, Custom Properties
- **JavaScript ES6+**: Vanilla JS, Clases, Async/Await
- **Telegram WebApp SDK**: Integración nativa
- **Vercel**: Hosting y despliegue

## 📁 Estructura de Archivos

```
frontend/
├── index.html              # Página principal
├── css/
│   ├── styles.css         # Estilos principales
│   └── responsive.css     # Media queries
├── js/
│   ├── app.js            # Lógica principal
│   ├── api.js            # Cliente API
│   ├── telegram.js       # Integración Telegram
│   └── utils.js          # Utilidades
├── vercel.json           # Configuración Vercel
└── README.md             # Este archivo
```

## 🚀 Instalación y Desarrollo

### Desarrollo Local

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd frontend
```

2. **Servir archivos localmente**
```bash
# Opción 1: Python
python -m http.server 3000

# Opción 2: Node.js
npx serve . -p 3000

# Opción 3: PHP
php -S localhost:3000
```

3. **Abrir en navegador**
```
http://localhost:3000
```

### Testing con Datos Demo

Para ver la interfaz con datos de ejemplo:
```
http://localhost:3000?demo=true
```

### Desarrollo en Telegram

1. **Crear Bot en Telegram**
   - Hablar con @BotFather
   - Crear nuevo bot: `/newbot`
   - Obtener token del bot

2. **Configurar Mini App**
   - Usar `/newapp` con @BotFather
   - Configurar URL de desarrollo
   - Habilitar inline mode si es necesario

3. **Testing en Telegram**
   - Usar ngrok para exponer localhost
   - Configurar URL en BotFather
   - Probar en Telegram Web/Desktop/Mobile

## 🌐 Despliegue en Vercel

### Automático (Recomendado)

1. **Conectar repositorio**
   - Ir a [vercel.com](https://vercel.com)
   - Importar proyecto desde Git
   - Seleccionar carpeta `frontend`

2. **Configurar variables**
   - No se requieren variables de entorno
   - La configuración está en `vercel.json`

3. **Desplegar**
   - Vercel despliega automáticamente
   - URL disponible inmediatamente

### Manual

```bash
# Instalar Vercel CLI
npm i -g vercel

# Desplegar
vercel --prod
```

## 🔧 Configuración

### API Backend

Editar en `js/api.js`:
```javascript
// Cambiar URL base de la API
this.baseURL = 'https://tu-api-gateway.amazonaws.com/prod';
```

### Telegram Bot

Configurar en @BotFather:
```
/setmenubutton
@tu_bot
Analizar Boletín - https://tu-app.vercel.app
```

## 📱 Componentes Principales

### 1. BoletinApp (app.js)
Controlador principal de la aplicación
- Maneja el flujo de análisis
- Coordina componentes
- Gestiona estado global

### 2. APIClient (api.js)
Cliente para comunicación con backend
- Reintentos automáticos
- Manejo de errores
- Timeout configurable

### 3. TelegramIntegration (telegram.js)
Integración con Telegram WebApp SDK
- Botones nativos
- Feedback háptico
- Adaptación de tema
- Funciones de compartir

### 4. Utils (utils.js)
Utilidades generales
- Formateo de fechas
- Validaciones
- Manejo de errores
- Funciones helper

## 🎯 Funcionalidades Detalladas

### Selector de Fecha
- Calendario nativo HTML5
- Validación de fechas futuras
- Fecha máxima = hoy
- Feedback visual de validación

### Análisis de Resultados
- **Resumen Ejecutivo**: Texto principal del análisis
- **Cambios Principales**: Lista de modificaciones normativas
- **Áreas Afectadas**: Tags de sectores impactados
- **Impacto Estimado**: Evaluación del impacto general
- **Opiniones de Expertos**: Perspectivas adicionales

### Estados de Carga
- Spinner animado con anillos
- Barra de progreso estimado
- Mensaje informativo
- Tiempo estimado de procesamiento

### Manejo de Errores
- Modal elegante con iconos
- Mensajes específicos por tipo de error
- Botones de reintento y cierre
- Logging para debugging

## 🔍 Testing y Debugging

### Datos de Demostración
```javascript
// En app.js - loadDemoAnalysis()
// Simula respuesta completa de la API
```

### Console Logging
```javascript
// Habilitar logs detallados
localStorage.setItem('debug', 'true');
```

### Telegram Testing
```javascript
// Información del entorno
console.log(window.telegramApp.getEnvironmentInfo());
```

## 📊 Performance

### Optimizaciones Implementadas
- **CSS**: Custom Properties para theming
- **JS**: Vanilla JS sin frameworks pesados
- **Images**: SVG icons para escalabilidad
- **Caching**: Service Worker ready
- **Lazy Loading**: Componentes bajo demanda

### Métricas Objetivo
- **First Contentful Paint**: < 1.5s
- **Largest Contentful Paint**: < 2.5s
- **Time to Interactive**: < 3s
- **Bundle Size**: < 100KB

## 🌐 Compatibilidad

### Navegadores Soportados
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

### Telegram Clients
- Telegram Web
- Telegram Desktop
- Telegram Mobile (iOS/Android)

### Dispositivos
- Mobile: 320px - 768px
- Tablet: 768px - 1024px
- Desktop: 1024px+

## 🔒 Seguridad

### Medidas Implementadas
- **XSS Protection**: Sanitización de HTML
- **CSRF**: Headers de seguridad
- **Content Security**: Vercel headers
- **Input Validation**: Validación client-side

### Headers de Seguridad
```json
{
  "X-Frame-Options": "ALLOWALL",
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "strict-origin-when-cross-origin"
}
```

## 🐛 Troubleshooting

### Problemas Comunes

1. **Telegram SDK no carga**
   - Verificar que esté en contexto de Telegram
   - Revisar URL configurada en BotFather

2. **API no responde**
   - Verificar URL en `api.js`
   - Revisar CORS en API Gateway
   - Comprobar logs de Lambda

3. **Estilos no se aplican**
   - Verificar cache del navegador
   - Comprobar rutas de CSS
   - Revisar media queries

### Debug Mode
```javascript
// Habilitar modo debug
window.DEBUG = true;

// Ver información de Telegram
console.log(window.telegramApp?.getEnvironmentInfo());

// Ver configuración de API
console.log(window.apiClient);
```

## 📈 Roadmap

### Próximas Funcionalidades
- [ ] Modo offline con Service Worker
- [ ] Notificaciones push
- [ ] Historial de análisis
- [ ] Filtros por área temática
- [ ] Exportar a PDF
- [ ] Modo oscuro automático

### Mejoras Técnicas
- [ ] TypeScript migration
- [ ] Unit tests con Jest
- [ ] E2E tests con Playwright
- [ ] Bundle optimization
- [ ] CDN para assets

## 🤝 Contribución

### Desarrollo
1. Fork del repositorio
2. Crear branch feature
3. Implementar cambios
4. Testing local
5. Pull request

### Estándares de Código
- ES6+ features
- Comentarios JSDoc
- Naming conventions consistentes
- Error handling robusto

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver archivo LICENSE para más detalles.

## 📞 Soporte

Para soporte técnico o consultas:
- Issues en GitHub
- Documentación en `/docs`
- Logs en browser console