# CloudWatch Monitoring and Alerting

# SNS Topic for Alarms
resource "aws_sns_topic" "hr_alarms" {
  name = "hr-resource-optimization-alarms-team2"
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

# SNS Topic Subscription (이메일 주소는 배포 시 수동으로 확인 필요)
resource "aws_sns_topic_subscription" "alarm_email" {
  count     = length(var.alarm_email_addresses)
  topic_arn = aws_sns_topic.hr_alarms.arn
  protocol  = "email"
  endpoint  = var.alarm_email_addresses[count.index]
}

# Variable for email addresses
variable "alarm_email_addresses" {
  description = "Email addresses for alarm notifications"
  type        = list(string)
  default     = []
}

# CloudWatch Dashboard for Lambda Metrics
resource "aws_cloudwatch_dashboard" "lambda_metrics" {
  dashboard_name = "HR-Lambda-Metrics-Team2"
  
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/Lambda", "Invocations", { stat = "Sum", label = "Resume Parser" }, { dimensions = { FunctionName = aws_lambda_function.resume_parser.function_name } }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.affinity_calculator.function_name }, label = "Affinity Calculator" }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.recommendation_engine.function_name }, label = "Recommendation Engine" }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.domain_analysis.function_name }, label = "Domain Analysis" }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.quantitative_analysis.function_name }, label = "Quantitative Analysis" }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.qualitative_analysis.function_name }, label = "Qualitative Analysis" }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.tech_trend_collector.function_name }, label = "Tech Trend Collector" }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.vector_embedding.function_name }, label = "Vector Embedding" }]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "Lambda Invocations"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/Lambda", "Errors", { stat = "Sum", label = "Resume Parser" }, { dimensions = { FunctionName = aws_lambda_function.resume_parser.function_name } }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.affinity_calculator.function_name }, label = "Affinity Calculator" }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.recommendation_engine.function_name }, label = "Recommendation Engine" }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.domain_analysis.function_name }, label = "Domain Analysis" }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.quantitative_analysis.function_name }, label = "Quantitative Analysis" }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.qualitative_analysis.function_name }, label = "Qualitative Analysis" }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.tech_trend_collector.function_name }, label = "Tech Trend Collector" }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.vector_embedding.function_name }, label = "Vector Embedding" }]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "Lambda Errors"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/Lambda", "Duration", { stat = "Average", label = "Resume Parser" }, { dimensions = { FunctionName = aws_lambda_function.resume_parser.function_name } }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.affinity_calculator.function_name }, label = "Affinity Calculator" }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.recommendation_engine.function_name }, label = "Recommendation Engine" }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.domain_analysis.function_name }, label = "Domain Analysis" }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.quantitative_analysis.function_name }, label = "Quantitative Analysis" }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.qualitative_analysis.function_name }, label = "Qualitative Analysis" }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.tech_trend_collector.function_name }, label = "Tech Trend Collector" }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.vector_embedding.function_name }, label = "Vector Embedding" }]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "Lambda Duration (ms)"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/Lambda", "Throttles", { stat = "Sum", label = "Resume Parser" }, { dimensions = { FunctionName = aws_lambda_function.resume_parser.function_name } }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.affinity_calculator.function_name }, label = "Affinity Calculator" }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.recommendation_engine.function_name }, label = "Recommendation Engine" }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.domain_analysis.function_name }, label = "Domain Analysis" }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.quantitative_analysis.function_name }, label = "Quantitative Analysis" }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.qualitative_analysis.function_name }, label = "Qualitative Analysis" }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.tech_trend_collector.function_name }, label = "Tech Trend Collector" }],
            ["...", { dimensions = { FunctionName = aws_lambda_function.vector_embedding.function_name }, label = "Vector Embedding" }]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "Lambda Throttles"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
      }
    ]
  })
}

# CloudWatch Dashboard for API Gateway Metrics
resource "aws_cloudwatch_dashboard" "api_gateway_metrics" {
  dashboard_name = "HR-API-Gateway-Metrics-Team2"
  
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/ApiGateway", "Count", { stat = "Sum" }, { dimensions = { ApiName = aws_api_gateway_rest_api.hr_api.name } }]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "API Gateway Request Count"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/ApiGateway", "4XXError", { stat = "Sum" }, { dimensions = { ApiName = aws_api_gateway_rest_api.hr_api.name } }],
            [".", "5XXError", { stat = "Sum" }, { dimensions = { ApiName = aws_api_gateway_rest_api.hr_api.name } }]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "API Gateway Errors"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/ApiGateway", "Latency", { stat = "Average" }, { dimensions = { ApiName = aws_api_gateway_rest_api.hr_api.name } }],
            [".", "IntegrationLatency", { stat = "Average" }, { dimensions = { ApiName = aws_api_gateway_rest_api.hr_api.name } }]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "API Gateway Latency (ms)"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
      }
    ]
  })
}

# CloudWatch Dashboard for DynamoDB Metrics
resource "aws_cloudwatch_dashboard" "dynamodb_metrics" {
  dashboard_name = "HR-DynamoDB-Metrics-Team2"
  
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/DynamoDB", "ConsumedReadCapacityUnits", { stat = "Sum", label = "Employees" }, { dimensions = { TableName = aws_dynamodb_table.employees.name } }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.projects.name }, label = "Projects" }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.employee_affinity.name }, label = "Employee Affinity" }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.messenger_logs.name }, label = "Messenger Logs" }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.company_events.name }, label = "Company Events" }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.tech_trends.name }, label = "Tech Trends" }]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "DynamoDB Read Capacity Units"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/DynamoDB", "ConsumedWriteCapacityUnits", { stat = "Sum", label = "Employees" }, { dimensions = { TableName = aws_dynamodb_table.employees.name } }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.projects.name }, label = "Projects" }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.employee_affinity.name }, label = "Employee Affinity" }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.messenger_logs.name }, label = "Messenger Logs" }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.company_events.name }, label = "Company Events" }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.tech_trends.name }, label = "Tech Trends" }]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "DynamoDB Write Capacity Units"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/DynamoDB", "UserErrors", { stat = "Sum", label = "Employees" }, { dimensions = { TableName = aws_dynamodb_table.employees.name } }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.projects.name }, label = "Projects" }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.employee_affinity.name }, label = "Employee Affinity" }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.messenger_logs.name }, label = "Messenger Logs" }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.company_events.name }, label = "Company Events" }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.tech_trends.name }, label = "Tech Trends" }]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "DynamoDB User Errors"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/DynamoDB", "SystemErrors", { stat = "Sum", label = "Employees" }, { dimensions = { TableName = aws_dynamodb_table.employees.name } }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.projects.name }, label = "Projects" }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.employee_affinity.name }, label = "Employee Affinity" }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.messenger_logs.name }, label = "Messenger Logs" }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.company_events.name }, label = "Company Events" }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.tech_trends.name }, label = "Tech Trends" }]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "DynamoDB System Errors"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/DynamoDB", "ReadThrottleEvents", { stat = "Sum", label = "Employees" }, { dimensions = { TableName = aws_dynamodb_table.employees.name } }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.projects.name }, label = "Projects" }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.employee_affinity.name }, label = "Employee Affinity" }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.messenger_logs.name }, label = "Messenger Logs" }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.company_events.name }, label = "Company Events" }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.tech_trends.name }, label = "Tech Trends" }]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "DynamoDB Read Throttle Events"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/DynamoDB", "WriteThrottleEvents", { stat = "Sum", label = "Employees" }, { dimensions = { TableName = aws_dynamodb_table.employees.name } }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.projects.name }, label = "Projects" }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.employee_affinity.name }, label = "Employee Affinity" }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.messenger_logs.name }, label = "Messenger Logs" }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.company_events.name }, label = "Company Events" }],
            ["...", { dimensions = { TableName = aws_dynamodb_table.tech_trends.name }, label = "Tech Trends" }]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "DynamoDB Write Throttle Events"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
      }
    ]
  })
}

# CloudWatch Alarms

# Lambda Error Rate Alarms
resource "aws_cloudwatch_metric_alarm" "lambda_errors_resume_parser" {
  alarm_name          = "lambda-errors-resume-parser-team2"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Resume Parser Lambda 함수 에러율이 임계값을 초과했습니다"
  alarm_actions       = [aws_sns_topic.hr_alarms.arn]
  
  dimensions = {
    FunctionName = aws_lambda_function.resume_parser.function_name
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "lambda_errors_affinity_calculator" {
  alarm_name          = "lambda-errors-affinity-calculator-team2"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Affinity Calculator Lambda 함수 에러율이 임계값을 초과했습니다"
  alarm_actions       = [aws_sns_topic.hr_alarms.arn]
  
  dimensions = {
    FunctionName = aws_lambda_function.affinity_calculator.function_name
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "lambda_errors_recommendation_engine" {
  alarm_name          = "lambda-errors-recommendation-engine-team2"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Recommendation Engine Lambda 함수 에러율이 임계값을 초과했습니다"
  alarm_actions       = [aws_sns_topic.hr_alarms.arn]
  
  dimensions = {
    FunctionName = aws_lambda_function.recommendation_engine.function_name
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "lambda_errors_domain_analysis" {
  alarm_name          = "lambda-errors-domain-analysis-team2"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Domain Analysis Lambda 함수 에러율이 임계값을 초과했습니다"
  alarm_actions       = [aws_sns_topic.hr_alarms.arn]
  
  dimensions = {
    FunctionName = aws_lambda_function.domain_analysis.function_name
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "lambda_errors_quantitative_analysis" {
  alarm_name          = "lambda-errors-quantitative-analysis-team2"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Quantitative Analysis Lambda 함수 에러율이 임계값을 초과했습니다"
  alarm_actions       = [aws_sns_topic.hr_alarms.arn]
  
  dimensions = {
    FunctionName = aws_lambda_function.quantitative_analysis.function_name
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "lambda_errors_qualitative_analysis" {
  alarm_name          = "lambda-errors-qualitative-analysis-team2"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Qualitative Analysis Lambda 함수 에러율이 임계값을 초과했습니다"
  alarm_actions       = [aws_sns_topic.hr_alarms.arn]
  
  dimensions = {
    FunctionName = aws_lambda_function.qualitative_analysis.function_name
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "lambda_errors_tech_trend_collector" {
  alarm_name          = "lambda-errors-tech-trend-collector-team2"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Tech Trend Collector Lambda 함수 에러율이 임계값을 초과했습니다"
  alarm_actions       = [aws_sns_topic.hr_alarms.arn]
  
  dimensions = {
    FunctionName = aws_lambda_function.tech_trend_collector.function_name
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "lambda_errors_vector_embedding" {
  alarm_name          = "lambda-errors-vector-embedding-team2"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Vector Embedding Lambda 함수 에러율이 임계값을 초과했습니다"
  alarm_actions       = [aws_sns_topic.hr_alarms.arn]
  
  dimensions = {
    FunctionName = aws_lambda_function.vector_embedding.function_name
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

# API Gateway Latency Alarm
resource "aws_cloudwatch_metric_alarm" "api_gateway_latency" {
  alarm_name          = "api-gateway-latency-team2"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Latency"
  namespace           = "AWS/ApiGateway"
  period              = 300
  statistic           = "Average"
  threshold           = 5000
  alarm_description   = "API Gateway 레이턴시가 5초를 초과했습니다"
  alarm_actions       = [aws_sns_topic.hr_alarms.arn]
  
  dimensions = {
    ApiName = aws_api_gateway_rest_api.hr_api.name
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

# API Gateway 5XX Error Alarm
resource "aws_cloudwatch_metric_alarm" "api_gateway_5xx_errors" {
  alarm_name          = "api-gateway-5xx-errors-team2"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "5XXError"
  namespace           = "AWS/ApiGateway"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "API Gateway 5XX 에러가 임계값을 초과했습니다"
  alarm_actions       = [aws_sns_topic.hr_alarms.arn]
  
  dimensions = {
    ApiName = aws_api_gateway_rest_api.hr_api.name
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

# DynamoDB Throttling Alarms
resource "aws_cloudwatch_metric_alarm" "dynamodb_read_throttle_employees" {
  alarm_name          = "dynamodb-read-throttle-employees-team2"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "ReadThrottleEvents"
  namespace           = "AWS/DynamoDB"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Employees 테이블에서 읽기 스로틀링이 발생했습니다"
  alarm_actions       = [aws_sns_topic.hr_alarms.arn]
  
  dimensions = {
    TableName = aws_dynamodb_table.employees.name
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "dynamodb_write_throttle_employees" {
  alarm_name          = "dynamodb-write-throttle-employees-team2"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "WriteThrottleEvents"
  namespace           = "AWS/DynamoDB"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Employees 테이블에서 쓰기 스로틀링이 발생했습니다"
  alarm_actions       = [aws_sns_topic.hr_alarms.arn]
  
  dimensions = {
    TableName = aws_dynamodb_table.employees.name
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "dynamodb_read_throttle_projects" {
  alarm_name          = "dynamodb-read-throttle-projects-team2"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "ReadThrottleEvents"
  namespace           = "AWS/DynamoDB"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Projects 테이블에서 읽기 스로틀링이 발생했습니다"
  alarm_actions       = [aws_sns_topic.hr_alarms.arn]
  
  dimensions = {
    TableName = aws_dynamodb_table.projects.name
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "dynamodb_write_throttle_projects" {
  alarm_name          = "dynamodb-write-throttle-projects-team2"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "WriteThrottleEvents"
  namespace           = "AWS/DynamoDB"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Projects 테이블에서 쓰기 스로틀링이 발생했습니다"
  alarm_actions       = [aws_sns_topic.hr_alarms.arn]
  
  dimensions = {
    TableName = aws_dynamodb_table.projects.name
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "dynamodb_read_throttle_affinity" {
  alarm_name          = "dynamodb-read-throttle-affinity-team2"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "ReadThrottleEvents"
  namespace           = "AWS/DynamoDB"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Employee Affinity 테이블에서 읽기 스로틀링이 발생했습니다"
  alarm_actions       = [aws_sns_topic.hr_alarms.arn]
  
  dimensions = {
    TableName = aws_dynamodb_table.employee_affinity.name
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "dynamodb_write_throttle_affinity" {
  alarm_name          = "dynamodb-write-throttle-affinity-team2"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "WriteThrottleEvents"
  namespace           = "AWS/DynamoDB"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Employee Affinity 테이블에서 쓰기 스로틀링이 발생했습니다"
  alarm_actions       = [aws_sns_topic.hr_alarms.arn]
  
  dimensions = {
    TableName = aws_dynamodb_table.employee_affinity.name
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

# Outputs
output "sns_topic_arn" {
  description = "SNS Topic ARN for alarms"
  value       = aws_sns_topic.hr_alarms.arn
}

output "cloudwatch_dashboards" {
  description = "CloudWatch Dashboard names"
  value = {
    lambda_metrics      = aws_cloudwatch_dashboard.lambda_metrics.dashboard_name
    api_gateway_metrics = aws_cloudwatch_dashboard.api_gateway_metrics.dashboard_name
    dynamodb_metrics    = aws_cloudwatch_dashboard.dynamodb_metrics.dashboard_name
  }
}
