# Project Structure

## Root Directory Layout

```
boletin-oficial-telegram-app/
├── lambda_function.py          # Main Lambda entry point
├── requirements.txt            # Python dependencies
├── requirements-test.txt       # Test-only dependencies
├── pytest.ini                 # Test configuration
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore patterns
├── README.md                  # Main documentation
├── API_DOCUMENTATION.md       # API reference
├── DEPLOYMENT_GUIDE.md        # Deployment instructions
├── TROUBLESHOOTING.md         # Common issues and solutions
├── services/                  # Business logic modules
├── utils/                     # Shared utilities
├── tests/                     # Test suite
├── scripts/                   # Build and deployment scripts
└── .kiro/                     # Kiro configuration
```

## Core Application Structure

### Main Entry Point
- `lambda_function.py`: AWS Lambda handler, request parsing, response formatting, service orchestration

### Service Layer (`services/`)
- `database_service.py`: MongoDB operations, connection pooling, data validation
- `llm_service_direct.py`: Direct Gemini integration, web access, prompt management
- `config_service.py`: Configuration management, environment variables
- `__init__.py`: Service module initialization

### Utilities (`utils/`)
- `error_handler.py`: Centralized error handling, logging, error codes
- `__init__.py`: Utility module initialization

### Testing (`tests/`)
- `test_database_service.py`: Database service unit tests
- `test_llm_service.py`: LLM service unit tests  
- `__init__.py`: Test module initialization

## Infrastructure & Scripts (`scripts/`)

### Infrastructure as Code (`scripts/iac/`)
- `main.tf`: Terraform main configuration
- `variables.tf`: Terraform variable definitions
- `outputs.tf`: Terraform output values
- `terraform.tfvars.example`: Configuration template
- `terraform.tfvars`: Actual configuration (gitignored)
- `README.md`: Infrastructure documentation

### Build & Deployment Scripts
- `scripts/setup.bat`: Initial project setup
- `build.bat`: Lambda package builder
- `deploy.bat`: Full deployment orchestrator
- `destroy.bat`: Infrastructure cleanup
- `test_dev.bat`: Development testing

## Configuration Files

### Python Configuration
- `requirements.txt`: Production dependencies only
- `requirements-test.txt`: Testing dependencies (pytest, mocks)
- `pytest.ini`: Test runner configuration, markers, paths

### Environment & Secrets
- `.env.example`: Template for local environment variables
- `scripts/iac/terraform.tfvars`: Infrastructure secrets and config
- Lambda environment variables: Runtime secrets (API keys, connection strings)

### Build Artifacts (Generated)
- `lambda_deployment.zip`: Deployment package
- `lambda_package/`: Temporary build directory
- `terraform.tfstate`: Infrastructure state file
- `.pytest_cache/`: Test cache directory

## Kiro Configuration (`.kiro/`)

### Steering Rules
- `.kiro/steering/product.md`: Product overview and purpose
- `.kiro/steering/tech.md`: Technology stack and build commands
- `.kiro/steering/structure.md`: Project organization (this file)

### Specifications
- `.kiro/specs/`: Feature specifications and requirements
- `.kiro/settings/`: Kiro-specific settings and configurations

## File Naming Conventions

### Python Files
- `snake_case.py` for all Python modules
- `test_*.py` for test files
- `__init__.py` for package initialization

### Scripts
- `*.bat` for Windows batch scripts
- `*.sh` for Unix shell scripts (where applicable)
- `*.tf` for Terraform configuration files

### Documentation
- `UPPERCASE.md` for major documentation files
- `lowercase.md` for supporting documentation
- `README.md` for directory-specific documentation

## Import Patterns

### Service Imports
```python
from services.database_service import MongoDBService
from services.llm_service import LLMAnalysisService
from services.pdf_scraper import BoletinWebAccessService
```

### Utility Imports
```python
from utils.error_handler import error_handler, ErrorCode
```

### Test Imports
```python
import pytest
from unittest.mock import Mock, patch
```

## Directory Responsibilities

### `/services/`
- Business logic implementation
- External service integrations
- Data processing and validation
- Service-specific error handling

### `/utils/`
- Cross-cutting concerns
- Shared utilities and helpers
- Common error handling
- Logging and monitoring utilities

### `/tests/`
- Unit tests for all modules
- Integration tests for service interactions
- Mock configurations and test data
- Test utilities and fixtures

### `/scripts/`
- Build automation
- Deployment orchestration
- Infrastructure management
- Development workflow tools