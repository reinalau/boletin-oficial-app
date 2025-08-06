# Documento de Requerimientos

## Introducción

La aplicación AppBoletinOficial es una mini app de Telegram que permite a los usuarios analizar automáticamente la normativa publicada en la sección "Legislación y Avisos Oficiales" del Boletín Oficial de la República Argentina. La aplicación utiliza inteligencia artificial para proporcionar análisis detallados de los cambios normativos y opiniones de expertos, facilitando la comprensión de las nuevas regulaciones.

## Requerimientos

### Requerimiento 1: Selección de Fecha

**Historia de Usuario:** Como usuario de la mini app, quiero seleccionar una fecha específica para consultar el boletín oficial, para poder revisar la normativa publicada en esa fecha.

#### Criterios de Aceptación

1. CUANDO el usuario accede a la mini app ENTONCES el sistema DEBERÁ mostrar un calendario interactivo
2. CUANDO el usuario selecciona una fecha ENTONCES el sistema DEBERÁ validar que la fecha esté dentro del rango disponible
3. CUANDO no se selecciona ninguna fecha ENTONCES el sistema DEBERÁ usar la fecha actual por defecto
4. CUANDO se selecciona una fecha futura ENTONCES el sistema DEBERÁ mostrar un mensaje de error indicando que no hay datos disponibles

### Requerimiento 2: Análisis Automático de Normativa

**Historia de Usuario:** Como usuario interesado en legislación, quiero recibir un análisis detallado de la nueva normativa publicada, para entender los cambios introducidos respecto a la normativa anterior.

#### Criterios de Aceptación

1. CUANDO se selecciona una fecha válida ENTONCES el sistema DEBERÁ acceder a https://www.boletinoficial.gob.ar/ para esa fecha
2. CUANDO se accede a la web del boletín se hace a traves de la IA de gemini que tiene capacidades de ingresar a una web y buscar en google search si es necesario. Identificará la primera sección (1) "Legislación y Avisos Oficiales"
3. CUANDO se analiza el contenido ENTONCES el sistema DEBERÁ generar un resumen de los cambios normativos utilizando IA
5. CUANDO se completa el análisis ENTONCES el sistema DEBERÁ mostrar los cambios de manera clara y estructurada
6. SI no existe la primera sección para la fecha seleccionada ENTONCES el sistema DEBERÁ informar que no hay normativa publicada para analizar

### Requerimiento 3: Opiniones de Expertos

**Historia de Usuario:** Como profesional del derecho, quiero acceder a opiniones de expertos sobre los cambios normativos, para obtener perspectivas adicionales sobre el impacto de las nuevas regulaciones.

#### Criterios de Aceptación

1. CUANDO existe análisis de normativa ENTONCES el sistema DEBERÁ buscar opiniones de expertos relacionadas
2. CUANDO se encuentran opiniones relevantes ENTONCES el sistema DEBERÁ mostrarlas en una sección separada
3. CUANDO no hay opiniones disponibles ENTONCES el sistema DEBERÁ indicar que no se encontraron opiniones de expertos
4. CUANDO se muestran opiniones ENTONCES el sistema DEBERÁ incluir la fuente y fecha de la opinión

### Requerimiento 4: Almacenamiento y Recuperación de Análisis

**Historia de Usuario:** Como usuario frecuente, quiero que mis consultas anteriores se guarden automáticamente, para poder acceder rápidamente a análisis previos sin tener que regenerarlos.

#### Criterios de Aceptación

1. CUANDO se completa un análisis ENTONCES el sistema DEBERÁ guardarlo en la base de datos con la fecha y sección correspondiente
2. CUANDO un usuario solicita un análisis de una fecha ya procesada ENTONCES el sistema DEBERÁ recuperar el análisis existente de la base de datos (no vuelve a utilizar la IA para generar el analisis)
3. CUANDO se recupera un análisis existente ENTONCES el sistema DEBERÁ mostrarlo.
4. CUANDO se almacena un análisis ENTONCES el sistema DEBERÁ incluir metadatos como fecha de creación y versión del análisis

### Requerimiento 5: Integración con Telegram

**Historia de Usuario:** Como usuario de Telegram, quiero acceder a la funcionalidad a través de una mini app integrada, para tener una experiencia fluida dentro del ecosistema de Telegram.

#### Criterios de Aceptación

1. CUANDO el usuario accede a la mini app desde Telegram ENTONCES el sistema DEBERÁ cargar la interfaz correctamente
2. CUANDO se realizan acciones en la mini app ENTONCES el sistema DEBERÁ mantener la sesión del usuario de Telegram
3. CUANDO se completa un análisis ENTONCES el sistema DEBERÁ permitir compartir los resultados dentro de Telegram
4. CUANDO hay errores de conectividad ENTONCES el sistema DEBERÁ mostrar mensajes de error apropiados

### Requerimiento 6: Procesamiento Backend

**Historia de Usuario:** Como administrador del sistema, quiero que el backend procese eficientemente las solicitudes de análisis, para garantizar tiempos de respuesta aceptables y escalabilidad.

#### Criterios de Aceptación

1. CUANDO se recibe una solicitud de análisis ENTONCES el sistema DEBERÁ invocar a la IA para realizar dicho analisis usando AWS Lambda
2. CUANDO se invoca el LLM ENTONCES el sistema DEBERÁ usar el modelo de Google Gemini gratuito que haya en el momento para gestionar la interacción
3. CUANDO se procesa la información del Boletin, ENTONCES el sistema DEBERÁ completar el análisis en un tiempo prudencial que se pasará por parametro.
4. SI el procesamiento falla ENTONCES el sistema DEBERÁ reintentar hasta 3 veces antes de reportar error
5. CUANDO se completa el procesamiento ENTONCES el sistema DEBERÁ devolver una respuesta estructurada en formato JSON

### Requerimiento 7: Implementación Frontend

**Historia de Usuario:** Como desarrollador, quiero implementar el frontend usando tecnologías web estándar, para asegurar compatibilidad con Telegram y facilidad de despliegue en Vercel.

#### Criterios de Aceptación

1. CUANDO se desarrolla la mini app ENTONCES el sistema DEBERÁ usar HTML5, CSS3 y JavaScript vanilla o frameworks ligeros
2. CUANDO se necesita invocar el backend ENTONCES el sistema DEBERÁ realizar llamadas HTTP a la API de AWS Lambda
3. CUANDO se despliega la aplicación ENTONCES el sistema DEBERÁ ser compatible con el hosting gratuito de Vercel
4. CUANDO se integra con Telegram ENTONCES el sistema DEBERÁ cumplir con los estándares de mini apps de Telegram
5. CUANDO se realizan llamadas a la API ENTONCES el sistema DEBERÁ manejar errores de conectividad y timeouts apropiadamente