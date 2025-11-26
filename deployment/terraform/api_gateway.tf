# API Gateway

resource "aws_api_gateway_rest_api" "hr_api" {
  name        = "HR-Resource-Optimization-API"
  description = "인력 배치 최적화 시스템 REST API"
  
  endpoint_configuration {
    types = ["REGIONAL"]
  }
  
  tags = {
    Team        = "Team2"
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
  authorization = "AWS_IAM"
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
  authorization = "AWS_IAM"
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
  authorization = "AWS_IAM"
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
  authorization = "AWS_IAM"
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
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

output "api_gateway_url" {
  value       = aws_api_gateway_stage.prod.invoke_url
  description = "API Gateway invoke URL"
}
