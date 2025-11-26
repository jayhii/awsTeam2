# Terraform Outputs

# DynamoDB Tables
output "dynamodb_tables" {
  description = "DynamoDB table names"
  value = {
    employees        = aws_dynamodb_table.employees.name
    projects         = aws_dynamodb_table.projects.name
    employee_affinity = aws_dynamodb_table.employee_affinity.name
    messenger_logs   = aws_dynamodb_table.messenger_logs.name
    company_events   = aws_dynamodb_table.company_events.name
    tech_trends      = aws_dynamodb_table.tech_trends.name
  }
}

output "dynamodb_table_arns" {
  description = "DynamoDB table ARNs"
  value = {
    employees        = aws_dynamodb_table.employees.arn
    projects         = aws_dynamodb_table.projects.arn
    employee_affinity = aws_dynamodb_table.employee_affinity.arn
    messenger_logs   = aws_dynamodb_table.messenger_logs.arn
    company_events   = aws_dynamodb_table.company_events.arn
    tech_trends      = aws_dynamodb_table.tech_trends.arn
  }
}

# S3 Buckets
output "s3_buckets" {
  description = "S3 bucket names"
  value = {
    frontend_hosting = aws_s3_bucket.frontend_hosting.bucket
    resumes          = aws_s3_bucket.resumes.bucket
    reports          = aws_s3_bucket.reports.bucket
    data_lake        = aws_s3_bucket.data_lake.bucket
  }
}

output "s3_bucket_arns" {
  description = "S3 bucket ARNs"
  value = {
    frontend_hosting = aws_s3_bucket.frontend_hosting.arn
    resumes          = aws_s3_bucket.resumes.arn
    reports          = aws_s3_bucket.reports.arn
    data_lake        = aws_s3_bucket.data_lake.arn
  }
}

# IAM Roles
output "iam_roles" {
  description = "IAM role names"
  value = {
    lambda_execution     = aws_iam_role.lambda_execution_team2.name
    api_gateway_execution = aws_iam_role.api_gateway_execution_team2.name
  }
}

output "iam_role_arns" {
  description = "IAM role ARNs"
  value = {
    lambda_execution     = aws_iam_role.lambda_execution_team2.arn
    api_gateway_execution = aws_iam_role.api_gateway_execution_team2.arn
  }
}

# Employees Table Stream
output "employees_stream_arn" {
  description = "Employees table DynamoDB stream ARN"
  value       = aws_dynamodb_table.employees.stream_arn
}
