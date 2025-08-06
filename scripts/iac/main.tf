# Terraform configuration for Boletin Oficial Telegram App
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

# Lambda now uses environment variables directly, no need for Systems Manager access

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

  # VPC Configuration (conditional)
  dynamic "vpc_config" {
    for_each = var.enable_vpc ? [1] : []
    content {
      subnet_ids         = var.subnet_ids
      security_group_ids = [aws_security_group.lambda_sg[0].id]
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

# API Gateway REST API
resource "aws_api_gateway_rest_api" "boletin_api" {
  name        = var.api_gateway_name
  description = var.api_gateway_description

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = merge(
    {
      Name = var.api_gateway_name
    },
    var.additional_tags
  )
}

# API Gateway Resource for /analyze endpoint
resource "aws_api_gateway_resource" "analyze_resource" {
  rest_api_id = aws_api_gateway_rest_api.boletin_api.id
  parent_id   = aws_api_gateway_rest_api.boletin_api.root_resource_id
  path_part   = "analyze"
}

# API Gateway Method for POST /analyze
resource "aws_api_gateway_method" "analyze_post" {
  rest_api_id   = aws_api_gateway_rest_api.boletin_api.id
  resource_id   = aws_api_gateway_resource.analyze_resource.id
  http_method   = "POST"
  authorization = "NONE"

  request_parameters = {
    "method.request.header.Content-Type" = true
  }
}

# API Gateway Method for OPTIONS /analyze (CORS preflight)
resource "aws_api_gateway_method" "analyze_options" {
  rest_api_id   = aws_api_gateway_rest_api.boletin_api.id
  resource_id   = aws_api_gateway_resource.analyze_resource.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

# API Gateway Integration for POST /analyze with Lambda
resource "aws_api_gateway_integration" "analyze_lambda_integration" {
  rest_api_id = aws_api_gateway_rest_api.boletin_api.id
  resource_id = aws_api_gateway_resource.analyze_resource.id
  http_method = aws_api_gateway_method.analyze_post.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.boletin_analyzer.invoke_arn

  depends_on = [aws_api_gateway_method.analyze_post]
}

# API Gateway Integration for OPTIONS /analyze (CORS preflight)
resource "aws_api_gateway_integration" "analyze_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.boletin_api.id
  resource_id = aws_api_gateway_resource.analyze_resource.id
  http_method = aws_api_gateway_method.analyze_options.http_method

  type = "MOCK"

  request_templates = {
    "application/json" = jsonencode({
      statusCode = 200
    })
  }

  depends_on = [aws_api_gateway_method.analyze_options]
}

# API Gateway Method Response for POST /analyze
resource "aws_api_gateway_method_response" "analyze_post_200" {
  rest_api_id = aws_api_gateway_rest_api.boletin_api.id
  resource_id = aws_api_gateway_resource.analyze_resource.id
  http_method = aws_api_gateway_method.analyze_post.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"  = true
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
  }

  response_models = {
    "application/json" = "Empty"
  }
}

# API Gateway Method Response for OPTIONS /analyze (CORS)
resource "aws_api_gateway_method_response" "analyze_options_200" {
  rest_api_id = aws_api_gateway_rest_api.boletin_api.id
  resource_id = aws_api_gateway_resource.analyze_resource.id
  http_method = aws_api_gateway_method.analyze_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"  = true
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
  }

  response_models = {
    "application/json" = "Empty"
  }
}

# API Gateway Integration Response for POST /analyze
resource "aws_api_gateway_integration_response" "analyze_post_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.boletin_api.id
  resource_id = aws_api_gateway_resource.analyze_resource.id
  http_method = aws_api_gateway_method.analyze_post.http_method
  status_code = aws_api_gateway_method_response.analyze_post_200.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
    "method.response.header.Access-Control-Allow-Headers" = "'${join(",", var.cors_allowed_headers)}'"
    "method.response.header.Access-Control-Allow-Methods" = "'${join(",", var.cors_allowed_methods)}'"
  }

  depends_on = [aws_api_gateway_integration.analyze_lambda_integration]
}

# API Gateway Integration Response for OPTIONS /analyze (CORS)
resource "aws_api_gateway_integration_response" "analyze_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.boletin_api.id
  resource_id = aws_api_gateway_resource.analyze_resource.id
  http_method = aws_api_gateway_method.analyze_options.http_method
  status_code = aws_api_gateway_method_response.analyze_options_200.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
    "method.response.header.Access-Control-Allow-Headers" = "'${join(",", var.cors_allowed_headers)}'"
    "method.response.header.Access-Control-Allow-Methods" = "'${join(",", var.cors_allowed_methods)}'"
  }

  response_templates = {
    "application/json" = ""
  }

  depends_on = [aws_api_gateway_integration.analyze_options_integration]
}

# Lambda permission for API Gateway to invoke the function
resource "aws_lambda_permission" "api_gateway_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.boletin_analyzer.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.boletin_api.execution_arn}/*/*"
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "api_deployment" {
  depends_on = [
    aws_api_gateway_method.analyze_post,
    aws_api_gateway_method.analyze_options,
    aws_api_gateway_integration.analyze_lambda_integration,
    aws_api_gateway_integration.analyze_options_integration,
    aws_api_gateway_integration_response.analyze_post_integration_response,
    aws_api_gateway_integration_response.analyze_options_integration_response,
  ]

  rest_api_id = aws_api_gateway_rest_api.boletin_api.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.analyze_resource.id,
      aws_api_gateway_method.analyze_post.id,
      aws_api_gateway_method.analyze_options.id,
      aws_api_gateway_integration.analyze_lambda_integration.id,
      aws_api_gateway_integration.analyze_options_integration.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

# API Gateway Stage (for additional configuration)
resource "aws_api_gateway_stage" "api_stage" {
  deployment_id = aws_api_gateway_deployment.api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.boletin_api.id
  stage_name    = var.api_gateway_stage_name

  # Enable CloudWatch logging
  xray_tracing_enabled = true

  tags = merge(
    {
      Name = "${var.api_gateway_name}-${var.api_gateway_stage_name}"
    },
    var.additional_tags
  )
}

# API Gateway Method Settings for throttling
resource "aws_api_gateway_method_settings" "api_throttling" {
  rest_api_id = aws_api_gateway_rest_api.boletin_api.id
  stage_name  = aws_api_gateway_stage.api_stage.stage_name
  method_path = "*/*"

  settings {
    throttling_rate_limit  = var.api_throttle_rate_limit
    throttling_burst_limit = var.api_throttle_burst_limit
    logging_level          = "INFO"
    data_trace_enabled     = true
    metrics_enabled        = true
  }
}

# CloudWatch Log Group for API Gateway
resource "aws_cloudwatch_log_group" "api_gateway_logs" {
  name              = "API-Gateway-Execution-Logs_${aws_api_gateway_rest_api.boletin_api.id}/${var.api_gateway_stage_name}"
  retention_in_days = 14

  tags = merge(
    {
      Name = "${var.project_name}-api-gateway-logs"
    },
    var.additional_tags
  )
}

# API Gateway Account (for CloudWatch logging)
resource "aws_api_gateway_account" "api_gateway_account" {
  cloudwatch_role_arn = aws_iam_role.api_gateway_cloudwatch_role.arn
}

# IAM Role for API Gateway CloudWatch logging
resource "aws_iam_role" "api_gateway_cloudwatch_role" {
  name = "${var.project_name}-api-gateway-cloudwatch-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "apigateway.amazonaws.com"
        }
      }
    ]
  })

  tags = merge(
    {
      Name = "${var.project_name}-api-gateway-cloudwatch-role"
    },
    var.additional_tags
  )
}

# IAM Policy attachment for API Gateway CloudWatch logging
resource "aws_iam_role_policy_attachment" "api_gateway_cloudwatch" {
  role       = aws_iam_role.api_gateway_cloudwatch_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
}

# Environment variables are now passed directly to Lambda function

# IAM Policy for Lambda to access VPC (if needed)
resource "aws_iam_policy" "lambda_vpc_policy" {
  count       = var.enable_vpc ? 1 : 0
  name        = "${var.project_name}-lambda-vpc-policy"
  description = "Policy for Lambda to access VPC resources"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface",
          "ec2:AttachNetworkInterface",
          "ec2:DetachNetworkInterface"
        ]
        Resource = "*"
      }
    ]
  })

  tags = merge(
    {
      Name = "${var.project_name}-lambda-vpc-policy"
    },
    var.additional_tags
  )
}

# Attach VPC policy to Lambda role (if VPC is enabled)
resource "aws_iam_role_policy_attachment" "lambda_vpc_attachment" {
  count      = var.enable_vpc ? 1 : 0
  policy_arn = aws_iam_policy.lambda_vpc_policy[0].arn
  role       = aws_iam_role.lambda_execution_role.name
}

# Security Group for Lambda (if VPC is enabled)
resource "aws_security_group" "lambda_sg" {
  count       = var.enable_vpc ? 1 : 0
  name        = "${var.project_name}-lambda-sg"
  description = "Security group for Lambda function"
  vpc_id      = var.vpc_id

  # Outbound rules for HTTPS traffic (for API calls)
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS outbound for API calls"
  }

  # Outbound rules for HTTP traffic (if needed)
  egress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP outbound for web scraping"
  }

  # Outbound rules for MongoDB Atlas (port 27017)
  egress {
    from_port   = 27017
    to_port     = 27017
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "MongoDB Atlas connection"
  }

  tags = merge(
    {
      Name = "${var.project_name}-lambda-sg"
    },
    var.additional_tags
  )
}

# IAM Policy for enhanced security monitoring
resource "aws_iam_policy" "lambda_security_policy" {
  name        = "${var.project_name}-lambda-security-policy"
  description = "Enhanced security policy for Lambda function"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "cloudwatch:namespace" = "AWS/Lambda"
          }
        }
      }
    ]
  })

  tags = merge(
    {
      Name = "${var.project_name}-lambda-security-policy"
    },
    var.additional_tags
  )
}

# Attach security policy to Lambda role
resource "aws_iam_role_policy_attachment" "lambda_security_attachment" {
  policy_arn = aws_iam_policy.lambda_security_policy.arn
  role       = aws_iam_role.lambda_execution_role.name
}

# API Gateway Resource Policy for additional security
resource "aws_api_gateway_rest_api_policy" "api_policy" {
  rest_api_id = aws_api_gateway_rest_api.boletin_api.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = "*"
        Action = "execute-api:Invoke"
        Resource = "${aws_api_gateway_rest_api.boletin_api.execution_arn}/*"
        Condition = {
          IpAddress = {
            "aws:SourceIp" = var.allowed_ip_ranges
          }
        }
      }
    ]
  })
}

# WAF Web ACL for API Gateway (optional, for enhanced security)
resource "aws_wafv2_web_acl" "api_waf" {
  count = var.enable_waf ? 1 : 0
  name  = "${var.project_name}-api-waf"
  scope = "REGIONAL"

  default_action {
    allow {}
  }

  # Rate limiting rule
  rule {
    name     = "RateLimitRule"
    priority = 1

    override_action {
      none {}
    }

    statement {
      rate_based_statement {
        limit              = var.waf_rate_limit
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitRule"
      sampled_requests_enabled   = true
    }

    action {
      block {}
    }
  }

  # AWS Managed Rules - Core Rule Set
  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "CommonRuleSetMetric"
      sampled_requests_enabled   = true
    }
  }

  tags = merge(
    {
      Name = "${var.project_name}-api-waf"
    },
    var.additional_tags
  )

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.project_name}-api-waf"
    sampled_requests_enabled   = true
  }
}

# Associate WAF with API Gateway (if enabled)
resource "aws_wafv2_web_acl_association" "api_waf_association" {
  count        = var.enable_waf ? 1 : 0
  resource_arn = aws_api_gateway_stage.api_stage.arn
  web_acl_arn  = aws_wafv2_web_acl.api_waf[0].arn
}