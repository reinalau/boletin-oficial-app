# Terraform configuration for Boletin Oficial with Lambda Function URLs (no API Gateway)
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}

# Data source for current AWS region
data "aws_region" "current" {}

# Use pre-built Lambda deployment package and layer
locals {
  lambda_zip_path = "${path.module}/../../${var.lambda_zip_path}"
  layer_zip_path  = "${path.module}/../../${var.layer_zip_path}"
}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.lambda_function_name}"
  retention_in_days = 3

  tags = merge(
    {
      Name = "${var.project_name}-lambda-logs"
    },
    var.additional_tags
  )
}

# IAM Role for Lambda execution
resource "aws_iam_role" "lambda_execution_role" {
  name = "${var.project_name}-lambda-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(
    {
      Name = "${var.project_name}-lambda-execution-role"
    },
    var.additional_tags
  )
}

# IAM Policy for Lambda basic execution
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_execution_role.name
}

# IAM Policy for Lambda CloudWatch Logs
resource "aws_iam_policy" "lambda_logs_policy" {
  name        = "${var.project_name}-lambda-logs-policy"
  description = "Policy for Lambda to write to CloudWatch Logs"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.lambda_logs.arn}:*"
      }
    ]
  })

  tags = merge(
    {
      Name = "${var.project_name}-lambda-logs-policy"
    },
    var.additional_tags
  )
}

# Attach CloudWatch Logs policy to Lambda role
resource "aws_iam_role_policy_attachment" "lambda_logs_attachment" {
  policy_arn = aws_iam_policy.lambda_logs_policy.arn
  role       = aws_iam_role.lambda_execution_role.name
}

# Lambda Layer for dependencies
resource "aws_lambda_layer_version" "dependencies_layer" {
  filename         = local.layer_zip_path
  layer_name       = "${var.project_name}-dependencies"
  description      = "Dependencies layer for ${var.project_name}"
  source_code_hash = filebase64sha256(local.layer_zip_path)

  compatible_runtimes = [var.lambda_runtime]
}

# Lambda Function
resource "aws_lambda_function" "boletin_analyzer" {
  filename         = local.lambda_zip_path
  function_name    = var.lambda_function_name
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "lambda_function.lambda_handler"
  runtime         = var.lambda_runtime
  timeout         = var.lambda_timeout
  memory_size     = var.lambda_memory_size
  source_code_hash = filebase64sha256(local.lambda_zip_path)

  # Use the dependencies layer
  layers = [aws_lambda_layer_version.dependencies_layer.arn]

  environment {
    variables = {
      # Direct environment variables
      GEMINI_API_KEY            = var.google_api_key
      MONGODB_CONNECTION_STRING = var.mongodb_connection_string
      MONGODB_DATABASE          = var.mongodb_database
      MONGODB_COLLECTION        = var.mongodb_collection
      # Non-sensitive configuration
      LANGCHAIN_MODEL           = var.langchain_model
      LANGCHAIN_TEMPERATURE     = var.langchain_temperature
      MAX_RETRY_ATTEMPTS        = var.max_retry_attempts
      LLM_REQUEST_TIMEOUT       = var.llm_request_timeout
    }
  }

  # Enable X-Ray tracing
  tracing_config {
    mode = "Active"
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic_execution,
    aws_iam_role_policy_attachment.lambda_logs_attachment,
    aws_cloudwatch_log_group.lambda_logs,
  ]

  tags = merge(
    {
      Name = var.lambda_function_name
    },
    var.additional_tags
  )
}

# Lambda Function URL (replaces API Gateway)
resource "aws_lambda_function_url" "boletin_analyzer_url" {
  function_name      = aws_lambda_function.boletin_analyzer.function_name
  authorization_type = "NONE"



  depends_on = [aws_lambda_function.boletin_analyzer]
}