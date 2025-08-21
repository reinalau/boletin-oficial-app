# Boletín Oficial Telegram App

Una aplicación serverless que analiza automáticamente la normativa publicada en la sección "Legislación y Avisos Oficiales" del Boletín Oficial de la República Argentina utilizando inteligencia artificial.

## 📋 Descripción

Esta aplicación permite a los usuarios consultar y analizar la normativa argentina de manera automatizada. Utiliza AWS Lambda para acceder directamente al sitio web del Boletín Oficial (https://www.boletinoficial.gob.ar/), y genera análisis detallados usando Google Gemini LLM con acceso web directo.

### Características principales

- ✅ **Análisis automático**: Accede directamente al sitio web del Boletín Oficial para análisis en tiempo real
- ✅ **Inteligencia artificial**: Utiliza Google Gemini con acceso web para generar análisis detallados
- ✅ **Cache inteligente**: Almacena análisis previos en MongoDB para respuestas rápidas
- ✅ **API REST**: Interfaz HTTP para integración con aplicaciones frontend
- ✅ **Arquitectura serverless**: Escalable y costo-efectiva usando AWS Lambda
- ✅ **Seguridad**: Manejo seguro de credenciales via variables de entorno

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐
│ Telegram Mini   │───▶│ AWS Lambda      │
│ App (Frontend)  │    │ Function URL    │
└─────────────────┘    └─────────────────┘
                                │
                       ┌────────┼──────────┐
                       │        ▼          │
                       │ ┌──────────────┐  │ ┌─────────────┐
                       │ │ LLM Service  │  │ │ Database    │
                       │ │ (Direct)     │  │ │ Service     │
                       │ └──────────────┘  │ └─────────────┘
                       └───────────────────┘
                        │                   │                │
                        ▼                   ▼                ▼
                  ┌─────────────────┐  ┌──────────────┐  ┌─────────────┐
                  │ Boletín Oficial │  │ Google Gemini│  │ MongoDB     │
                  │ Website         │  │ (Web Access) │  │ Atlas       │
                  └─────────────────┘  └──────────────┘  └─────────────┘
```

## 🚀 Instalación y Despliegue

### Prerrequisitos

Antes de comenzar, asegúrate de tener instalado:

- **Python 3.11+** - [Descargar Python](https://www.python.org/downloads/)
- **Terraform 1.0+** - [Instalar Terraform](https://www.terraform.io/downloads.html)
- **AWS CLI** (opcional pero recomendado) - [Instalar AWS CLI](https://aws.amazon.com/cli/)
- **Git** - [Instalar Git](https://git-scm.com/downloads)

### Cuentas y servicios requeridos

1. **Cuenta AWS** con permisos para crear:
   - Lambda functions
   - Lambda Function URLs
   - IAM roles y policies
   - CloudWatch logs

2. **Google Cloud Account** para acceso a Gemini API:
   - Crear proyecto en [Google Cloud Console](https://console.cloud.google.com/)
   - Habilitar Gemini API
   - Generar API key

3. **MongoDB Atlas** (gratuito):
   - Crear cuenta en [MongoDB Atlas](https://www.mongodb.com/atlas)
   - Crear cluster gratuito
   - Obtener connection string

### Paso 1: Clonar el repositorio

```bash
git clone <repository-url>
cd boletin-oficial-telegram-app
```

### Paso 2: Configurar variables de entorno

1. Ejecuta el script de setup (recomendado):
```bash
scripts\setup.bat
```

O manualmente:

1. Copia el archivo de ejemplo:
```bash
copy scripts\iac\terraform.tfvars.example scripts\iac\terraform.tfvars
```

2. Edita `scripts\iac\terraform.tfvars` con tus valores:
```hcl
# Configuración del proyecto
project_name = "boletin-oficial-telegram-app"
environment  = "prod"
aws_region   = "us-east-1"

# Credenciales (REQUERIDAS)
google_api_key            = "tu-google-api-key-aqui"
mongodb_connection_string = "mongodb+srv://usuario:password@cluster.mongodb.net/?retryWrites=true&w=majority"

# Configuración de base de datos
mongodb_database   = "BoletinOficial"
mongodb_collection = "boletin-oficial"

# Configuración de Lambda
lambda_function_name = "boletin-oficial-analyzer"
lambda_memory_size   = 500
lambda_timeout       = 360

# Configuración opcional
cors_allowed_origins = ["*"]
```

### Paso 3: Configurar credenciales AWS

Elige una de las siguientes opciones:

**Opción A: Variables de entorno**
```bash
set AWS_ACCESS_KEY_ID=tu-access-key
set AWS_SECRET_ACCESS_KEY=tu-secret-key
set AWS_DEFAULT_REGION=us-east-1
```

**Opción B: AWS CLI**
```bash
aws configure
```

**Opción C: Perfil específico**
```bash
set AWS_PROFILE=tu-perfil
```

### Paso 4: Desplegar la aplicación

Ejecuta el script de despliegue:

```bash
deploy.bat
```

El script realizará automáticamente:
1. ✅ Verificación de prerrequisitos
2. ✅ Construcción del paquete Lambda
3. ✅ Inicialización de Terraform
4. ✅ Planificación del despliegue
5. ✅ Aplicación de la infraestructura
6. ✅ Configuración de Lambda Function URL

### Paso 5: Verificar el despliegue

Una vez completado el despliegue, verás información similar a:

```
🎉 Deployment completed successfully!

📋 Important information:
  📡 Lambda Function URL: https://w6scjpjua3bmj272d2dqhxy2ve000000.lambda-url.us-east-1.on.aws/
  🔍 Direct HTTPS Endpoint: https://w6scjpjua3bmj272d2dqhxy2ve000000.lambda-url.us-east-1.on.aws/

⚠️  Next steps:
  1. Test your API using the test script: python test_api.py
  2. Configure your Telegram Mini App to use the Lambda Function URL
  3. Monitor logs in AWS CloudWatch
```

### Paso 6: Probar la API

Ejecuta las pruebas automatizadas:

```bash
python test_api.py https://xxxxxxxxxxx.lambda-url.us-east-1.on.aws/
```

## 🔧 Configuración

### Variables de entorno principales

| Variable | Descripción | Requerida | Valor por defecto |
|----------|-------------|-----------|-------------------|
| `google_api_key` | API key de Google Gemini | ✅ Sí | - |
| `mongodb_connection_string` | String de conexión MongoDB Atlas | ✅ Sí | - |
| `mongodb_database` | Nombre de la base de datos | No | `BoletinOficial` |
| `mongodb_collection` | Nombre de la colección | No | `boletin-oficial` |
| `lambda_memory_size` | Memoria Lambda (MB) | No | `256` |
| `lambda_timeout` | Timeout Lambda (segundos) | No | `360` |
| `langchain_model` | Modelo Gemini a usar | No | `gemini-2.5-flash` |
| `langchain_temperature` | Temperatura del modelo | No | `0` |

### Configuración avanzada

Para configuraciones más avanzadas, puedes modificar las siguientes variables en `terraform.tfvars`:

```hcl
# Configuración de red (opcional)
enable_vpc = true
vpc_id     = "vpc-12345678"
subnet_ids = ["subnet-12345678", "subnet-87654321"]

# Configuración de seguridad
enable_waf = true
waf_rate_limit = 2000
allowed_ip_ranges = ["0.0.0.0/0"]

# Configuración de throttling
api_throttle_rate_limit  = 100
api_throttle_burst_limit = 200

# Tags adicionales
additional_tags = {
  Owner       = "tu-nombre"
  CostCenter  = "desarrollo"
  Environment = "production"
}
```

## 📖 Uso de la API

### Endpoint principal

```
POST https://[function-url].lambda-url.[region].on.aws/
```

### Formato de request

```json
{
  "fecha": "2024-01-15",
  "forzar_reanalisis": false
}
```

### Parámetros

| Parámetro | Tipo | Descripción | Requerido |
|-----------|------|-------------|-----------|
| `fecha` | string | Fecha en formato YYYY-MM-DD | No (usa fecha actual) |
| `forzar_reanalisis` | boolean | Forzar nuevo análisis ignorando cache | No (default: false) |

### Formato de response exitosa

```json
{
  "success": true,
  "data": {
    "fecha": "2024-01-15",
    "analisis": {
      "resumen": "Resumen ejecutivo de los cambios normativos...",
      "cambios_principales": [
        {
          "tipo": "decreto",
          "numero": "123/2024",
          "rotulo": "PODER EJECUTIVO. Decreto 123/2024. DECTO-2025-592-APN-PTE - Decreto N° 186/2022. Modificación.",
          "titulo": "Modificación de...",
          "descripcion": "Descripción del cambio",
          "impacto": "alto"
        }
      ],
      "impacto_estimado": "Análisis del impacto general",
      "areas_afectadas": ["tributario", "laboral", "comercial"]
    },
    "opiniones_expertos": [
      {
        "fuente": "Nombre del experto",
        "opinion": "Texto de la opinión",
        "fecha_opinion": "2024-01-15",
        "relevancia": "alta"
      }
    ],
    "metadatos": {
      "fecha_creacion": "2024-01-15T10:30:00Z",
      "tiempo_procesamiento": 25.5,
      "desde_cache": false
    }
  },
  "message": "Análisis completado exitosamente"
}
```

### Formato de response de error

```json
{
  "success": false,
  "error": {
    "code": "WEB_001",
    "message": "No se pudo acceder al contenido para la fecha especificada",
    "details": "Información adicional del error"
  },
  "message": "Error en el procesamiento"
}
```

### Códigos de error

| Código | Descripción | Status HTTP |
|--------|-------------|-------------|
| `WEB_001` | Error accediendo al sitio web | 404 |
| `WEB_002` | Error procesando contenido web | 500 |
| `LLM_001` | Error en servicio de IA | 503 |
| `DB_001` | Error de base de datos | 500 |
| `VALIDATION_001` | Error de validación | 400 |

### Ejemplos de uso

**Análisis de fecha específica:**
```bash
curl -X POST https://w6scjpjua3bmj272d2dqhxy2ve000000.lambda-url.us-east-1.on.aws/ \
  -H "Content-Type: application/json" \
  -d '{"fecha": "2024-01-15"}'
```

**Forzar nuevo análisis:**
```bash
curl -X POST https://w6scjpjua3bmj272d2dqhxy2ve000000.lambda-url.us-east-1.on.aws/ \
  -H "Content-Type: application/json" \
  -d '{"fecha": "2024-01-15", "forzar_reanalisis": true}'
```

**Análisis de fecha actual:**
```bash
curl -X POST https://w6scjpjua3bmj272d2dqhxy2ve000000.lambda-url.us-east-1.on.aws/ \
  -H "Content-Type: application/json" \
  -d '{"fecha": "2025-08-07"}'
```

## 🧪 Testing

### Pruebas automatizadas

El proyecto incluye un script de pruebas completo:

```bash
# Ejecutar todas las pruebas
python test_api.py https://w6scjpjua3bmj272d2dqhxy2ve000000.lambda-url.us-east-1.on.aws/

# Ejecutar con datos de prueba
python test_api.py https://w6scjpjua3bmj272d2dqhxy2ve000000.lambda-url.us-east-1.on.aws/ --load-test-data

# Ejecutar prueba específica
python test_api.py https://w6scjpjua3bmj272d2dqhxy2ve000000.lambda-url.us-east-1.on.aws/ --single-test health

# Con timeout personalizado
python test_api.py https://w6scjpjua3bmj272d2dqhxy2ve000000.lambda-url.us-east-1.on.aws/ --timeout 120
```

### Tipos de pruebas incluidas

1. **Health Check**: Verifica conectividad básica
2. **Input Validation**: Prueba validación de parámetros
3. **Recent Date Analysis**: Análisis con fecha reciente
4. **Old Date Analysis**: Análisis con fecha antigua
5. **Cache Functionality**: Verificación del sistema de cache
6. **Error Handling**: Manejo de errores

### Pruebas unitarias

```bash
# Instalar dependencias de testing
pip install pytest pytest-mock mongomock

# Ejecutar pruebas unitarias
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=services --cov=utils
```

## 📊 Monitoreo

### CloudWatch Logs

Los logs se almacenan automáticamente en CloudWatch:

- **Lambda logs**: `/aws/lambda/boletin-oficial-analyzer`

### Métricas importantes

1. **Invocation Count**: Número de invocaciones
2. **Duration**: Tiempo de ejecución
3. **Error Rate**: Tasa de errores
4. **Memory Usage**: Uso de memoria
5. **Cache Hit Rate**: Tasa de aciertos de cache

### Alertas recomendadas

```bash
# Error rate > 5%
aws cloudwatch put-metric-alarm \
  --alarm-name "BoletinOficial-HighErrorRate" \
  --alarm-description "High error rate in Lambda function" \
  --metric-name "Errors" \
  --namespace "AWS/Lambda" \
  --statistic "Sum" \
  --period 300 \
  --threshold 5 \
  --comparison-operator "GreaterThanThreshold"

# Duration > 4 minutes
aws cloudwatch put-metric-alarm \
  --alarm-name "BoletinOficial-HighDuration" \
  --alarm-description "High duration in Lambda function" \
  --metric-name "Duration" \
  --namespace "AWS/Lambda" \
  --statistic "Average" \
  --period 300 \
  --threshold 240000 \
  --comparison-operator "GreaterThanThreshold"
```

## 🔒 Seguridad

### Mejores prácticas implementadas

1. **Variables de entorno**: Credenciales manejadas de forma segura via Lambda environment variables
2. **IAM Roles**: Permisos mínimos necesarios
3. **HTTPS**: Todas las comunicaciones encriptadas
4. **Rate Limiting**: Protección contra abuso
5. **Input Validation**: Validación estricta de parámetros
6. **CORS**: Configuración restrictiva de orígenes

### Configuración de seguridad adicional

Para entornos de producción, considera:

```hcl
# Habilitar WAF
enable_waf = true
waf_rate_limit = 1000

# Restringir IPs
allowed_ip_ranges = ["203.0.113.0/24", "198.51.100.0/24"]

# Habilitar VPC
enable_vpc = true
vpc_id = "vpc-12345678"
subnet_ids = ["subnet-12345678", "subnet-87654321"]
```

## 🚨 Troubleshooting

### Problemas comunes y soluciones

#### 1. Error de credenciales AWS

**Síntoma**: `Unable to locate credentials`

**Solución**:
```bash
# Verificar credenciales
aws sts get-caller-identity

# Configurar si es necesario
aws configure
```

#### 2. Error de API key de Google

**Síntoma**: `Invalid API key` o `Permission denied`

**Solución**:
1. Verificar que la API key sea correcta
2. Asegurar que Gemini API esté habilitada
3. Verificar cuotas y límites

#### 3. Error de conexión MongoDB

**Síntoma**: `Connection timeout` o `Authentication failed`

**Solución**:
1. Verificar connection string
2. Verificar whitelist de IPs en MongoDB Atlas
3. Verificar credenciales de usuario

#### 4. Lambda timeout

**Síntoma**: `Task timed out after 300.00 seconds`

**Solución**:
```hcl
# Aumentar timeout en terraform.tfvars
lambda_timeout = 600  # 10 minutos
lambda_memory_size = 2048  # Más memoria = más CPU
```

#### 5. Paquete Lambda muy grande

**Síntoma**: `Unzipped size must be smaller than 262144000 bytes`

**Solución**:
1. Revisar dependencias en `requirements.txt`
2. Usar layers para dependencias grandes
3. Optimizar código y eliminar archivos innecesarios

#### 6. Error de permisos IAM

**Síntoma**: `User is not authorized to perform: lambda:InvokeFunction`

**Solución**:
1. Verificar políticas IAM
2. Asegurar que el rol tenga permisos correctos
3. Revisar resource-based policies

### Logs de debugging

Para debugging detallado:

```bash
# Ver logs de Lambda en tiempo real
aws logs tail /aws/lambda/boletin-oficial-analyzer --follow

# Ver configuración de Function URL
aws lambda get-function-url-config --function-name boletin-oficial-analyzer

# Filtrar por errores
aws logs filter-log-events \
  --log-group-name /aws/lambda/boletin-oficial-analyzer \
  --filter-pattern "ERROR"
```

### Comandos útiles para debugging

```bash
# Verificar estado de Terraform
terraform show

# Verificar configuración
terraform validate

# Ver outputs
terraform output

# Refrescar estado
terraform refresh

# Importar recurso existente
terraform import aws_lambda_function.boletin_analyzer nombre-funcion
```

## 🔄 Mantenimiento

### Actualizaciones

Para actualizar la aplicación:

1. **Actualizar código**:
```bash
git pull origin main
```

2. **Reconstruir y redesplegar**:
```bash
deploy.bat
```

3. **Solo actualizar código Lambda**:
```bash
build.bat
# Subir manualmente el ZIP a AWS Lambda Console
```

### Backup

**Base de datos**:
```bash
# Backup de MongoDB Atlas (automático)
# Configurar en MongoDB Atlas Console > Backup
```

**Configuración**:
```bash
# Backup de estado de Terraform
copy terraform.tfstate terraform.tfstate.backup.$(date +%Y%m%d)
```

### Limpieza

Para limpiar recursos temporales:

```bash
# Limpiar archivos de build
del lambda_deployment.zip
rmdir /s lambda_package

# Limpiar logs antiguos (opcional)
aws logs delete-log-group --log-group-name /aws/lambda/boletin-oficial-analyzer
```

## 🗑️ Desinstalación

Para eliminar completamente la aplicación:

```bash
# CUIDADO: Esto eliminará TODOS los recursos
destroy.bat

# O con confirmación automática
destroy.bat /force
```

## 📞 Soporte

### Recursos adicionales

- [Documentación de AWS Lambda](https://docs.aws.amazon.com/lambda/)
- [Documentación de Terraform](https://www.terraform.io/docs/)
- [Google Generative AI Documentation](https://ai.google.dev/docs)
- [Google Gemini API](https://ai.google.dev/docs)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)

### Reportar problemas

Si encuentras problemas:

1. Revisar esta documentación
2. Verificar logs en CloudWatch
3. Ejecutar pruebas de diagnóstico
4. Crear issue en el repositorio con:
   - Descripción del problema
   - Logs relevantes
   - Pasos para reproducir
   - Configuración (sin credenciales)

## 📱 Configuración de Telegram Mini App (Opcional)

Una vez que tengas el backend y frontend desplegados, puedes configurar la aplicación como una Telegram Mini App para una experiencia nativa.

### Prerrequisitos

- ✅ Backend desplegado (Lambda Function URL funcionando)
- ✅ Frontend desplegado (en Netlify, Vercel, etc.)
- 📱 Bot de Telegram creado

### Paso 1: Crear Bot de Telegram

1. **Abrir Telegram** y buscar `@BotFather`
2. **Enviar** `/newbot`
3. **Seguir instrucciones** para crear tu bot
4. **Guardar el token** que te proporciona BotFather

### Paso 2: Configurar Mini App

1. **Enviar a BotFather**: `/newapp`
2. **Seleccionar tu bot** de la lista
3. **Configurar la aplicación**:
   - **Title**: `Boletín Oficial Argentina`
   - **Description**: `Análisis inteligente del Boletín Oficial argentino`
   - **Photo**: Subir un ícono (512x512 px recomendado)
   - **Web App URL**: `https://tu-frontend.netlify.app` (tu URL de Netlify/vercel o hosting elegido)

### Paso 3: Configurar Comandos del Bot

Enviar a BotFather: `/setcommands`

```
start - Iniciar análisis del Boletín Oficial
help - Ayuda y información
analyze - Abrir Mini App para análisis
```

### Paso 4: Configurar Menu Button

1. **Enviar a BotFather**: `/setmenubutton`
2. **Seleccionar tu bot**
3. **Configurar**:
   - **Button text**: `📊 Analizar Boletín`
   - **Web App URL**: `https://tu-frontend.netlify.app`

### Paso 5: Configurar Descripción

Enviar a BotFather: `/setdescription`

```
🇦🇷 Bot oficial para análisis inteligente del Boletín Oficial de la República Argentina.

✨ Características:
• Análisis automático con IA
• Resumen de cambios normativos
• Opiniones de expertos
• Búsqueda por fecha
• Interfaz intuitiva

Desarrollado con AWS Lambda y Google Gemini AI.
```

### Paso 6: Configurar About Text

Enviar a BotFather: `/setabouttext`

```
Análisis inteligente del Boletín Oficial argentino usando IA. Obtén resúmenes automáticos de cambios normativos, impacto estimado y opiniones de expertos.
```

### Paso 7: Probar la Mini App

1. **Buscar tu bot** en Telegram
2. **Enviar** `/start`
3. **Hacer clic** en el botón "📊 Analizar Boletín"
4. **Verificar** que se abra tu frontend correctamente

### Configuración Avanzada (Opcional)

#### Personalización de la Mini App

En tu frontend, puedes detectar el tema de Telegram:

```javascript
// En tu app.js
if (window.Telegram?.WebApp) {
    const tg = window.Telegram.WebApp;
    
    // Aplicar tema de Telegram
    document.documentElement.style.setProperty('--tg-theme-bg-color', tg.themeParams.bg_color);
    document.documentElement.style.setProperty('--tg-theme-text-color', tg.themeParams.text_color);
    
    // Configurar botón principal
    tg.MainButton.setText('Analizar Boletín');
    tg.MainButton.show();
}
```

#### Botones de Telegram

```javascript
// Configurar botones nativos de Telegram
if (window.Telegram?.WebApp) {
    const tg = window.Telegram.WebApp;
    
    // Botón principal
    tg.MainButton.setText('🔍 Analizar');
    tg.MainButton.onClick(() => {
        handleAnalyze();
    });
    
    // Botón de atrás
    tg.BackButton.onClick(() => {
        showDateSelector();
    });
}
```

### Troubleshooting

#### Mini App no se abre

1. **Verificar URL**: Debe ser HTTPS
2. **Verificar certificado SSL**: Debe ser válido
3. **Probar URL** directamente en navegador

#### Errores de CORS

1. **Verificar headers** en tu Lambda
2. **Verificar configuración** de Netlify
3. **Revisar logs** de CloudWatch

### Recursos Útiles

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Telegram Mini Apps](https://core.telegram.org/bots/webapps)
- [BotFather Commands](https://core.telegram.org/bots#botfather)
- [Telegram Web App SDK](https://core.telegram.org/bots/webapps#initializing-mini-apps)

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver archivo `LICENSE` para más detalles.

