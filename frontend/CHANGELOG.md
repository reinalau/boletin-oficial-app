# Changelog - Frontend Boletín Oficial

## [2.0.0] - 2025-01-XX

### 🎉 Nuevas Características

#### Separación en Dos Botones
- **Botón "Analizar Boletín"**: Realiza únicamente el análisis del contenido normativo
- **Botón "Analizar Opiniones de Expertos"**: Obtiene opiniones de expertos sobre el análisis existente

#### Mejoras en la Experiencia de Usuario
- **Flujo más rápido**: El análisis principal se completa en ~30-60 segundos
- **Control granular**: El usuario decide si necesita opiniones de expertos
- **Feedback visual mejorado**: Diferentes mensajes de carga para cada tipo de análisis
- **Estado de botones inteligente**: El botón de expertos se habilita solo después del análisis del boletín

### 🔧 Cambios Técnicos

#### API Client (`js/api.js`)
- Nuevo método `analyzeBoletin()` para análisis del boletín solamente
- Nuevo método `getExpertOpinions()` para obtener opiniones de expertos
- Mantenimiento de `analyzeDate()` para compatibilidad hacia atrás

#### Aplicación Principal (`js/app.js`)
- Nuevo método `handleAnalyzeBoletin()` para manejar análisis del boletín
- Nuevo método `handleAnalyzeExperts()` para manejar opiniones de expertos
- Nuevo método `displayBoletinResults()` para mostrar solo resultados del boletín
- Mejoras en `showLoading()` con mensajes personalizables
- Sistema de rastreo de última acción para reintentos inteligentes

#### Interfaz de Usuario (`index.html`)
- Reemplazo del botón único por contenedor `.analyze-buttons`
- Dos botones separados con iconos distintivos
- Estructura HTML optimizada para el nuevo flujo

#### Estilos (`css/styles.css`)
- Nuevos estilos para `.analyze-buttons` container
- Estilos diferenciados para botones primario y secundario
- Mejoras en responsive design para los nuevos botones

### 🔄 Flujo de Trabajo

#### Flujo Anterior (v1.x)
1. Usuario selecciona fecha
2. Hace clic en "Analizar Boletín"
3. Espera 60-120 segundos
4. Recibe análisis completo con opiniones

#### Nuevo Flujo (v2.0)
1. Usuario selecciona fecha
2. Hace clic en "Analizar Boletín" (~30-60s)
3. Recibe análisis del boletín
4. **Opcionalmente** hace clic en "Analizar Opiniones de Expertos" (~20-40s)
5. Recibe opiniones de expertos

### 🐛 Correcciones

- Mejor manejo de errores específicos por tipo de análisis
- Prevención de múltiples solicitudes simultáneas
- Mejora en el manejo de timeouts
- Corrección en el estado de botones después de errores

### 📱 Compatibilidad

- **Telegram Mini Apps**: Totalmente compatible
- **Navegadores**: Mantiene compatibilidad con todos los navegadores soportados
- **API**: Mantiene compatibilidad hacia atrás con el endpoint original

### 🔧 Configuración

No se requieren cambios de configuración. La aplicación detecta automáticamente si el backend soporta los nuevos endpoints.

### 📊 Métricas de Rendimiento

- **Tiempo de análisis del boletín**: Reducido de 60-120s a 30-60s
- **Tiempo total (con opiniones)**: Similar al anterior (80-100s)
- **Tiempo solo boletín**: 50% más rápido
- **Tasa de éxito**: Mejorada debido a timeouts más cortos

### 🚀 Migración

#### Para Usuarios
- No se requiere acción. La interfaz se actualiza automáticamente.
- El flujo anterior sigue funcionando con el endpoint legacy.

#### Para Desarrolladores
```javascript
// Nuevo flujo recomendado
const boletinAnalysis = await apiClient.analyzeBoletin(date, forceReanalysis);
const expertOpinions = await apiClient.getExpertOpinions(date);

// Flujo anterior (aún soportado)
const fullAnalysis = await apiClient.analyzeDate(date, forceReanalysis);
```

### 📝 Notas de Desarrollo

- Los nuevos endpoints utilizan el parámetro `action` para determinar el tipo de análisis
- El estado de la aplicación se mantiene entre las dos operaciones
- El sistema de cache funciona independientemente para cada tipo de análisis
- Los errores se manejan de forma específica para cada operación

### 🔮 Próximas Características

- [ ] Análisis incremental de opiniones
- [ ] Filtros por tipo de medio
- [ ] Exportación de resultados por separado
- [ ] Notificaciones push para nuevas opiniones