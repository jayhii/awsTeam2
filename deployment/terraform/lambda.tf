# Lambda Functions

# Lambda Layer for dependencies
resource "aws_lambda_layer_version" "boto3_layer" {
  filename   = "../../lambda_layers/boto3_layer.zip"
  layer_name = "boto3-layer-team2"
  
  compatible_runtimes = ["python3.11"]
  
  lifecycle {
    create_before_destroy = true
  }
}

# Resume Parser Lambda
resource "aws_lambda_function" "resume_parser" {
  filename      = "../../lambda_functions/resume_parser.zip"
  function_name = "ResumeParser"
  role          = aws_iam_role.lambda_execution_team2.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 300
  memory_size   = 1024
  
  layers = [aws_lambda_layer_version.boto3_layer.arn]
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

resource "aws_lambda_permission" "allow_s3_resume_parser" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.resume_parser.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.resumes.arn
}

# Affinity Score Calculator Lambda
resource "aws_lambda_function" "affinity_calculator" {
  filename      = "../../lambda_functions/affinity_calculator.zip"
  function_name = "AffinityScoreCalculator"
  role          = aws_iam_role.lambda_execution_team2.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 180
  memory_size   = 512
  
  layers = [aws_lambda_layer_version.boto3_layer.arn]
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

# EventBridge rule for daily affinity calculation
resource "aws_cloudwatch_event_rule" "daily_affinity_calculation" {
  name                = "daily-affinity-calculation-team2"
  description         = "Trigger affinity calculation daily"
  schedule_expression = "rate(1 day)"
  
  tags = {
    Team       = "Team2"
    EmployeeID = "524956"
    Project    = "HR-Resource-Optimization"
  }
}

resource "aws_cloudwatch_event_target" "affinity_calculator_target" {
  rule      = aws_cloudwatch_event_rule.daily_affinity_calculation.name
  target_id = "AffinityCalculatorTarget"
  arn       = aws_lambda_function.affinity_calculator.arn
}

resource "aws_lambda_permission" "allow_eventbridge_affinity" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.affinity_calculator.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_affinity_calculation.arn
}

# Project Recommendation Engine Lambda
resource "aws_lambda_function" "recommendation_engine" {
  filename      = "../../lambda_functions/recommendation_engine.zip"
  function_name = "ProjectRecommendationEngine"
  role          = aws_iam_role.lambda_execution_team2.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 300
  memory_size   = 2048
  
  layers = [aws_lambda_layer_version.boto3_layer.arn]
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

# Domain Analysis Engine Lambda
resource "aws_lambda_function" "domain_analysis" {
  filename      = "../../lambda_functions/domain_analysis.zip"
  function_name = "DomainAnalysisEngine"
  role          = aws_iam_role.lambda_execution_team2.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 300
  memory_size   = 1024
  
  layers = [aws_lambda_layer_version.boto3_layer.arn]
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

# Quantitative Analysis Lambda
resource "aws_lambda_function" "quantitative_analysis" {
  filename      = "../../lambda_functions/quantitative_analysis.zip"
  function_name = "QuantitativeAnalysis"
  role          = aws_iam_role.lambda_execution_team2.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 120
  memory_size   = 512
  
  layers = [aws_lambda_layer_version.boto3_layer.arn]
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

# Qualitative Analysis Lambda
resource "aws_lambda_function" "qualitative_analysis" {
  filename      = "../../lambda_functions/qualitative_analysis.zip"
  function_name = "QualitativeAnalysis"
  role          = aws_iam_role.lambda_execution_team2.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 180
  memory_size   = 1024
  
  layers = [aws_lambda_layer_version.boto3_layer.arn]
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

# Tech Trend Collector Lambda
resource "aws_lambda_function" "tech_trend_collector" {
  filename      = "../../lambda_functions/tech_trend_collector.zip"
  function_name = "TechTrendCollector"
  role          = aws_iam_role.lambda_execution_team2.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 180
  memory_size   = 512
  
  layers = [aws_lambda_layer_version.boto3_layer.arn]
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

# EventBridge rule for weekly tech trend collection
resource "aws_cloudwatch_event_rule" "weekly_tech_trends" {
  name                = "weekly-tech-trends-team2"
  description         = "Trigger tech trend collection weekly"
  schedule_expression = "rate(7 days)"
  
  tags = {
    Team       = "Team2"
    EmployeeID = "524956"
    Project    = "HR-Resource-Optimization"
  }
}

resource "aws_cloudwatch_event_target" "tech_trend_target" {
  rule      = aws_cloudwatch_event_rule.weekly_tech_trends.name
  target_id = "TechTrendTarget"
  arn       = aws_lambda_function.tech_trend_collector.arn
}

resource "aws_lambda_permission" "allow_eventbridge_tech_trends" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.tech_trend_collector.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.weekly_tech_trends.arn
}

# Vector Embedding Generator Lambda
resource "aws_lambda_function" "vector_embedding" {
  filename      = "../../lambda_functions/vector_embedding.zip"
  function_name = "VectorEmbeddingGenerator"
  role          = aws_iam_role.lambda_execution_team2.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 180
  memory_size   = 1024
  
  layers = [aws_lambda_layer_version.boto3_layer.arn]
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

# DynamoDB Stream event source mapping
resource "aws_lambda_event_source_mapping" "employees_stream" {
  event_source_arn  = aws_dynamodb_table.employees.stream_arn
  function_name     = aws_lambda_function.vector_embedding.arn
  starting_position = "LATEST"
}

# Variable for external API key
variable "external_api_key" {
  description = "External API key for tech trend collection"
  type        = string
  sensitive   = true
  default     = ""
}


# Employees List Lambda
resource "aws_lambda_function" "employees_list" {
  filename      = "../../lambda_functions/employees_list.zip"
  function_name = "EmployeesList"
  role          = aws_iam_role.lambda_execution_team2.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 30
  memory_size   = 256
  
  layers = [aws_lambda_layer_version.boto3_layer.arn]
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

# Employee Create Lambda
resource "aws_lambda_function" "employee_create" {
  filename      = "../../lambda_functions/employee_create.zip"
  function_name = "EmployeeCreate"
  role          = aws_iam_role.lambda_execution_team2.arn
  handler       = "index.lambda_handler"
  runtime       = "python3.11"
  timeout       = 30
  memory_size   = 512
  
  layers = [aws_lambda_layer_version.boto3_layer.arn]
  
  environment {
    variables = {
      EMPLOYEES_TABLE = aws_dynamodb_table.employees.name
    }
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

# Projects List Lambda
resource "aws_lambda_function" "projects_list" {
  filename      = "../../lambda_functions/projects_list.zip"
  function_name = "ProjectsList"
  role          = aws_iam_role.lambda_execution_team2.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 30
  memory_size   = 256
  
  layers = [aws_lambda_layer_version.boto3_layer.arn]
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

# Project Create Lambda
resource "aws_lambda_function" "project_create" {
  filename      = "../../lambda_functions/project_create.zip"
  function_name = "ProjectCreate"
  role          = aws_iam_role.lambda_execution_team2.arn
  handler       = "index.lambda_handler"
  runtime       = "python3.11"
  timeout       = 30
  memory_size   = 512
  
  layers = [aws_lambda_layer_version.boto3_layer.arn]
  
  environment {
    variables = {
      PROJECTS_TABLE = aws_dynamodb_table.projects.name
    }
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

# Dashboard Metrics Lambda
resource "aws_lambda_function" "dashboard_metrics" {
  filename      = "../../lambda_functions/dashboard_metrics.zip"
  function_name = "DashboardMetrics"
  role          = aws_iam_role.lambda_execution_team2.arn
  handler       = "index.lambda_handler"
  runtime       = "python3.11"
  timeout       = 30
  memory_size   = 512
  
  layers = [aws_lambda_layer_version.boto3_layer.arn]
  
  environment {
    variables = {
      EMPLOYEES_TABLE   = aws_dynamodb_table.employees.name
      PROJECTS_TABLE    = aws_dynamodb_table.projects.name
      EVALUATIONS_TABLE = "EmployeeEvaluations"
    }
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

# Project Assignment Lambda
resource "aws_lambda_function" "project_assign" {
  filename      = "../../lambda_functions/project_assign.zip"
  function_name = "ProjectAssignment"
  role          = aws_iam_role.lambda_execution_team2.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 60
  memory_size   = 512
  
  layers = [aws_lambda_layer_version.boto3_layer.arn]
  
  environment {
    variables = {
      EMPLOYEES_TABLE = aws_dynamodb_table.employees.name
      PROJECTS_TABLE  = aws_dynamodb_table.projects.name
    }
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

# Resume Upload URL Generator Lambda
resource "aws_lambda_function" "resume_upload" {
  filename      = "../../lambda_functions/resume_upload.zip"
  function_name = "ResumeUploadURLGenerator"
  role          = aws_iam_role.lambda_execution_team2.arn
  handler       = "index.lambda_handler"
  runtime       = "python3.11"
  timeout       = 30
  memory_size   = 256
  
  environment {
    variables = {
      RESUMES_BUCKET = aws_s3_bucket.resumes.id
    }
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

# Evaluations List Lambda
resource "aws_lambda_function" "evaluations_list" {
  filename      = "../../lambda_functions/evaluations_list.zip"
  function_name = "EvaluationsList"
  role          = aws_iam_role.lambda_execution_team2.arn
  handler       = "index.lambda_handler"
  runtime       = "python3.11"
  timeout       = 30
  memory_size   = 256
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

# Evaluation Status Update Lambda
resource "aws_lambda_function" "evaluation_status_update" {
  filename      = "../../lambda_functions/evaluation_status_update.zip"
  function_name = "EvaluationStatusUpdate"
  role          = aws_iam_role.lambda_execution_team2.arn
  handler       = "index.lambda_handler"
  runtime       = "python3.11"
  timeout       = 30
  memory_size   = 256
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}
