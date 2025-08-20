# Guía de Troubleshooting - Boletín Oficial Telegram App

Esta guía te ayudará a diagnosticar y resolver los problemas más comunes que puedes encontrar al desplegar y usar la aplicación.

## 🔍 Diagnóstico Rápido

### Script de Diagnóstico Automático

Ejecuta este comando para un diagnóstico rápido:

```bash
# Windows
python -c "
import subprocess
import sys
import os

print('=== DIAGNÓSTICO RÁPIDO ===')
print()

# Check Python
try:
    import sys
    print(f'✅ Python: {sys.version}')
except:
    print('❌ Python no encontrado')

# Check Terraform
try:
    result = subprocess.run(['terraform', 'version'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f'✅ Terraform: {result.stdout.split()[1]}')
    else:
        print('❌ Terraform no encontrado')
except:
    print('❌ Terraform no encontrado')

# Check AWS CLI
try:
    result = subprocess.run(['aws', '--version'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f'✅ AWS CLI: {result.stdout.strip()}')
    else:
        print('❌ AWS CLI no encontrado')
except:
    print('❌ AWS CLI no encontrado')

# Check files
files = ['scripts/iac/terraform.tfvars', 'lambda_function.py', 'requirements.txt']
for file in files:
    if os.path.exists(file):
        print(f'✅ {file} existe')
    else:
        print(f'❌ {file} no encontrado')

print()
print('=== VARIABLES DE ENTORNO ===')
aws_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_PROFILE', 'AWS_DEFAULT_REGION']
for var in aws_vars:
    if os.environ.get(var):
        print(f'✅ {var} configurada')
    else:
        print(f'⚠️  {var} no configurada')
"
```

## 🚨 Problemas de Instalación

### 1. Error: "Terraform not found"

**Síntomas**:
```
'terraform' is not recognized as an internal or external command
```

**Soluciones**:

1. **Instalar Terraform**:
   - Descargar desde [terraform.io](https://www.terraform.io/downloads.html)
   - Extraer a una carpeta (ej: `C:\terraform`)
   - Agregar a PATH del sistema

2. **Verificar instalación**:
```bash
terraform version
```

3. **Instalación alternativa con Chocolatey**:
```bash
choco install terraform
```

### 2. Error: "Python not found"

**Síntomas**:
```
'python' is not recognized as an internal or external command
```

**Soluciones**:

1. **Instalar Python 3.11+**:
   - Descargar desde [python.org](https://www.python.org/downloads/)
   - ✅ Marcar "Add Python to PATH" durante instalación

2. **Verificar instalación**:
```bash
python --version
pip --version
```

3. **Si tienes múltiples versiones**:
```bash
py -3.11 --version
```

### 3. Error: "pip install failed"

**Síntomas**:
```
ERROR: Could not install packages due to an EnvironmentError
```

**Soluciones**:

1. **Actualizar pip**:
```bash
python -m pip install --upgrade pip
```

2. **Usar usuario local**:
```bash
pip install --user -r requirements.txt
```

3. **Limpiar cache**:
```bash
pip cache purge
pip install --no-cache-dir -r requirements.txt
```

## 🔑 Problemas de Credenciales

### 1. Error: "Unable to locate credentials"

**Síntomas**:
```
NoCredentialsError: Unable to locate credentials
```

**Diagnóstico**:
```bash
aws sts get-caller-identity
```

**Soluciones**:

1. **Configurar AWS CLI**:
```bash
aws configure
```

2. **Variables de entorno**:
```bash
set AWS_ACCESS_KEY_ID=tu-access-key
set AWS_SECRET_ACCESS_KEY=tu-secret-key
set AWS_DEFAULT_REGION=us-east-1
```

3. **Usar perfil específico**:
```bash
set AWS_PROFILE=mi-perfil
```

4. **Verificar credenciales**:
```bash
aws configure list
```

### 2. Error: "Access Denied"

**Síntomas**:
```
AccessDenied: User: arn:aws:iam::123456789012:user/myuser is not authorized
```

**Soluciones**:

1. **Verificar permisos IAM**:
   - Lambda: `AWSLambdaFullAccess`
   - IAM: `IAMFullAccess`
   - CloudWatch: `CloudWatchFullAccess`

2. **Política mínima requerida**:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lambda:*",
                "iam:*",
                "logs:*"
            ],
            "Resource": "*"
        }
    ]
}
```

### 3. Error: "Invalid API key" (Google)

**Síntomas**:
```
google.api_core.exceptions.PermissionDenied: 403 API key not valid
```

**Soluciones**:

1. **Verificar API key**:
   - Ir a [Google Cloud Console](https://console.cloud.google.com/)
   - APIs & Services > Credentials
   - Verificar que la key esté activa

2. **Habilitar APIs necesarias**:
   - Generative AI API
   - Vertex AI API

3. **Verificar restricciones**:
   - Quitar restricciones de IP si existen
   - Verificar restricciones de API

## 🗄️ Problemas de Base de Datos

### 1. Error: "Connection timeout" (MongoDB)

**Síntomas**:
```
pymongo.errors.ServerSelectionTimeoutError: connection timeout
```

**Soluciones**:

1. **Verificar connection string**:
```python
# Formato correcto:
mongodb+srv://usuario:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

2. **Verificar whitelist de IPs**:
   - MongoDB Atlas > Network Access
   - Agregar `0.0.0.0/0` para permitir todas las IPs
   - O agregar IPs específicas de AWS Lambda

3. **Verificar credenciales**:
   - Usuario y password correctos
   - Usuario tiene permisos de lectura/escritura

4. **Test de conexión**:
```python
from pymongo import MongoClient
client = MongoClient("tu-connection-string")
print(client.admin.command('ping'))
```

### 2. Error: "Authentication failed"

**Síntomas**:
```
pymongo.errors.OperationFailure: Authentication failed
```

**Soluciones**:

1. **Verificar credenciales**:
   - Usuario existe en MongoDB Atlas
   - Password es correcto
   - Usuario tiene permisos en la base de datos

2. **Recrear usuario**:
   - MongoDB Atlas > Database Access
   - Eliminar y recrear usuario
   - Asignar rol `readWrite`

## 🏗️ Problemas de Terraform

### 1. Error: "terraform.tfvars not found"

**Síntomas**:
```
Error: terraform.tfvars not found
```

**Soluciones**:

1. **Crear archivo de configuración**:
```bash
copy scripts\iac\terraform.tfvars.example scripts\iac\terraform.tfvars
```

2. **Editar con valores reales**:
```hcl
google_api_key = "tu-api-key-real"
mongodb_connection_string = "tu-connection-string-real"
```

### 2. Error: "Invalid provider configuration"

**Síntomas**:
```
Error: Invalid provider configuration
```

**Soluciones**:

1. **Reinicializar Terraform**:
```bash
terraform init -upgrade
```

2. **Limpiar cache**:
```bash
rmdir /s .terraform
terraform init
```

### 3. Error: "Resource already exists"

**Síntomas**:
```
Error: resource already exists
```

**Soluciones**:

1. **Importar recurso existente**:
```bash
terraform import aws_lambda_function.boletin_analyzer nombre-funcion-existente
```

2. **Destruir y recrear**:
```bash
terraform destroy
terraform apply
```

## 🚀 Problemas de Despliegue

### 1. Error: "Lambda package too large"

**Síntomas**:
```
InvalidParameterValueException: Unzipped size must be smaller than 262144000 bytes
```

**Soluciones**:

1. **Optimizar dependencias**:
```bash
# Editar requirements.txt, remover dependencias innecesarias
pip install --no-deps -r requirements.txt
```

2. **Usar Lambda Layers**:
```hcl
# En main.tf
resource "aws_lambda_layer_version" "dependencies" {
  filename   = "dependencies.zip"
  layer_name = "python-dependencies"
  compatible_runtimes = ["python3.11"]
}
```

3. **Verificar tamaño**:
```bash
# Ver tamaño del ZIP
dir lambda_deployment.zip
```

### 2. Error: "Lambda timeout"

**Síntomas**:
```
Task timed out after 300.00 seconds
```

**Soluciones**:

1. **Aumentar timeout**:
```hcl
# En terraform.tfvars
lambda_timeout = 600  # 10 minutos
```

2. **Aumentar memoria**:
```hcl
# En terraform.tfvars
lambda_memory_size = 2048  # Más memoria = más CPU
```

3. **Optimizar código**:
   - Usar cache para evitar reprocesamiento
   - Optimizar queries a base de datos
   - Reducir llamadas a APIs externas

### 3. Error: "Lambda Function URL CORS"

**Síntomas**:
```
Access to fetch at 'https://xxx.lambda-url.us-east-1.on.aws/' from origin 'https://myapp.com' has been blocked by CORS policy
```

**Diagnóstico**:
```bash
# Ver logs de Lambda
aws logs tail /aws/lambda/boletin-oficial-analyzer --follow
```

**Soluciones**:

1. **Verificar configuración CORS en Terraform**:
```hcl
resource "aws_lambda_function_url" "boletin_analyzer_url" {
  function_name      = aws_lambda_function.boletin_analyzer.function_name
  authorization_type = "NONE"

  cors {
    allow_credentials = false
    allow_origins     = ["*"]
    allow_methods     = ["*"]
    allow_headers     = ["*"]
    max_age          = 86400
  }
}
```

2. **Verificar headers en Lambda**:
```python
# Lambda debe retornar headers CORS
return {
    'statusCode': 200,
    'headers': {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    },
    'body': json.dumps(response_data)
}
```

3. **Manejar OPTIONS requests**:
```python
# En lambda_function.py
if event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        },
        'body': ''
    }
```

## 🧪 Problemas de Testing

### 1. Error: "Connection refused" en tests

**Síntomas**:
```
requests.exceptions.ConnectionError: Connection refused
```

**Soluciones**:

1. **Verificar URL de Lambda Function**:
```bash
# Obtener URL correcta
terraform output lambda_function_url
```

2. **Verificar despliegue**:
```bash
# Verificar que Lambda esté activa
aws lambda get-function --function-name boletin-oficial-analyzer
```

3. **Test manual**:
```bash
curl -X POST https://xxx.lambda-url.us-east-1.on.aws/ -H "Content-Type: application/json" -d '{"fecha":"2025-08-07","forzar_reanalisis":false}'
```

### 2. Error: "Test data not loading"

**Síntomas**:
```
Error loading test data: pymongo not available
```

**Soluciones**:

1. **Instalar pymongo**:
```bash
pip install pymongo
```

2. **Configurar variables de entorno**:
```bash
set MONGODB_CONNECTION_STRING=tu-connection-string
set MONGODB_DATABASE=BoletinOficial
```

## 📊 Problemas de Monitoreo

### 1. No aparecen logs en CloudWatch

**Soluciones**:

1. **Verificar permisos IAM**:
```json
{
    "Effect": "Allow",
    "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
    ],
    "Resource": "arn:aws:logs:*:*:*"
}
```

2. **Verificar log group**:
```bash
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/boletin"
```

### 2. Métricas no aparecen

**Soluciones**:

1. **Esperar tiempo de propagación** (5-10 minutos)

2. **Verificar región**:
```bash
# Asegurar que estás viendo la región correcta
aws configure get region
```

## 🔧 Comandos de Diagnóstico

### Verificar estado de recursos

```bash
# Estado de Terraform
terraform show

# Estado de Lambda
aws lambda get-function --function-name boletin-oficial-analyzer

# Estado de Lambda Function URL
aws lambda get-function-url-config --function-name boletin-oficial-analyzer

# Logs recientes
aws logs tail /aws/lambda/boletin-oficial-analyzer --since 1h
```

### Test de conectividad

```bash
# Test de Lambda Function URL
curl -X OPTIONS https://xxx.lambda-url.us-east-1.on.aws/

# Test de Lambda directamente
aws lambda invoke --function-name boletin-oficial-analyzer --payload '{}' response.json

# Test de base de datos
python -c "
from pymongo import MongoClient
client = MongoClient('tu-connection-string')
print('Conexión exitosa:', client.admin.command('ping'))
"
```

### Verificar configuración

```bash
# Variables de Terraform
terraform output

# Variables de entorno de Lambda
aws lambda get-function-configuration --function-name boletin-oficial-analyzer

# Políticas IAM
aws iam list-attached-role-policies --role-name boletin-oficial-telegram-app-lambda-execution-role
```

## 🆘 Recuperación de Desastres

### 1. Restaurar desde backup

```bash
# Restaurar estado de Terraform
copy terraform.tfstate.backup terraform.tfstate

# Refrescar estado
terraform refresh
```

### 2. Recrear desde cero

```bash
# Destruir todo
destroy.bat /force

# Limpiar archivos locales
del lambda_deployment.zip
rmdir /s lambda_package

# Redesplegar
deploy.bat
```

### 3. Recuperar base de datos

```bash
# MongoDB Atlas tiene backups automáticos
# Ir a Atlas Console > Backup > Restore
```

## 📞 Obtener Ayuda

### Información para reportar problemas

Cuando reportes un problema, incluye:

1. **Información del sistema**:
```bash
python --version
terraform version
aws --version
```

2. **Logs relevantes**:
```bash
# Logs de Lambda
aws logs tail /aws/lambda/boletin-oficial-analyzer --since 1h

# Logs de Terraform
terraform plan -detailed-exitcode
```

3. **Configuración** (sin credenciales):
```bash
# Estado de Terraform
terraform show

# Variables (censuradas)
terraform output
```

4. **Pasos para reproducir** el problema

### Recursos adicionales

- [AWS Lambda Troubleshooting](https://docs.aws.amazon.com/lambda/latest/dg/troubleshooting.html)
- [Terraform Debugging](https://www.terraform.io/docs/internals/debugging.html)
- [MongoDB Atlas Support](https://docs.atlas.mongodb.com/troubleshoot-connection/)
- [Google Cloud API Troubleshooting](https://cloud.google.com/apis/docs/troubleshooting)

### Contacto

- **Issues**: Crear issue en el repositorio
- **Documentación**: Ver [README.md](README.md)

---

**Nota**: La mayoría de problemas se resuelven verificando credenciales, permisos y configuración. Siempre revisa los logs para obtener más información específica sobre el error.