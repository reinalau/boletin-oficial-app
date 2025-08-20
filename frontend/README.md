# Frontend - Boletín Oficial Telegram App

Frontend de la aplicación Telegram Mini App para análisis del Boletín Oficial argentino.

## 🚀 Despliegue en Netlify

### 1. Configurar Variables de Entorno

En Netlify, ve a **Site settings > Environment variables** y agrega:

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `LAMBDA_FUNCTION_URL` | `https://tu-lambda-url.lambda-url.us-east-1.on.aws/` | URL de tu Lambda Function |

**Para obtener la URL de Lambda:**
```bash
cd scripts/iac
terraform output lambda_function_url
```

### 2. Configurar Build Settings

En Netlify, configura:

- **Build command**: (vacío o `echo "Static site"`)
- **Publish directory**: `frontend` o `.` (si el repo es solo frontend)
- **Functions directory**: (vacío)

### 3. Deploy

1. Conecta tu repositorio a Netlify
2. Configura las variables de entorno
3. Haz deploy

## 🔧 Desarrollo Local

### 1. Instalar dependencias (opcional)

Si usas un bundler o herramientas de desarrollo:
```bash
npm install
```

### 2. Configurar variables locales

Copia el archivo de ejemplo:
```bash
copy .env.example .env
```

Edita `.env` con tu URL real:
```env
LAMBDA_FUNCTION_URL=https://tu-lambda-url.lambda-url.us-east-1.on.aws/
```

### 3. Servir localmente

Usa cualquier servidor HTTP local:

```bash
# Python
python -m http.server 3000

# Node.js
npx serve .

# PHP
php -S localhost:3000
```

## 📁 Estructura de Archivos

```
frontend/
├── index.html              # Página principal de la Mini App
├── css/
│   ├── styles.css          # Estilos principales
│   └── responsive.css      # Estilos responsivos
├── js/
│   ├── app.js             # Lógica principal de la aplicación
│   ├── api.js             # Cliente API (configuración dinámica)
│   ├── utils.js           # Utilidades
│   └── telegram.js        # Integración con Telegram
├── test.html              # Página de pruebas
├── debug-test.html        # Página de debug
├── .env.example           # Ejemplo de variables de entorno
└── README.md              # Este archivo
```

## 🔄 Configuración Automática

### Opción 1: Script de configuración (Windows)

```bash
configure.bat
```

Este script:
1. Obtiene la URL de Lambda desde Terraform
2. Actualiza el meta tag en `index.html`
3. Crea archivo `.env` local

### Opción 2: Script de configuración (Node.js)

```bash
node configure.js
```

## 🧪 Testing

### Páginas de prueba incluidas:

1. **`test.html`**: Interfaz completa de testing
2. **`debug-test.html`**: Comparación de payloads
3. **`index.html?demo=true`**: Modo demo con datos simulados

### Probar la API:

```javascript
// En la consola del navegador
testAPI('2025-08-07', false);
```

## 🔧 Configuración de API

La aplicación detecta automáticamente la URL de Lambda desde:

1. **Variables de entorno de Netlify** (recomendado)
2. **Variable global `window.LAMBDA_FUNCTION_URL`**
3. **Meta tag en HTML** (fallback manual)
4. **URL por defecto** (desarrollo)

### Ejemplo de configuración manual:

```html
<!-- En index.html -->
<meta name="lambda-function-url" content="https://tu-url.lambda-url.us-east-1.on.aws/">
```

```javascript
// O via JavaScript
window.LAMBDA_FUNCTION_URL = 'https://tu-url.lambda-url.us-east-1.on.aws/';
```

## 🐛 Troubleshooting

### Error: "Using fallback Lambda URL"

**Causa**: No se configuró la variable de entorno `LAMBDA_FUNCTION_URL`

**Solución**:
1. En Netlify: Site settings > Environment variables
2. Agregar `LAMBDA_FUNCTION_URL` con tu URL real
3. Hacer redeploy

### Error: "Failed to fetch"

**Causa**: Problemas de CORS o URL incorrecta

**Solución**:
1. Verificar que la URL de Lambda sea correcta
2. Verificar configuración CORS en Lambda
3. Revisar logs de CloudWatch

### Error: "Invalid date format"

**Causa**: Formato de fecha incorrecto

**Solución**:
- Usar formato YYYY-MM-DD
- Verificar que la fecha no sea futura

## 📚 Recursos

- [Netlify Environment Variables](https://docs.netlify.com/environment-variables/overview/)
- [Telegram Mini Apps](https://core.telegram.org/bots/webapps)
- [AWS Lambda Function URLs](https://docs.aws.amazon.com/lambda/latest/dg/lambda-urls.html)

## 🔗 Enlaces

- [Documentación Principal](../README.md)
- [API Documentation](../API_DOCUMENTATION.md)
- [Troubleshooting](../TROUBLESHOOTING.md)