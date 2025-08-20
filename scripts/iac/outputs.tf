# Lambda Function Outputs
output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.boletin_analyzer.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.boletin_analyzer.arn
}

output "lambda_function_version" {
  description = "Latest published version of the Lambda function"
  value       = aws_lambda_function.boletin_analyzer.version
}

# Lambda Function URL Outputs (replaces API Gateway)
output "lambda_function_url" {
  description = "Lambda Function URL (replaces API Gateway)"
  value       = aws_lambda_function_url.boletin_analyzer_url.function_url
}

output "lambda_function_url_id" {
  description = "Lambda Function URL ID"
  value       = aws_lambda_function_url.boletin_analyzer_url.url_id
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