# Guía de Despliegue - Boletín Oficial Telegram App

Esta guía te llevará paso a paso a través del proceso completo de despliegue de la aplicación.

## 📋 Lista de Verificación Pre-Despliegue

Antes de comenzar, asegúrate de tener todo lo necesario:

### ✅ Software Requerido

- [ ] **Python 3.11+** instalado y en PATH
- [ ] **Terraform 1.0+** instalado y en PATH
- [ ] **Git** instalado
- [ ] **AWS CLI** (opcional pero recomendado)

### ✅ Cuentas y Servicios

- [ ] **Cuenta AWS** con permisos administrativos
- [ ] **Google Cloud Account** con Gemini API habilitada
- [ ] **MongoDB Atlas** cluster creado (gratuito)

### ✅ Credenciales Preparadas

- [ ] AWS Access Key ID y Secret Access Key
- [ ] Google Gemini API Key
- [ ] MongoDB Atlas Connection String

## 🚀 Proceso de Despliegue Paso a Paso

### Paso 1: Preparación del Entorno

#### 1.1 Clonar el Repositorio

```bash
git clone <repository-url>
cd boletin-oficial-telegram-app
```

#### 1.2 Verificar Prerrequisitos

Ejecuta este comando para verificar que todo esté instalado:

```bash
python --version
terraform version
git --version
```

**Salida esperada:**
```
Python 3.11.x
Terraform v1.x.x
git version 2.x.x
```

### Paso 2: Configuración de Credenciales AWS

Elige **UNA** de las siguientes opciones:

#### Opción A: Variables de Entorno (Recomendado para desarrollo)

```bash
# Windows
set AWS_ACCESS_KEY_ID=AKIA...
set AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI...
set AWS_DEFAULT_REGION=us-east-1

# Linux/Mac
export AWS_ACCESS_KEY_ID=AKIA...
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI...
export AWS_DEFAULT_REGION=us-east-1
```

#### Opción B: AWS CLI (Recomendado para uso personal)

```bash
aws configure
```

Ingresa cuando se solicite:
- AWS Access Key ID: `AKIA...`
- AWS Secret Access Key: `wJalrXUtnFEMI...`
- Default region name: `us-east-1`
- Default output format: `json`

#### Opción C: Perfil Específico

```bash
aws configure --profile mi-proyecto
set AWS_PROFILE=mi-proyecto
```

#### Verificar Configuración

```bash
aws sts get-caller-identity
```

**Salida esperada:**
```json
{
    "UserId": "AIDACKCEVSQ6C2EXAMPLE",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/DevAdmin"
}
```

### Paso 3: Obtener Credenciales de Servicios Externos

#### 3.1 Google Gemini API Key

1. **Ir a Google Cloud Console**:
   - Visita: https://console.cloud.google.com/

2. **Crear/Seleccionar Proyecto**:
   - Crear nuevo proyecto o seleccionar existente

3. **Habilitar APIs**:
   - Ir a "APIs & Services" > "Library"
   - Buscar "Generative AI API"
   - Hacer clic en "Enable"

4. **Crear API Key**:
   - Ir a "APIs & Services" > "Credentials"
   - Hacer clic en "Create Credentials" > "API Key"
   - Copiar la API key generada

5. **Configurar Restricciones** (Opcional pero recomendado):
   - Hacer clic en la API key creada
   - En "API restrictions", seleccionar "Generative AI API"

6. **El modelo capa gratuita de gemini actual es gemini-2.5-flash**

#### 3.2 MongoDB Atlas Connection String

1. **Crear Cuenta en MongoDB Atlas**:
   - Visita: https://www.mongodb.com/atlas
   - Crear cuenta gratuita

2. **Crear Cluster**:
   - Seleccionar "Build a Database"
   - Elegir "M0 Sandbox" (gratuito)
   - Seleccionar región (preferiblemente us-east-1)
   - Nombrar cluster (ej: "Cluster0")

3. **Configurar Acceso**:
   - **Database Access**: Crear usuario con permisos de lectura/escritura
   - **Network Access**: Agregar IP `0.0.0.0/0` (permitir desde cualquier lugar)

4. **Obtener Connection String**:
   - Hacer clic en "Connect" en tu cluster
   - Seleccionar "Connect your application"
   - Copiar el connection string
   - Reemplazar `<password>` con tu password real

**Formato esperado:**
```
mongodb+srv://usuario:password@cluster0.abc123.mongodb.net/?retryWrites=true&w=majority
```

### Paso 4: Configuración del Proyecto

#### 4.1 Crear Archivo de Configuración

```bash
copy scripts\iac\terraform.tfvars.example scripts\iac\terraform.tfvars
```

#### 4.2 Editar Configuración

Abre `scripts\iac\terraform.tfvars` en tu editor favorito y completa los valores:

```hcl
# VALORES REQUERIDOS - COMPLETAR CON TUS CREDENCIALES REALES
google_api_key = "AIzaSyC-tu-api-key-real-aqui"
mongodb_connection_string = "mongodb+srv://usuario:password@cluster0.abc123.mongodb.net/?retryWrites=true&w=majority"

# CONFIGURACIÓN BÁSICA (ajustar si es necesario)
project_name = "boletin-oficial-telegram-app"
environment = "prod"
aws_region = "us-east-1"

# CONFIGURACIÓN DE LAMBDA (ajustar según necesidades)
lambda_memory_size = 500  # MB
lambda_timeout = 360       # segundos (6 minutos)


#### 4.3 Validar Configuración

```bash
# Verificar que no hay valores placeholder
findstr /c:"your-.*-here" /c:"example" /c:"changeme" terraform.tfvars
```

**No debe mostrar ningún resultado** si la configuración está completa.

### Paso 5: Despliegue de la Infraestructura

#### 5.1 Ejecutar Script de Despliegue

```bash
deploy.bat
```

El script realizará automáticamente:

1. ✅ **Verificación de prerrequisitos**
2. ✅ **Construcción del paquete Lambda**
3. ✅ **Inicialización de Terraform**
4. ✅ **Planificación del despliegue**
5. ✅ **Aplicación de la infraestructura**

#### 5.2 Monitorear el Progreso

Durante el despliegue verás salida similar a:

```
🚀 Starting deployment process...
===============================================

🔍 Checking prerequisites...
✅ Terraform version: v1.6.0
✅ AWS CLI is available
✅ Prerequisites check completed

📦 Building Lambda deployment package...
✅ Lambda package built successfully
✅ Package size: 15728640 bytes

🏗️  Initializing Terraform...
✅ Terraform initialized successfully

✅ Validating Terraform configuration...
✅ Terraform configuration is valid

📋 Planning Terraform deployment...
Plan: 15 to add, 0 to change, 0 to destroy.
✅ Terraform plan created successfully

🚀 Applying Terraform configuration...
Apply complete! Resources: 15 added, 0 changed, 0 destroyed.
✅ Terraform deployment completed successfully
```

#### 5.3 Obtener Información de Despliegue

Al finalizar, verás información importante:

```
🎉 Deployment completed successfully!

📋 Important information:
  📡 API Gateway URL: https://abc123def.execute-api.us-east-1.amazonaws.com/v1
  🔍 Analyze Endpoint: https://abc123def.execute-api.us-east-1.amazonaws.com/v1/analyze

⚠️  Next steps:
  1. Test your API using the test script: python test_api.py
  2. Configure your Telegram Mini App to use the API endpoint
  3. Monitor logs in AWS CloudWatch
```

**¡IMPORTANTE!** Guarda la URL del API Gateway, la necesitarás para configurar tu frontend.

### Paso 6: Verificación del Despliegue

#### 6.1 Prueba Básica de Conectividad

```bash
curl -X POST https://tu-api-gateway-url.execute-api.us-east-1.amazonaws.com/v1/analyze ^
  -H "Content-Type: application/json" ^
  -d "{}"
```

**Respuesta esperada** (puede variar según disponibilidad de datos):
```json
{
  "success": true,
  "data": {
    "fecha": "2024-01-15",
    "analisis": {...},
    "metadatos": {...}
  }
}
```

#### 6.2 Ejecutar Suite de Pruebas Completa

```bash
python test_api.py https://tu-api-gateway-url.execute-api.us-east-1.amazonaws.com/v1
```

**Salida esperada:**
```
[10:30:15] INFO: Starting comprehensive API test suite
[10:30:15] INFO: API URL: https://abc123def.execute-api.us-east-1.amazonaws.com/v1
[10:30:15] INFO: Timeout: 60s
------------------------------------------------------------
[10:30:15] INFO: Running test: API Health Check
[10:30:16] SUCCESS: ✓ API Health Check PASSED (1.23s)

[10:30:16] INFO: Running test: Input Validation
[10:30:17] SUCCESS: ✓ Input Validation PASSED (0.89s)

...

============================================================
[10:30:45] INFO: TEST SUMMARY
============================================================
[10:30:45] INFO: Total tests run: 6
[10:30:45] SUCCESS: Tests passed: 6
[10:30:45] SUCCESS: All tests passed! 🎉
```

### Paso 7: Configuración Post-Despliegue

#### 7.1 Configurar Monitoreo

1. **Ir a AWS CloudWatch Console**:
   - https://console.aws.amazon.com/cloudwatch/

2. **Verificar Log Groups**:
   - `/aws/lambda/boletin-oficial-analyzer`
   - `API-Gateway-Execution-Logs_[api-id]/v1`

3. **Configurar Alertas** (Opcional):
```bash
# Alerta por alta tasa de errores
aws cloudwatch put-metric-alarm \
  --alarm-name "BoletinOficial-HighErrorRate" \
  --alarm-description "High error rate in Lambda function" \
  --metric-name "Errors" \
  --namespace "AWS/Lambda" \
  --statistic "Sum" \
  --period 300 \
  --threshold 5 \
  --comparison-operator "GreaterThanThreshold" \
  --dimensions Name=FunctionName,Value=boletin-oficial-analyzer
```

#### 7.2 Configurar Backup (Recomendado)

1. **MongoDB Atlas**:
   - Los backups automáticos están habilitados por defecto
   - Verificar en Atlas Console > Backup

2. **Terraform State**:
```bash
# Crear backup del estado
copy terraform.tfstate terraform.tfstate.backup.%date:~-4,4%%date:~-10,2%%date:~-7,2%
```

## 🔧 Configuraciones Avanzadas

### Configuración para Producción

Para un entorno de producción, considera estas configuraciones adicionales:

```hcl
# En terraform.tfvars

# Aumentar recursos para mejor performance
lambda_memory_size = 2048
lambda_timeout = 600

# Habilitar seguridad adicional
enable_waf = true
waf_rate_limit = 1000

# Restringir acceso por IP
allowed_ip_ranges = ["203.0.113.0/24"]  # Tu rango de IPs

# Configurar VPC para mayor seguridad
enable_vpc = true
vpc_id = "vpc-12345678"
subnet_ids = ["subnet-12345678", "subnet-87654321"]

# Tags para organización
additional_tags = {
  Environment = "production"
  Owner       = "tu-nombre"
  CostCenter  = "proyecto-telegram"
  Backup      = "required"
}
```

### Configuración Multi-Región

Para desplegar en múltiples regiones:

1. **Crear configuración por región**:
```bash
# Región principal
copy terraform.tfvars terraform.tfvars.us-east-1
# Editar aws_region = "us-east-1"

# Región secundaria
copy terraform.tfvars terraform.tfvars.eu-west-1
# Editar aws_region = "eu-west-1"
```

2. **Desplegar por región**:
```bash
# Región principal
terraform apply -var-file="terraform.tfvars.us-east-1"

# Región secundaria
terraform apply -var-file="terraform.tfvars.eu-west-1"
```

## 📊 Monitoreo y Mantenimiento

### Métricas Importantes a Monitorear

1. **Lambda Metrics**:
   - Invocations (número de invocaciones)
   - Duration (tiempo de ejecución)
   - Errors (errores)
   - Throttles (throttling)

2. **API Gateway Metrics**:
   - Count (número de requests)
   - Latency (latencia)
   - 4XXError (errores del cliente)
   - 5XXError (errores del servidor)

3. **Custom Metrics**:
   - Cache hit rate
   - Web content processing time
   - LLM response time

### Comandos de Monitoreo

```bash
# Ver logs en tiempo real
aws logs tail /aws/lambda/boletin-oficial-analyzer --follow

# Ver métricas de Lambda
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=boletin-oficial-analyzer \
  --statistics Average \
  --start-time 2024-01-15T00:00:00Z \
  --end-time 2024-01-15T23:59:59Z \
  --period 3600

# Ver estado de la función
aws lambda get-function --function-name boletin-oficial-analyzer
```

## 🔄 Actualizaciones y Mantenimiento

### Actualizar Solo el Código Lambda

```bash
# Reconstruir paquete
build.bat

# Actualizar función (manual)
aws lambda update-function-code \
  --function-name boletin-oficial-analyzer \
  --zip-file fileb://lambda_deployment.zip
```

### Actualización Completa

```bash
# Actualizar código desde repositorio
git pull origin main

# Redesplegar completamente
deploy.bat
```

### Rollback en Caso de Problemas

```bash
# Volver a versión anterior
terraform apply -var-file="terraform.tfvars.backup"

# O restaurar desde backup
copy terraform.tfstate.backup terraform.tfstate
terraform refresh
```

## 🗑️ Limpieza y Desinstalación

### Eliminar Recursos de Prueba

```bash
# Solo limpiar archivos locales
destroy.bat /cleanup-only
```

### Desinstalación Completa

```bash
# CUIDADO: Esto eliminará TODOS los recursos
destroy.bat

# Con confirmación automática (para scripts)
destroy.bat /force
```

## 🆘 Solución de Problemas Comunes

### Error: "terraform.tfvars not found"

```bash
# Verificar que el archivo existe
dir terraform.tfvars

# Si no existe, crearlo desde el ejemplo
copy terraform.tfvars.example terraform.tfvars
```

### Error: "Invalid API key"

1. Verificar que la API key sea correcta
2. Verificar que Gemini API esté habilitada
3. Verificar restricciones de la API key

### Error: "Connection timeout" (MongoDB)

1. Verificar connection string
2. Verificar whitelist de IPs en MongoDB Atlas
3. Verificar credenciales de usuario

### Error: "Lambda timeout"

```hcl
# Aumentar timeout en terraform.tfvars
lambda_timeout = 600  # 10 minutos
lambda_memory_size = 2048  # Más memoria = más CPU
```

## 📞 Obtener Ayuda

Si encuentras problemas durante el despliegue:

1. **Revisar logs**:
```bash
aws logs tail /aws/lambda/boletin-oficial-analyzer --since 1h
```

2. **Verificar estado de Terraform**:
```bash
terraform show
terraform validate
```

3. **Ejecutar diagnóstico**:
```bash
python test_api.py https://tu-api-url.execute-api.us-east-1.amazonaws.com/v1 --single-test health
```

4. **Consultar documentación**:
   - [README.md](README.md) - Documentación general
   - [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Guía de problemas
   - [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Documentación de API

---

**¡Felicitaciones!** 🎉 Si has llegado hasta aquí, tu aplicación debería estar funcionando correctamente. Ahora puedes integrarla con tu Telegram Mini App y comenzar a analizar el Boletín Oficial de Argentina.