# Infrastructure as Code (IaC) - Terraform

Esta carpeta contiene toda la configuración de infraestructura para el despliegue de la aplicación Boletín Oficial Telegram App en AWS usando Terraform.

## 📁 Estructura de Archivos

```
scripts/iac/
├── README.md                    # Este archivo
├── main.tf                      # Configuración principal de recursos AWS
├── variables.tf                 # Definición de variables de entrada
├── outputs.tf                   # Valores de salida después del despliegue
├── terraform.tfvars.example     # Plantilla de configuración
└── terraform.tfvars            # Configuración real (no incluido en git)
```

## 🏗️ Recursos de AWS Creados

### Core Infrastructure
- **AWS Lambda Function**: Función principal para análisis de normativa
- **Lambda Function URL**: Endpoint HTTPS directo (sin API Gateway)
- **IAM Roles & Policies**: Permisos y roles de seguridad
- **CloudWatch Log Groups**: Logging y monitoreo

### Security & Monitoring
- **WAF (opcional)**: Web Application Firewall para protección
- **VPC Configuration (opcional)**: Red privada virtual
- **X-Ray Tracing**: Trazabilidad de requests
- **CloudWatch Alarms**: Alertas de monitoreo

## ⚠️ Prerequisitos Importantes

**ANTES de ejecutar Terraform**, debes construir el paquete Lambda:

1. El archivo `lambda_deployment.zip` debe existir en la raíz del proyecto
2. Este archivo se crea ejecutando `build.bat` desde la raíz del proyecto
3. Terraform usa este ZIP pre-construido, no construye el paquete automáticamente

## 🚀 Uso Rápido

### 1. Configuración Inicial

```bash
# Desde la raíz del proyecto
cd scripts/iac

# Copiar plantilla de configuración
copy terraform.tfvars.example terraform.tfvars

# Editar con tus valores reales
notepad terraform.tfvars

# Configurar parámetros en AWS Systems Manager (OPCIONAL - script helper)
setup-parameters.bat
```

### 2. Construir el paquete Lambda

```bash
# Desde la raíz del proyecto (no desde scripts/iac)
cd ..\..\

# Construir el paquete de despliegue
build.bat
```

### 3. Despliegue

```bash
# Volver a la carpeta de Terraform
cd scripts/iac

# Inicializar Terraform
terraform init

# Planificar cambios
terraform plan -var-file="terraform.tfvars"

# Aplicar cambios
terraform apply -var-file="terraform.tfvars"
```

### 3. Verificar Despliegue

```bash
# Ver outputs importantes
terraform output

# Ver estado actual
terraform show
```

## 📋 Variables Requeridas

Las siguientes variables **DEBEN** ser configuradas en `terraform.tfvars`:

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `google_api_key` | API key de Google Gemini | `"AIzaSyC..."` |
| `mongodb_connection_string` | Connection string de MongoDB Atlas | `"mongodb+srv://..."` |
| `aws_region` | Región de AWS | `"us-east-1"` |

Ver `terraform.tfvars.example` para la lista completa de variables.

## 🔧 Configuraciones por Entorno

### Desarrollo
```hcl
environment = "dev"
lambda_memory_size = 512
lambda_timeout = 180
enable_waf = false
```

### Staging
```hcl
environment = "staging"
lambda_memory_size = 1024
lambda_timeout = 300
enable_waf = true
```

### Producción
```hcl
environment = "prod"
lambda_memory_size = 500
lambda_timeout = 360
langchain_temperature = "0"
llm_request_timeout = "360"
```

## 📊 Outputs Importantes

Después del despliegue, Terraform proporcionará:

- `lambda_function_url`: URL directa de la función Lambda
- `lambda_function_name`: Nombre de la función Lambda
- `lambda_function_arn`: ARN de la función Lambda

## 🔒 Seguridad

### Archivos Sensibles
- `terraform.tfvars` - **NUNCA** commitear al repositorio
- `terraform.tfstate` - Contiene información sensible
- `*.tfstate.backup` - Backups del estado

### Permisos AWS Requeridos
El usuario/rol de AWS necesita permisos para:
- Lambda (crear, actualizar, eliminar funciones y Function URLs)
- IAM (crear roles y políticas)
- CloudWatch (crear log groups)

## 🧹 Limpieza

### Eliminar Recursos
```bash
# Eliminar toda la infraestructura
terraform destroy -var-file="terraform.tfvars"

# Limpiar archivos locales
del terraform.tfstate*
del .terraform.lock.hcl
rmdir /s .terraform
```

## 🔄 Actualizaciones

### Actualizar Solo Lambda
```bash
# Cambiar solo el código de Lambda
terraform apply -target=aws_lambda_function.boletin_analyzer -var-file="terraform.tfvars"
```

### Actualizar Configuración
```bash
# Aplicar cambios en variables
terraform plan -var-file="terraform.tfvars"
terraform apply -var-file="terraform.tfvars"
```

## 🐛 Troubleshooting

### Problemas Comunes

1. **Error: "lambda_deployment.zip not found"**
   ```bash
   # Desde la raíz del proyecto
   cd ..\..\
   build.bat
   cd scripts\iac
   ```

2. **Error: "terraform.tfvars not found"**
   ```bash
   copy terraform.tfvars.example terraform.tfvars
   ```

3. **Error: "Invalid provider configuration"**
   ```bash
   terraform init -upgrade
   ```

4. **Error: "Resource already exists"**
   ```bash
   terraform import aws_lambda_function.boletin_analyzer nombre-funcion
   ```

5. **Error: "Lambda package too large"**
   ```bash
   # El paquete debe ser menor a 50MB
   # Revisar dependencias en requirements.txt
   # Ejecutar build.bat nuevamente
   ```

### Logs y Debugging
```bash
# Habilitar logs detallados
set TF_LOG=DEBUG
terraform apply -var-file="terraform.tfvars"

# Ver estado actual
terraform show

# Validar configuración
terraform validate
```

## 📚 Referencias

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Lambda with Terraform](https://learn.hashicorp.com/tutorials/terraform/lambda-api-gateway)
- [Terraform Best Practices](https://www.terraform.io/docs/cloud/guides/recommended-practices/index.html)

## 🔗 Enlaces Relacionados

- [Documentación Principal](../../README.md)
- [Guía de Despliegue](../../DEPLOYMENT_GUIDE.md)
- [Troubleshooting](../../TROUBLESHOOTING.md)
- [API Documentation](../../API_DOCUMENTATION.md)

---

**Nota**: Esta carpeta contiene solo la configuración de infraestructura. Para el despliegue completo (incluyendo build de Lambda), usar los scripts en la raíz del proyecto: `deploy.bat`, `build.bat`, etc.