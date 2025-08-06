# Product Overview

## Boletín Oficial Telegram App

A serverless application that automatically analyzes legal regulations published in the "Legislación y Avisos Oficiales" section of Argentina's Official Bulletin using artificial intelligence.

### Core Purpose
- Analyzes legal regulations directly from the Official Bulletin website (https://www.boletinoficial.gob.ar/)
- Generates detailed analysis using Google Gemini LLM with direct web access
- Provides intelligent caching with MongoDB for fast responses
- Exposes REST API for integration with Telegram Mini Apps

### Key Features
- **Automated Analysis**: Processes Official Bulletin PDFs and extracts legal regulations
- **AI-Powered Insights**: Uses Google Gemini for detailed legal analysis
- **Smart Caching**: Stores previous analyses in MongoDB for quick retrieval
- **REST API**: HTTP interface for frontend integration
- **Serverless Architecture**: Scalable and cost-effective using AWS Lambda
- **Security**: Secure credential management via environment variables

### Target Users
- Legal professionals needing automated analysis of Argentine regulations
- Government agencies tracking regulatory changes
- Businesses monitoring compliance requirements
- Telegram Mini App users seeking accessible legal information

### Business Value
- Reduces manual effort in legal document analysis
- Provides timely insights on regulatory changes
- Enables automated compliance monitoring
- Democratizes access to legal information through AI