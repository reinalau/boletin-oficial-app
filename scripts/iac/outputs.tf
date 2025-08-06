# Lambda Function Outputs
output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.boletin_analyzer.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.boletin_analyzer.arn
}

output "lambda_function_invoke_arn" {
  description = "Invoke ARN of the Lambda function"
  value       = aws_lambda_function.boletin_analyzer.invoke_arn
}

output "lambda_function_version" {
  description = "Latest published version of the Lambda function"
  value       = aws_lambda_function.boletin_analyzer.version
}

# Lambda Layer Outputs
output "lambda_layer_arn" {
  description = "ARN of the Lambda layer"
  value       = aws_lambda_layer_version.dependencies_layer.arn
}

output "lambda_layer_version" {
  description = "Version of the Lambda layer"
  value       = aws_lambda_layer_version.dependencies_layer.version
}

# IAM Role Outputs
output "lambda_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_execution_role.arn
}

output "lambda_role_name" {
  description = "Name of the Lambda execution role"
  value       = aws_iam_role.lambda_execution_role.name
}

# API Gateway Outputs
output "api_gateway_id" {
  description = "ID of the API Gateway"
  value       = aws_api_gateway_rest_api.boletin_api.id
}

output "api_gateway_root_resource_id" {
  description = "Root resource ID of the API Gateway"
  value       = aws_api_gateway_rest_api.boletin_api.root_resource_id
}

output "api_gateway_execution_arn" {
  description = "Execution ARN of the API Gateway"
  value       = aws_api_gateway_rest_api.boletin_api.execution_arn
}

output "api_gateway_url" {
  description = "URL of the deployed API Gateway"
  value       = "https://${aws_api_gateway_rest_api.boletin_api.id}.execute-api.${var.aws_region}.amazonaws.com/${var.api_gateway_stage_name}"
}

output "api_gateway_stage_name" {
  description = "Stage name of the API Gateway deployment"
  value       = aws_api_gateway_stage.api_stage.stage_name
}

# API Gateway Resource Outputs
output "analyze_resource_id" {
  description = "ID of the /analyze resource"
  value       = aws_api_gateway_resource.analyze_resource.id
}

output "analyze_endpoint_url" {
  description = "Full URL of the analyze endpoint"
  value       = "https://${aws_api_gateway_rest_api.boletin_api.id}.execute-api.${var.aws_region}.amazonaws.com/${var.api_gateway_stage_name}/analyze"
}

# Configuration is now passed via environment variables directly to Lambda

# CloudWatch Log Group Outputs
output "lambda_log_group_name" {
  description = "Name of the Lambda CloudWatch log group"
  value       = aws_cloudwatch_log_group.lambda_logs.name
}

output "lambda_log_group_arn" {
  description = "ARN of the Lambda CloudWatch log group"
  value       = aws_cloudwatch_log_group.lambda_logs.arn
}

# General Information Outputs
output "aws_region" {
  description = "AWS region where resources are deployed"
  value       = var.aws_region
}

output "aws_account_id" {
  description = "AWS account ID"
  value       = data.aws_caller_identity.current.account_id
}

output "project_name" {
  description = "Project name"
  value       = var.project_name
}

output "environment" {
  description = "Environment name"
  value       = var.environment
}