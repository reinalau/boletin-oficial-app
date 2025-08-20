# Arquitectura Completa - AppBoletinOficial

## Diagrama de Arquitectura General

```mermaid
graph TB
    %% Frontend Layer
    subgraph "Frontend - Vercel"
        TMA[Telegram Mini App<br/>HTML/CSS/JS]
        UI[Interface de Usuario<br/>- Calendario<br/>- Visualización de análisis<br/>- Compartir resultados]
    end
    
    %% Telegram Integration
    subgraph "Telegram Platform"
        TB[Telegram Bot]
        TU[Usuario de Telegram]
    end
    
    %% API Layer
    subgraph "AWS Cloud"
        subgraph "AWS Lambda Function"
            LH[Lambda Handler<br/>lambda_function.py]
            LFU[Lambda Function URL<br/>- Direct HTTPS endpoint<br/>- CORS configured<br/>- No API Gateway needed]
            
            subgraph "Services Layer"
                PS[Web Access Service<br/>- Direct web access<br/>- Real-time content<br/>- No PDF download needed]
                LLM[LLM Analysis Service<br/>- Direct Gemini integration<br/>- Web access capability<br/>- Structured prompts]
                DB[MongoDB Service<br/>- CRUD operations<br/>- Connection pooling<br/>- Data validation]
                EH[Error Handler<br/>- Retry logic<br/>- Structured logging<br/>- Error codes]
            end
        end
    end
    
    %% External Services
    subgraph "External APIs"
        BO[Boletín Oficial<br/>otslist.boletinoficial.gob.ar<br/>- PDF downloads<br/>- Daily publications]
        GM[Google Gemini API<br/>- Text analysis<br/>- Expert opinions<br/>- Structured responses]
    end
    
    %% Database
    subgraph "MongoDB Atlas"
        MDB[(MongoDB Database<br/>Collection: boletin_analysis<br/>- Cached analyses<br/>- Expert opinions<br/>- Metadata)]
    end
    
    %% User Flow
    TU -->|Accede a Mini App| TB
    TB -->|Carga Mini App| TMA
    TMA -->|Interfaz de usuario| UI
    UI -->|Selecciona fecha| TMA
    
    %% API Communication
    TMA -->|HTTP POST| LFU
    LFU -->|Direct invoke| LH
    
    %% Service Orchestration
    LH -->|Coordina servicios| PS
    LH -->|Coordina servicios| LLM
    LH -->|Coordina servicios| DB
    LH -->|Manejo de errores| EH
    
    %% External Integrations
    PS -->|Descarga PDFs| BO
    LLM -->|Análisis de texto| GM
    DB -->|Almacena/Recupera| MDB
    
    %% Response Flow
    LH -->|JSON Response| LFU
    LFU -->|HTTP Response| TMA
    TMA -->|Muestra resultados| UI
    UI -->|Compartir| TB
    
    %% Styling
    classDef frontend fill:#e1f5fe
    classDef aws fill:#fff3e0
    classDef external fill:#f3e5f5
    classDef database fill:#e8f5e8
    classDef telegram fill:#fff8e1
    
    class TMA,UI frontend
    class LFU,LH,PS,LLM,DB,EH aws
    class BO,GM external
    class MDB database
    class TB,TU telegram
```

## Flujo de Datos Detallado

```mermaid
sequenceDiagram
    participant U as Usuario Telegram
    participant T as Telegram Mini App
    participant L as AWS Lambda
    participant F as Lambda Function URL
    participant S as PDF Scraper
    participant B as Boletín Oficial
    participant M as LLM Service
    participant G as Gemini API
    participant D as MongoDB
    
    U->>T: Abre Mini App
    T->>U: Muestra calendario
    U->>T: Selecciona fecha (ej: 2024-01-15)
    
    T->>F: POST {"fecha": "2024-01-15"}
    F->>L: Direct invocation
    
    L->>D: Verifica si existe análisis
    alt Análisis existe en cache
        D->>L: Retorna análisis existente
        L->>F: Respuesta con análisis cacheado
    else Análisis no existe
        L->>S: Solicita scraping de PDF
        S->>B: Busca PDF para fecha
        B->>S: Retorna URL del PDF
        S->>B: Descarga PDF
        B->>S: Contenido del PDF
        S->>L: Texto extraído de sección legislación
        
        L->>M: Solicita análisis de normativa
        M->>G: Envía texto para análisis
        G->>M: Retorna análisis estructurado
        M->>L: Análisis formateado
        
        L->>M: Solicita opiniones de expertos
        M->>G: Genera opiniones simuladas
        G->>M: Retorna opiniones
        M->>L: Opiniones formateadas
        
        L->>D: Guarda análisis completo
        D->>L: Confirmación de guardado
        L->>F: Respuesta con nuevo análisis
    end
    
    F->>T: JSON con análisis y opiniones
    T->>U: Muestra análisis formateado
    U->>T: Comparte resultados (opcional)
    T->>U: Opciones de compartir en Telegram
```

## Componentes Técnicos por Capa

### 1. Frontend (Vercel)
```
📱 Telegram Mini App
├── 📄 index.html (Interfaz principal)
├── 🎨 styles.css (Estilos responsivos)
├── ⚡ app.js (Lógica de la aplicación)
├── 📅 calendar.js (Componente calendario)
└── 🔗 telegram-web-app.js (SDK de Telegram)
```

### 2. Backend (AWS Lambda)
```
🚀 AWS Lambda Function
├── 📝 lambda_function.py (Handler principal)
├── 🔧 services/
│   ├── pdf_scraper.py (Scraping y PDF)
│   ├── llm_service.py (Direct Gemini + Web Access)
│   ├── database_service.py (MongoDB)
│   └── config_service.py (Configuración)
├── 🛠️ utils/
│   ├── error_handler.py (Manejo de errores)
│   └── validators.py (Validaciones)
└── 📋 requirements.txt (Dependencias)
```

### 3. Infraestructura (Terraform)
```
🏗️ Infrastructure as Code
├── 📄 main.tf (Recursos principales)
├── 🔧 variables.tf (Variables)
├── 📤 outputs.tf (Outputs)
└── 🔐 iam.tf (Roles y políticas)
```

## Tecnologías por Componente

| Componente | Tecnologías | Propósito |
|------------|-------------|-----------|
| **Frontend** | HTML5, CSS3, JavaScript, Telegram Web App SDK | Interfaz de usuario en Telegram |
| **Function URL** | AWS Lambda Function URL, HTTPS endpoint | Punto de entrada HTTP directo |
| **Backend** | Python 3.11, AWS Lambda | Lógica de negocio serverless |
| **Web Access** | Google Gemini Web Access | Acceso directo a contenido web |
| **AI Analysis** | Google Generative AI, Gemini API | Análisis inteligente con acceso web |
| **Database** | MongoDB Atlas, pymongo | Almacenamiento de análisis |
| **Infrastructure** | Terraform, AWS IAM | Infraestructura como código |
| **Deployment** | Vercel (frontend), AWS (backend) | Hosting y despliegue |

## Flujo de Desarrollo

```mermaid
graph LR
    A[1. Desarrollo Backend<br/>AWS Lambda] --> B[2. Testing Local<br/>Unit Tests]
    B --> C[3. Infraestructura<br/>Terraform]
    C --> D[4. Despliegue Backend<br/>AWS]
    D --> E[5. Desarrollo Frontend<br/>Mini App]
    E --> F[6. Integración<br/>API Testing]
    F --> G[7. Despliegue Frontend<br/>Vercel]
    G --> H[8. Testing E2E<br/>Telegram]
```

Este diagrama te muestra el objetivo completo del sistema que vamos a construir. El plan de tareas que creamos se enfoca principalmente en los pasos 1-4 (backend e infraestructura), que son la base fundamental para que después puedas desarrollar el frontend y completar la integración.

¿Te ayuda esta visualización a entender mejor hacia dónde vamos con el desarrollo?