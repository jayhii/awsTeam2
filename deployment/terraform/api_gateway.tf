# API Gateway

resource "aws_api_gateway_rest_api" "hr_api" {
  name        = "HR-Resource-Optimization-API"
  description = "인력 배치 최적화 시스템 REST API"
  
  endpoint_configuration {
    types = ["REGIONAL"]
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

# /recommendations resource
resource "aws_api_gateway_resource" "recommendations" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  parent_id   = aws_api_gateway_rest_api.hr_api.root_resource_id
  path_part   = "recommendations"
}

resource "aws_api_gateway_method" "recommendations_post" {
  rest_api_id   = aws_api_gateway_rest_api.hr_api.id
  resource_id   = aws_api_gateway_resource.recommendations.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "recommendations_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.hr_api.id
  resource_id             = aws_api_gateway_resource.recommendations.id
  http_method             = aws_api_gateway_method.recommendations_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.recommendation_engine.invoke_arn
}

resource "aws_lambda_permission" "api_gateway_recommendations" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.recommendation_engine.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.hr_api.execution_arn}/*/*"
}

# /domain-analysis resource
resource "aws_api_gateway_resource" "domain_analysis" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  parent_id   = aws_api_gateway_rest_api.hr_api.root_resource_id
  path_part   = "domain-analysis"
}

resource "aws_api_gateway_method" "domain_analysis_post" {
  rest_api_id   = aws_api_gateway_rest_api.hr_api.id
  resource_id   = aws_api_gateway_resource.domain_analysis.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "domain_analysis_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.hr_api.id
  resource_id             = aws_api_gateway_resource.domain_analysis.id
  http_method             = aws_api_gateway_method.domain_analysis_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.domain_analysis.invoke_arn
}

resource "aws_lambda_permission" "api_gateway_domain_analysis" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.domain_analysis.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.hr_api.execution_arn}/*/*"
}

# /quantitative-analysis resource
resource "aws_api_gateway_resource" "quantitative_analysis" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  parent_id   = aws_api_gateway_rest_api.hr_api.root_resource_id
  path_part   = "quantitative-analysis"
}

resource "aws_api_gateway_method" "quantitative_analysis_post" {
  rest_api_id   = aws_api_gateway_rest_api.hr_api.id
  resource_id   = aws_api_gateway_resource.quantitative_analysis.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "quantitative_analysis_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.hr_api.id
  resource_id             = aws_api_gateway_resource.quantitative_analysis.id
  http_method             = aws_api_gateway_method.quantitative_analysis_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.quantitative_analysis.invoke_arn
}

resource "aws_lambda_permission" "api_gateway_quantitative" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.quantitative_analysis.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.hr_api.execution_arn}/*/*"
}

# /qualitative-analysis resource
resource "aws_api_gateway_resource" "qualitative_analysis" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  parent_id   = aws_api_gateway_rest_api.hr_api.root_resource_id
  path_part   = "qualitative-analysis"
}

resource "aws_api_gateway_method" "qualitative_analysis_post" {
  rest_api_id   = aws_api_gateway_rest_api.hr_api.id
  resource_id   = aws_api_gateway_resource.qualitative_analysis.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "qualitative_analysis_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.hr_api.id
  resource_id             = aws_api_gateway_resource.qualitative_analysis.id
  http_method             = aws_api_gateway_method.qualitative_analysis_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.qualitative_analysis.invoke_arn
}

resource "aws_lambda_permission" "api_gateway_qualitative" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.qualitative_analysis.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.hr_api.execution_arn}/*/*"
}

# CORS configuration
resource "aws_api_gateway_method" "options" {
  for_each = {
    recommendations        = aws_api_gateway_resource.recommendations.id
    domain_analysis        = aws_api_gateway_resource.domain_analysis.id
    quantitative_analysis  = aws_api_gateway_resource.quantitative_analysis.id
    qualitative_analysis   = aws_api_gateway_resource.qualitative_analysis.id
  }
  
  rest_api_id   = aws_api_gateway_rest_api.hr_api.id
  resource_id   = each.value
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "options" {
  for_each = {
    recommendations        = aws_api_gateway_resource.recommendations.id
    domain_analysis        = aws_api_gateway_resource.domain_analysis.id
    quantitative_analysis  = aws_api_gateway_resource.quantitative_analysis.id
    qualitative_analysis   = aws_api_gateway_resource.qualitative_analysis.id
  }
  
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  resource_id = each.value
  http_method = "OPTIONS"
  type        = "MOCK"
  
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "options" {
  for_each = {
    recommendations        = aws_api_gateway_resource.recommendations.id
    domain_analysis        = aws_api_gateway_resource.domain_analysis.id
    quantitative_analysis  = aws_api_gateway_resource.quantitative_analysis.id
    qualitative_analysis   = aws_api_gateway_resource.qualitative_analysis.id
  }
  
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  resource_id = each.value
  http_method = "OPTIONS"
  status_code = "200"
  
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "options" {
  for_each = {
    recommendations        = aws_api_gateway_resource.recommendations.id
    domain_analysis        = aws_api_gateway_resource.domain_analysis.id
    quantitative_analysis  = aws_api_gateway_resource.quantitative_analysis.id
    qualitative_analysis   = aws_api_gateway_resource.qualitative_analysis.id
  }
  
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  resource_id = each.value
  http_method = "OPTIONS"
  status_code = "200"
  
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,POST,PUT,DELETE,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
  
  depends_on = [aws_api_gateway_integration.options]
}

# Deployment
resource "aws_api_gateway_deployment" "hr_api" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.recommendations.id,
      aws_api_gateway_method.recommendations_post.id,
      aws_api_gateway_integration.recommendations_lambda.id,
    ]))
  }
  
  lifecycle {
    create_before_destroy = true
  }
  
  depends_on = [
    aws_api_gateway_integration.recommendations_lambda,
    aws_api_gateway_integration.domain_analysis_lambda,
    aws_api_gateway_integration.quantitative_analysis_lambda,
    aws_api_gateway_integration.qualitative_analysis_lambda
  ]
}

# Stage
resource "aws_api_gateway_stage" "prod" {
  deployment_id = aws_api_gateway_deployment.hr_api.id
  rest_api_id   = aws_api_gateway_rest_api.hr_api.id
  stage_name    = var.environment
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

output "api_gateway_url" {
  value       = aws_api_gateway_stage.prod.invoke_url
  description = "API Gateway invoke URL"
}


# /employees resource
resource "aws_api_gateway_resource" "employees" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  parent_id   = aws_api_gateway_rest_api.hr_api.root_resource_id
  path_part   = "employees"
}

# GET /employees
resource "aws_api_gateway_method" "employees_get" {
  rest_api_id   = aws_api_gateway_rest_api.hr_api.id
  resource_id   = aws_api_gateway_resource.employees.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "employees_get_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.hr_api.id
  resource_id             = aws_api_gateway_resource.employees.id
  http_method             = aws_api_gateway_method.employees_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.employees_list.invoke_arn
}

resource "aws_lambda_permission" "api_gateway_employees_get" {
  statement_id  = "AllowAPIGatewayInvokeGet"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.employees_list.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.hr_api.execution_arn}/*/*"
}

# POST /employees
resource "aws_api_gateway_method" "employees_post" {
  rest_api_id   = aws_api_gateway_rest_api.hr_api.id
  resource_id   = aws_api_gateway_resource.employees.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "employees_post_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.hr_api.id
  resource_id             = aws_api_gateway_resource.employees.id
  http_method             = aws_api_gateway_method.employees_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.employee_create.invoke_arn
}

resource "aws_lambda_permission" "api_gateway_employees_post" {
  statement_id  = "AllowAPIGatewayInvokePost"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.employee_create.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.hr_api.execution_arn}/*/*"
}

# /projects resource
resource "aws_api_gateway_resource" "projects" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  parent_id   = aws_api_gateway_rest_api.hr_api.root_resource_id
  path_part   = "projects"
}

# GET /projects
resource "aws_api_gateway_method" "projects_get" {
  rest_api_id   = aws_api_gateway_rest_api.hr_api.id
  resource_id   = aws_api_gateway_resource.projects.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "projects_get_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.hr_api.id
  resource_id             = aws_api_gateway_resource.projects.id
  http_method             = aws_api_gateway_method.projects_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.projects_list.invoke_arn
}

resource "aws_lambda_permission" "api_gateway_projects_get" {
  statement_id  = "AllowAPIGatewayInvokeGet"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.projects_list.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.hr_api.execution_arn}/*/*"
}

# POST /projects
resource "aws_api_gateway_method" "projects_post" {
  rest_api_id   = aws_api_gateway_rest_api.hr_api.id
  resource_id   = aws_api_gateway_resource.projects.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "projects_post_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.hr_api.id
  resource_id             = aws_api_gateway_resource.projects.id
  http_method             = aws_api_gateway_method.projects_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.project_create.invoke_arn
}

resource "aws_lambda_permission" "api_gateway_projects_post" {
  statement_id  = "AllowAPIGatewayInvokePost"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.project_create.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.hr_api.execution_arn}/*/*"
}

# CORS for /employees
resource "aws_api_gateway_method" "employees_options" {
  rest_api_id   = aws_api_gateway_rest_api.hr_api.id
  resource_id   = aws_api_gateway_resource.employees.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "employees_options" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  resource_id = aws_api_gateway_resource.employees.id
  http_method = "OPTIONS"
  type        = "MOCK"
  
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "employees_options" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  resource_id = aws_api_gateway_resource.employees.id
  http_method = "OPTIONS"
  status_code = "200"
  
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "employees_options" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  resource_id = aws_api_gateway_resource.employees.id
  http_method = "OPTIONS"
  status_code = "200"
  
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
  
  depends_on = [aws_api_gateway_integration.employees_options]
}

# CORS for /projects
resource "aws_api_gateway_method" "projects_options" {
  rest_api_id   = aws_api_gateway_rest_api.hr_api.id
  resource_id   = aws_api_gateway_resource.projects.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "projects_options" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  resource_id = aws_api_gateway_resource.projects.id
  http_method = "OPTIONS"
  type        = "MOCK"
  
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "projects_options" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  resource_id = aws_api_gateway_resource.projects.id
  http_method = "OPTIONS"
  status_code = "200"
  
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "projects_options" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  resource_id = aws_api_gateway_resource.projects.id
  http_method = "OPTIONS"
  status_code = "200"
  
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
  
  depends_on = [aws_api_gateway_integration.projects_options]
}

# /dashboard/metrics resource
resource "aws_api_gateway_resource" "dashboard" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  parent_id   = aws_api_gateway_rest_api.hr_api.root_resource_id
  path_part   = "dashboard"
}

resource "aws_api_gateway_resource" "dashboard_metrics" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  parent_id   = aws_api_gateway_resource.dashboard.id
  path_part   = "metrics"
}

resource "aws_api_gateway_method" "dashboard_metrics_get" {
  rest_api_id   = aws_api_gateway_rest_api.hr_api.id
  resource_id   = aws_api_gateway_resource.dashboard_metrics.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "dashboard_metrics_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.hr_api.id
  resource_id             = aws_api_gateway_resource.dashboard_metrics.id
  http_method             = aws_api_gateway_method.dashboard_metrics_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.dashboard_metrics.invoke_arn
}

resource "aws_lambda_permission" "api_gateway_dashboard_metrics" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.dashboard_metrics.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.hr_api.execution_arn}/*/*"
}

# CORS for /dashboard/metrics
resource "aws_api_gateway_method" "dashboard_metrics_options" {
  rest_api_id   = aws_api_gateway_rest_api.hr_api.id
  resource_id   = aws_api_gateway_resource.dashboard_metrics.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "dashboard_metrics_options" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  resource_id = aws_api_gateway_resource.dashboard_metrics.id
  http_method = "OPTIONS"
  type        = "MOCK"
  
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "dashboard_metrics_options" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  resource_id = aws_api_gateway_resource.dashboard_metrics.id
  http_method = "OPTIONS"
  status_code = "200"
  
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "dashboard_metrics_options" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  resource_id = aws_api_gateway_resource.dashboard_metrics.id
  http_method = "OPTIONS"
  status_code = "200"
  
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
  
  depends_on = [aws_api_gateway_integration.dashboard_metrics_options]
}

# /projects/{projectId}/assign resource
resource "aws_api_gateway_resource" "project_id" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  parent_id   = aws_api_gateway_resource.projects.id
  path_part   = "{projectId}"
}

resource "aws_api_gateway_resource" "project_assign" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  parent_id   = aws_api_gateway_resource.project_id.id
  path_part   = "assign"
}

# POST /projects/{projectId}/assign
resource "aws_api_gateway_method" "project_assign_post" {
  rest_api_id   = aws_api_gateway_rest_api.hr_api.id
  resource_id   = aws_api_gateway_resource.project_assign.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "project_assign_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.hr_api.id
  resource_id             = aws_api_gateway_resource.project_assign.id
  http_method             = aws_api_gateway_method.project_assign_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.project_assign.invoke_arn
}

resource "aws_lambda_permission" "api_gateway_project_assign" {
  statement_id  = "AllowAPIGatewayInvokeAssign"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.project_assign.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.hr_api.execution_arn}/*/*"
}

# OPTIONS /projects/{projectId}/assign (CORS)
resource "aws_api_gateway_method" "project_assign_options" {
  rest_api_id   = aws_api_gateway_rest_api.hr_api.id
  resource_id   = aws_api_gateway_resource.project_assign.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "project_assign_options" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  resource_id = aws_api_gateway_resource.project_assign.id
  http_method = aws_api_gateway_method.project_assign_options.http_method
  type        = "MOCK"
  
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "project_assign_options" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  resource_id = aws_api_gateway_resource.project_assign.id
  http_method = aws_api_gateway_method.project_assign_options.http_method
  status_code = "200"
  
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "project_assign_options" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  resource_id = aws_api_gateway_resource.project_assign.id
  http_method = aws_api_gateway_method.project_assign_options.http_method
  status_code = "200"
  
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
  
  depends_on = [aws_api_gateway_integration.project_assign_options]
}

# /resume resource
resource "aws_api_gateway_resource" "resume" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  parent_id   = aws_api_gateway_rest_api.hr_api.root_resource_id
  path_part   = "resume"
}

resource "aws_api_gateway_resource" "resume_upload_url" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  parent_id   = aws_api_gateway_resource.resume.id
  path_part   = "upload-url"
}

# POST /resume/upload-url
resource "aws_api_gateway_method" "resume_upload_url_post" {
  rest_api_id   = aws_api_gateway_rest_api.hr_api.id
  resource_id   = aws_api_gateway_resource.resume_upload_url.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "resume_upload_url_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.hr_api.id
  resource_id             = aws_api_gateway_resource.resume_upload_url.id
  http_method             = aws_api_gateway_method.resume_upload_url_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.resume_upload.invoke_arn
}

resource "aws_lambda_permission" "api_gateway_resume_upload" {
  statement_id  = "AllowAPIGatewayInvokeResumeUpload"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.resume_upload.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.hr_api.execution_arn}/*/*"
}

# OPTIONS /resume/upload-url (CORS)
resource "aws_api_gateway_method" "resume_upload_url_options" {
  rest_api_id   = aws_api_gateway_rest_api.hr_api.id
  resource_id   = aws_api_gateway_resource.resume_upload_url.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "resume_upload_url_options" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  resource_id = aws_api_gateway_resource.resume_upload_url.id
  http_method = aws_api_gateway_method.resume_upload_url_options.http_method
  type        = "MOCK"
  
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "resume_upload_url_options" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  resource_id = aws_api_gateway_resource.resume_upload_url.id
  http_method = aws_api_gateway_method.resume_upload_url_options.http_method
  status_code = "200"
  
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "resume_upload_url_options" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  resource_id = aws_api_gateway_resource.resume_upload_url.id
  http_method = aws_api_gateway_method.resume_upload_url_options.http_method
  status_code = "200"
  
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
  
  depends_on = [aws_api_gateway_integration.resume_upload_url_options]
}

# /evaluations resource
resource "aws_api_gateway_resource" "evaluations" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  parent_id   = aws_api_gateway_rest_api.hr_api.root_resource_id
  path_part   = "evaluations"
}

# GET /evaluations
resource "aws_api_gateway_method" "evaluations_get" {
  rest_api_id   = aws_api_gateway_rest_api.hr_api.id
  resource_id   = aws_api_gateway_resource.evaluations.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "evaluations_get_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.hr_api.id
  resource_id             = aws_api_gateway_resource.evaluations.id
  http_method             = aws_api_gateway_method.evaluations_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.evaluations_list.invoke_arn
}

resource "aws_lambda_permission" "api_gateway_evaluations_get" {
  statement_id  = "AllowAPIGatewayInvokeEvaluationsGet"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.evaluations_list.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.hr_api.execution_arn}/*/*"
}

# /evaluations/{evaluationId} resource
resource "aws_api_gateway_resource" "evaluation_id" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  parent_id   = aws_api_gateway_resource.evaluations.id
  path_part   = "{evaluationId}"
}

# /evaluations/{evaluationId}/approve resource
resource "aws_api_gateway_resource" "evaluation_approve" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  parent_id   = aws_api_gateway_resource.evaluation_id.id
  path_part   = "approve"
}

# PUT /evaluations/{evaluationId}/approve
resource "aws_api_gateway_method" "evaluation_approve_put" {
  rest_api_id   = aws_api_gateway_rest_api.hr_api.id
  resource_id   = aws_api_gateway_resource.evaluation_approve.id
  http_method   = "PUT"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "evaluation_approve_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.hr_api.id
  resource_id             = aws_api_gateway_resource.evaluation_approve.id
  http_method             = aws_api_gateway_method.evaluation_approve_put.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.evaluation_status_update.invoke_arn
}

resource "aws_lambda_permission" "api_gateway_evaluation_approve" {
  statement_id  = "AllowAPIGatewayInvokeEvaluationApprove"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.evaluation_status_update.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.hr_api.execution_arn}/*/*"
}

# /evaluations/{evaluationId}/review resource
resource "aws_api_gateway_resource" "evaluation_review" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  parent_id   = aws_api_gateway_resource.evaluation_id.id
  path_part   = "review"
}

# PUT /evaluations/{evaluationId}/review
resource "aws_api_gateway_method" "evaluation_review_put" {
  rest_api_id   = aws_api_gateway_rest_api.hr_api.id
  resource_id   = aws_api_gateway_resource.evaluation_review.id
  http_method   = "PUT"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "evaluation_review_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.hr_api.id
  resource_id             = aws_api_gateway_resource.evaluation_review.id
  http_method             = aws_api_gateway_method.evaluation_review_put.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.evaluation_status_update.invoke_arn
}

resource "aws_lambda_permission" "api_gateway_evaluation_review" {
  statement_id  = "AllowAPIGatewayInvokeEvaluationReview"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.evaluation_status_update.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.hr_api.execution_arn}/*/*"
}

# /evaluations/{evaluationId}/reject resource
resource "aws_api_gateway_resource" "evaluation_reject" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  parent_id   = aws_api_gateway_resource.evaluation_id.id
  path_part   = "reject"
}

# PUT /evaluations/{evaluationId}/reject
resource "aws_api_gateway_method" "evaluation_reject_put" {
  rest_api_id   = aws_api_gateway_rest_api.hr_api.id
  resource_id   = aws_api_gateway_resource.evaluation_reject.id
  http_method   = "PUT"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "evaluation_reject_lambda" {
  rest_api_id             = aws_api_gateway_rest_api.hr_api.id
  resource_id             = aws_api_gateway_resource.evaluation_reject.id
  http_method             = aws_api_gateway_method.evaluation_reject_put.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.evaluation_status_update.invoke_arn
}

resource "aws_lambda_permission" "api_gateway_evaluation_reject" {
  statement_id  = "AllowAPIGatewayInvokeEvaluationReject"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.evaluation_status_update.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.hr_api.execution_arn}/*/*"
}

# CORS for /evaluations
resource "aws_api_gateway_method" "evaluations_options" {
  rest_api_id   = aws_api_gateway_rest_api.hr_api.id
  resource_id   = aws_api_gateway_resource.evaluations.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "evaluations_options" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  resource_id = aws_api_gateway_resource.evaluations.id
  http_method = "OPTIONS"
  type        = "MOCK"
  
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "evaluations_options" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  resource_id = aws_api_gateway_resource.evaluations.id
  http_method = "OPTIONS"
  status_code = "200"
  
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "evaluations_options" {
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  resource_id = aws_api_gateway_resource.evaluations.id
  http_method = "OPTIONS"
  status_code = "200"
  
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,PUT,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
  
  depends_on = [aws_api_gateway_integration.evaluations_options]
}

# CORS for evaluation actions (approve, review, reject)
resource "aws_api_gateway_method" "evaluation_actions_options" {
  for_each = {
    approve = aws_api_gateway_resource.evaluation_approve.id
    review  = aws_api_gateway_resource.evaluation_review.id
    reject  = aws_api_gateway_resource.evaluation_reject.id
  }
  
  rest_api_id   = aws_api_gateway_rest_api.hr_api.id
  resource_id   = each.value
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "evaluation_actions_options" {
  for_each = {
    approve = aws_api_gateway_resource.evaluation_approve.id
    review  = aws_api_gateway_resource.evaluation_review.id
    reject  = aws_api_gateway_resource.evaluation_reject.id
  }
  
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  resource_id = each.value
  http_method = "OPTIONS"
  type        = "MOCK"
  
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "evaluation_actions_options" {
  for_each = {
    approve = aws_api_gateway_resource.evaluation_approve.id
    review  = aws_api_gateway_resource.evaluation_review.id
    reject  = aws_api_gateway_resource.evaluation_reject.id
  }
  
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  resource_id = each.value
  http_method = "OPTIONS"
  status_code = "200"
  
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "evaluation_actions_options" {
  for_each = {
    approve = aws_api_gateway_resource.evaluation_approve.id
    review  = aws_api_gateway_resource.evaluation_review.id
    reject  = aws_api_gateway_resource.evaluation_reject.id
  }
  
  rest_api_id = aws_api_gateway_rest_api.hr_api.id
  resource_id = each.value
  http_method = "OPTIONS"
  status_code = "200"
  
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization'"
    "method.response.header.Access-Control-Allow-Methods" = "'PUT,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
  
  depends_on = [aws_api_gateway_integration.evaluation_actions_options]
}
