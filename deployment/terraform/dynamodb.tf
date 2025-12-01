# DynamoDB Tables

resource "aws_dynamodb_table" "employees" {
  name           = "Employees"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "user_id"
  
  attribute {
    name = "user_id"
    type = "S"
  }
  
  attribute {
    name = "role"
    type = "S"
  }
  
  global_secondary_index {
    name            = "RoleIndex"
    hash_key        = "role"
    projection_type = "ALL"
  }
  
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

resource "aws_dynamodb_table" "projects" {
  name           = "Projects"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "project_id"
  
  attribute {
    name = "project_id"
    type = "S"
  }
  
  attribute {
    name = "client_industry"
    type = "S"
  }
  
  global_secondary_index {
    name            = "IndustryIndex"
    hash_key        = "client_industry"
    projection_type = "ALL"
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

resource "aws_dynamodb_table" "employee_affinity" {
  name           = "EmployeeAffinity"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "affinity_id"
  
  attribute {
    name = "affinity_id"
    type = "S"
  }
  
  attribute {
    name = "employee_1"
    type = "S"
  }
  
  global_secondary_index {
    name            = "Employee1Index"
    hash_key        = "employee_1"
    projection_type = "ALL"
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

resource "aws_dynamodb_table" "messenger_logs" {
  name           = "MessengerLogs"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "log_id"
  
  attribute {
    name = "log_id"
    type = "S"
  }
  
  attribute {
    name = "sender_id"
    type = "S"
  }
  
  attribute {
    name = "timestamp"
    type = "S"
  }
  
  global_secondary_index {
    name            = "SenderTimestampIndex"
    hash_key        = "sender_id"
    range_key       = "timestamp"
    projection_type = "ALL"
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

resource "aws_dynamodb_table" "company_events" {
  name           = "CompanyEvents"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "event_id"
  
  attribute {
    name = "event_id"
    type = "S"
  }
  
  attribute {
    name = "event_date"
    type = "S"
  }
  
  global_secondary_index {
    name            = "DateIndex"
    hash_key        = "event_date"
    projection_type = "ALL"
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

resource "aws_dynamodb_table" "tech_trends" {
  name           = "TechTrends"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "tech_name"
  
  attribute {
    name = "tech_name"
    type = "S"
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

# Employee Evaluations Table
resource "aws_dynamodb_table" "employee_evaluations" {
  name           = "EmployeeEvaluations"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "evaluation_id"
  
  attribute {
    name = "evaluation_id"
    type = "S"
  }
  
  attribute {
    name = "status"
    type = "S"
  }
  
  attribute {
    name = "submitted_at"
    type = "S"
  }
  
  global_secondary_index {
    name            = "StatusIndex"
    hash_key        = "status"
    range_key       = "submitted_at"
    projection_type = "ALL"
  }
  
  tags = {
    Team        = "Team2"
    EmployeeID  = "524956"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}
