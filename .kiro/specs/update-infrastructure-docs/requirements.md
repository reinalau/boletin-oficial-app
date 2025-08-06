# Requirements Document

## Introduction

Este proyecto necesita actualizar la documentación y configuración de infraestructura para reflejar los cambios arquitectónicos actuales. La aplicación ya no utiliza LangChain ni PDF scraping, sino que usa Google Gemini API directamente con acceso a URLs. Además, se requiere migrar de AWS Secrets Manager a AWS Systems Manager Parameter Store para reducir costos y simplificar la gestión de credenciales.

## Requirements

### Requirement 1

**User Story:** Como desarrollador, quiero que la documentación refleje la arquitectura actual sin LangChain y PDF scraping, para que otros desarrolladores entiendan correctamente cómo funciona el sistema.

#### Acceptance Criteria

1. WHEN se revise el README principal THEN SHALL eliminar todas las referencias a LangChain y PDF scraping
2. WHEN se actualice la documentación THEN SHALL reflejar que usa Google Gemini API directamente
3. WHEN se describa el flujo de análisis THEN SHALL indicar que accede directamente a URLs del Boletín Oficial
4. WHEN se listen las dependencias THEN SHALL mostrar solo las librerías actualmente utilizadas
5. WHEN se documente la arquitectura THEN SHALL reflejar el uso de `llm_service_direct.py` en lugar de `llm_service.py`

### Requirement 2

**User Story:** Como DevOps engineer, quiero migrar las credenciales de AWS Secrets Manager a AWS Systems Manager Parameter Store, para reducir costos y simplificar la gestión de configuración.

#### Acceptance Criteria

1. WHEN se configure Terraform THEN SHALL usar AWS Systems Manager Parameter Store en lugar de Secrets Manager
2. WHEN se almacenen credenciales THEN SHALL usar parámetros SecureString para datos sensibles
3. WHEN se configure Lambda THEN SHALL tener permisos para leer parámetros de Systems Manager
4. WHEN se actualice el código THEN SHALL leer credenciales desde Parameter Store
5. WHEN se compare el costo THEN SHALL ser significativamente menor que Secrets Manager
6. WHEN se organicen los parámetros THEN SHALL usar una estructura jerárquica clara (ej: /boletin-oficial/prod/google-api-key)

### Requirement 3

**User Story:** Como desarrollador, quiero que la documentación de Terraform esté actualizada con la nueva configuración de Systems Manager, para poder desplegar correctamente la infraestructura.

#### Acceptance Criteria

1. WHEN se revise main.tf THEN SHALL usar recursos de Systems Manager en lugar de Secrets Manager
2. WHEN se actualicen las variables THEN SHALL reflejar los nuevos parámetros de configuración
3. WHEN se actualice terraform.tfvars.example THEN SHALL mostrar la nueva estructura de configuración
4. WHEN se actualice el README de IaC THEN SHALL documentar el uso de Systems Manager
5. WHEN se listen los permisos IAM THEN SHALL incluir permisos para Systems Manager Parameter Store

### Requirement 4

**User Story:** Como desarrollador, quiero que el servicio de configuración lea credenciales desde Systems Manager Parameter Store, para mantener la seguridad y reducir la complejidad.

#### Acceptance Criteria

1. WHEN se actualice config_service.py THEN SHALL leer parámetros desde Systems Manager
2. WHEN se manejen errores THEN SHALL tener retry logic para fallos de conexión a Systems Manager
3. WHEN se cacheen credenciales THEN SHALL implementar cache local temporal para mejorar performance
4. WHEN se inicialice la aplicación THEN SHALL validar que todos los parámetros requeridos estén disponibles
5. WHEN se ejecute en Lambda THEN SHALL usar el SDK de AWS para acceder a Parameter Store

### Requirement 5

**User Story:** Como desarrollador, quiero que la documentación de despliegue esté actualizada con los nuevos procesos, para poder desplegar y mantener la aplicación correctamente.

#### Acceptance Criteria

1. WHEN se actualice DEPLOYMENT_GUIDE.md THEN SHALL reflejar el uso de Systems Manager
2. WHEN se documenten los scripts de build THEN SHALL mostrar los comandos actualizados
3. WHEN se listen los prerequisitos THEN SHALL incluir la configuración de Parameter Store
4. WHEN se documente troubleshooting THEN SHALL incluir problemas comunes con Systems Manager
5. WHEN se actualicen los ejemplos THEN SHALL mostrar cómo configurar parámetros en AWS Console

### Requirement 6

**User Story:** Como desarrollador, quiero que la documentación técnica refleje la arquitectura actual simplificada, para facilitar el mantenimiento y onboarding de nuevos desarrolladores.

#### Acceptance Criteria

1. WHEN se actualice la documentación técnica THEN SHALL eliminar referencias a servicios no utilizados
2. WHEN se describan los servicios THEN SHALL enfocarse en database_service, llm_service_direct y config_service
3. WHEN se documenten las APIs THEN SHALL reflejar solo los endpoints actualmente implementados
4. WHEN se listen las tecnologías THEN SHALL mostrar solo las librerías y servicios en uso
5. WHEN se actualicen los diagramas THEN SHALL reflejar el flujo simplificado actual