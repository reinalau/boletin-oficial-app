# Lambda Layer Deployment Guide

Este documento explica cómo deployar la aplicación usando Lambda Layers para resolver conflictos de dependencias.

## ¿Por qué usar Lambda Layers?

Lambda Layers nos permiten:
- Separar las dependencias del código de la aplicación
- Resolver conflictos de versiones de librerías
- Reducir el tamaño del paquete de deployment
- Reutilizar dependencias entre múltiples funciones
- Mejorar los tiempos de deployment

## Estructura del Deployment

```
Deployment con Layers:
├── Lambda Layer (lambda_layer.zip)
│   └── python/
│       ├── google-generativeai
│       ├── pymongo
│       ├── requests
│       └── otras dependencias...
└── Lambda Function (lambda_deployment.zip)
    ├── lambda_function.py
    ├── services/
    └── utils/
```

## Scripts Disponibles

### 1. Construcción Individual

**Construir Layer:**
```cmd
.\build_layer_docker.ps1
```
- Crea `lambda_layer.zip` con todas las dependencias
- Estructura compatible con Lambda Layers (`python/` directory)

**Construir Función:**
```cmd
.\build_lambda_only.bat
```
- Crea `lambda_deployment.zip` solo con código de aplicación
- No incluye dependencias (las obtiene del layer)

### 2. Deployment Completo


## Configuración de Terraform

### Nuevos Recursos

**Lambda Layer:**
```hcl
resource "aws_lambda_layer_version" "dependencies_layer" {
  filename         = "lambda_layer.zip"
  layer_name       = "boletin-oficial-dependencies"
  description      = "Dependencies layer"
  compatible_runtimes = ["python3.11"]
}
```

**Lambda Function con Layer:**
```hcl
resource "aws_lambda_function" "boletin_analyzer" {
  # ... configuración existente ...
  layers = [aws_lambda_layer_version.dependencies_layer.arn]
}
```

### Variables Nuevas

```hcl
variable "layer_zip_path" {
  description = "Path to the Lambda layer package"
  type        = string
  default     = "lambda_layer.zip"
}
```

## Dependencias Resueltas

El layer incluye versiones específicas que resuelven conflictos:

```
google-generativeai==0.8.3
pydantic==2.5.3
rsa==4.7.2  # Compatible con AWS CLI
pymongo==4.6.0
requests==2.31.0
beautifulsoup4==4.12.0
python-dateutil==2.8.2
python-dotenv==1.0.0
```

## Proceso de Deployment

### 1. Preparación
```cmd
# Asegúrate de tener terraform.tfvars configurado
cd scripts/iac
cp terraform.tfvars.example terraform.tfvars
# Edita terraform.tfvars con tus valores
```
**Deploy con Layer en AWS (Backend Lambda):**
Se hace via terraform (corroborar todos los archivos necesarios)

```cmd
cd scripts/iac
terraform init
terraform validate
terraform plan -var-file="terraform.tfvars"
terraform apply -target="aws_lambda_function.boletin_analyzer" -var-file="terraform.tfvars" -auto-approve
```


### Tamaños Optimizados
- **Layer:** ~50MB (dependencias)
- **Función:** ~5KB (solo código)
- **Total:** Más eficiente que paquete monolítico

### Reutilización
- El layer puede ser usado por múltiples funciones
- Actualizaciones de dependencias independientes del código

## Troubleshooting

### Error: Layer not found
```
Error: Layer version not found
```
**Solución:** Asegúrate de que `lambda_layer.zip` existe antes del deployment.

### Error: Import module
```
ModuleNotFoundError: No module named 'google.generativeai'
```
**Solución:** Verifica que la función Lambda esté configurada para usar el layer.

### Error: Terraform plan fails
```
Error: file does not exist
```
**Solución:** Ejecuta `build_layer.bat` y `build_lambda_only.bat` antes de Terraform.

## Comandos de Desarrollo

### Testing Local
```cmd
# Instalar dependencias localmente para desarrollo
pip install -r requirements_prod.txt

# Probar función localmente
python tests/test_lambda_local.py
```

### Actualizar Dependencias
```cmd
# 1. Actualizar requirements_prod.txt
# 2. Reconstruir layer
build_layer.bat

# 3. Redeploy solo el layer
cd scripts/iac
terraform apply -target=aws_lambda_layer_version.dependencies_layer
```

### Logs y Monitoring
```cmd
# Ver logs de Lambda
aws logs tail /aws/lambda/boletin-oficial-analyzer --follow

# Ver métricas del layer
aws lambda get-layer-version --layer-name boletin-oficial-dependencies --version-number 1
```

