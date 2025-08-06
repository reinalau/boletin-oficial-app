# Project Configuration
variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "boletin-oficial-telegram-app"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

# AWS Configuration
variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

# Lambda Configuration
variable "lambda_function_name" {
  description = "Name of the Lambda function"
  type        = string
  default     = "boletin-oficial-analyzer"
}

variable "lambda_runtime" {
  description = "Runtime for Lambda function"
  type        = string
  default     = "python3.11"
}

variable "lambda_timeout" {
  description = "Timeout for Lambda function in seconds"
  type        = number
  default     = 300
}

variable "lambda_memory_size" {
  description = "Memory size for Lambda function in MB"
  type        = number
  default     = 1024
}

variable "lambda_zip_path" {
  description = "Path to the Lambda deployment package"
  type        = string
  default     = "lambda_deployment.zip"
}

variable "layer_zip_path" {
  description = "Path to the Lambda layer package"
  type        = string
  default     = "lambda_layer.zip"
}

# Environment Variables for Lambda
variable "google_api_key" {
  description = "Google Gemini API key (will be passed as GEMINI_API_KEY to Lambda)"
  type        = string
  sensitive   = true
}

variable "mongodb_connection_string" {
  description = "MongoDB Atlas connection string"
  type        = string
  sensitive   = true
}

variable "mongodb_database" {
  description = "MongoDB database name"
  type        = string
  default     = "BoletinOficial"
}

variable "mongodb_collection" {
  description = "MongoDB collection name"
  type        = string
  default     = "boletin-oficial"
}

variable "langchain_model" {
  description = "LangChain model to use"
  type        = string
  default     = "gemini-2.5-flash"
}

variable "langchain_temperature" {
  description = "Temperature setting for LangChain model"
  type        = string
  default     = "1"
}

variable "max_retry_attempts" {
  description = "Maximum retry attempts for operations"
  type        = string
  default     = "3"
}

variable "llm_request_timeout" {
  description = "Timeout for LLM requests in seconds"
  type        = string
  default     = "120"
}

# API Gateway Configuration
variable "api_gateway_name" {
  description = "Name of the API Gateway"
  type        = string
  default     = "boletin-oficial-api"
}

variable "api_gateway_description" {
  description = "Description of the API Gateway"
  type        = string
  default     = "API for Boletin Oficial Telegram App"
}

variable "api_gateway_stage_name" {
  description = "Stage name for API Gateway deployment"
  type        = string
  default     = "v1"
}

# Rate limiting configuration
variable "api_throttle_rate_limit" {
  description = "API Gateway throttle rate limit (requests per second)"
  type        = number
  default     = 100
}

variable "api_throttle_burst_limit" {
  description = "API Gateway throttle burst limit"
  type        = number
  default     = 200
}

# CORS Configuration
variable "cors_allowed_origins" {
  description = "List of allowed origins for CORS"
  type        = list(string)
  default     = ["*"]
}

variable "cors_allowed_methods" {
  description = "List of allowed HTTP methods for CORS"
  type        = list(string)
  default     = ["GET", "POST", "OPTIONS"]
}

variable "cors_allowed_headers" {
  description = "List of allowed headers for CORS"
  type        = list(string)
  default     = ["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key", "X-Amz-Security-Token"]
}

# Security Configuration
# Configuration is now passed via environment variables directly

# Tags
variable "additional_tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}

# VPC Configuration (optional)
variable "enable_vpc" {
  description = "Enable VPC configuration for Lambda"
  type        = bool
  default     = false
}

variable "vpc_id" {
  description = "VPC ID for Lambda function (required if enable_vpc is true)"
  type        = string
  default     = ""
}

variable "subnet_ids" {
  description = "Subnet IDs for Lambda function (required if enable_vpc is true)"
  type        = list(string)
  default     = []
}

# Security Configuration
variable "allowed_ip_ranges" {
  description = "List of allowed IP ranges for API Gateway access"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

# WAF Configuration (optional)
variable "enable_waf" {
  description = "Enable AWS WAF for API Gateway"
  type        = bool
  default     = false
}

variable "waf_rate_limit" {
  description = "Rate limit for WAF (requests per 5-minute period)"
  type        = number
  default     = 2000
}