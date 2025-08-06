# Technology Stack

## Core Technologies

### Backend & Runtime
- **Python 3.11+**: Primary programming language
- **AWS Lambda**: Serverless compute platform
- **API Gateway**: REST API management and routing

### AI & Language Models
- **Google Gemini**: Primary LLM for legal analysis with direct web access (gemini-2.5-flash)
- **Google Generative AI**: Python SDK for direct Gemini integration
- **Web Access**: Direct access to https://www.boletinoficial.gob.ar/ for real-time analysis

### Database & Storage
- **MongoDB Atlas**: Document database for analysis caching

### Web Access & Content Processing
- **Google Gemini Web Access**: Direct access to Official Bulletin website
- **Real-time Analysis**: No PDF download required, direct web content analysis
- **requests**: HTTP client for fallback web scraping (if needed)

### Infrastructure as Code
- **Terraform**: Infrastructure provisioning and management
- **AWS CLI**: Command-line interface for AWS services

### Testing & Development
- **pytest**: Testing framework
- **pytest-mock**: Mocking for unit tests
- **mongomock**: MongoDB mocking for tests
- **python-dotenv**: Environment variable management

## Build System & Commands

### Core Build Commands
```bash
# Build Lambda deployment package
build.bat

# Full deployment (build + infrastructure)
deploy.bat

# Setup project after cloning
scripts\setup.bat

# Run tests
pytest tests/ -v

# Test API endpoints
python test_api.py [API_URL]
```

### Development Workflow
```bash
# Install dependencies
pip install -r requirements.txt

# Run unit tests with coverage
pytest tests/ --cov=services --cov=utils

# Build and test locally
build.bat
python test_api.py

# Deploy to AWS
deploy.bat
```

### Infrastructure Management
```bash
# Initialize Terraform
cd scripts\iac
terraform init

# Plan deployment
terraform plan -var-file="terraform.tfvars"

# Apply changes
terraform apply -var-file="terraform.tfvars"

# Destroy infrastructure
terraform destroy -var-file="terraform.tfvars"
```

## Configuration Files

### Essential Config Files
- `requirements.txt`: Python dependencies
- `scripts/iac/terraform.tfvars`: Infrastructure configuration
- `pytest.ini`: Test configuration
- `.env`: Local environment variables (optional)

### Build Artifacts
- `lambda_deployment.zip`: Lambda deployment package
- `lambda_package/`: Temporary build directory
- `terraform.tfstate`: Infrastructure state (sensitive)

## Environment Requirements

### Development Prerequisites
- Python 3.11+
- pip (Python package manager)
- Terraform 1.0+
- AWS CLI (optional but recommended)

### Cloud Services Required
- AWS Account with Lambda, API Gateway, IAM permissions
- Google Cloud Account with Gemini API access
- MongoDB Atlas cluster (free tier available)

## Architecture Patterns

### Service Layer Pattern
- `services/`: Business logic modules
- `utils/`: Shared utilities and error handling
- `lambda_function.py`: Main entry point and orchestration

### Error Handling
- Centralized error handling via `utils/error_handler.py`
- Structured error codes and HTTP status mapping
- Comprehensive logging with CloudWatch integration

### Configuration Management
- Environment-based configuration via Lambda environment variables
- Terraform variables for infrastructure settings