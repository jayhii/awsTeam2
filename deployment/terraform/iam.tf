# IAM Roles and Policies

# Lambda Execution Role
resource "aws_iam_role" "lambda_execution_team2" {
  name = "LambdaExecutionRole-Team2"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
        Condition = {
          StringEquals = {
            "aws:RequestedRegion" = var.aws_region
          }
        }
      }
    ]
  })
  
  tags = {
    Team       = "Team2"
    EmployeeID = "524956"
    Project    = "HR-Resource-Optimization"
  }
}

# Attach AWS managed policy for basic Lambda execution
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_execution_team2.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# DynamoDB Access Policy
resource "aws_iam_role_policy" "lambda_dynamodb_access" {
  name = "Team2-DynamoDB-Access"
  role = aws_iam_role.lambda_execution_team2.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:DescribeStream",
          "dynamodb:GetRecords",
          "dynamodb:GetShardIterator",
          "dynamodb:ListStreams"
        ]
        Resource = "arn:aws:dynamodb:${var.aws_region}:*:table/*"
        Condition = {
          StringEquals = {
            "aws:ResourceTag/Team" = "Team2"
          }
        }
      }
    ]
  })
}

# S3 Access Policy
resource "aws_iam_role_policy" "lambda_s3_access" {
  name = "Team2-S3-Access"
  role = aws_iam_role.lambda_execution_team2.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "arn:aws:s3:::*/*"
        Condition = {
          StringEquals = {
            "aws:ResourceTag/Team" = "Team2"
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = "arn:aws:s3:::*"
        Condition = {
          StringEquals = {
            "aws:ResourceTag/Team" = "Team2"
          }
        }
      }
    ]
  })
}

# Bedrock Access Policy
resource "aws_iam_role_policy" "lambda_bedrock_access" {
  name = "Team2-Bedrock-Access"
  role = aws_iam_role.lambda_execution_team2.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = [
          "arn:aws:bedrock:${var.aws_region}::foundation-model/anthropic.claude-v2",
          "arn:aws:bedrock:${var.aws_region}::foundation-model/amazon.titan-embed-text-v1"
        ]
      }
    ]
  })
}

# Textract Access Policy
resource "aws_iam_role_policy" "lambda_textract_access" {
  name = "Team2-Textract-Access"
  role = aws_iam_role.lambda_execution_team2.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "textract:DetectDocumentText",
          "textract:AnalyzeDocument"
        ]
        Resource = "*"
      }
    ]
  })
}

# OpenSearch Access Policy
resource "aws_iam_role_policy" "lambda_opensearch_access" {
  name = "Team2-OpenSearch-Access"
  role = aws_iam_role.lambda_execution_team2.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "es:ESHttpGet",
          "es:ESHttpPut",
          "es:ESHttpPost",
          "es:ESHttpDelete"
        ]
        Resource = "arn:aws:es:${var.aws_region}:*:domain/*"
        Condition = {
          StringEquals = {
            "aws:ResourceTag/Team" = "Team2"
          }
        }
      }
    ]
  })
}

# API Gateway Execution Role
resource "aws_iam_role" "api_gateway_execution_team2" {
  name = "APIGatewayExecutionRole-Team2"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "apigateway.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
  
  tags = {
    Team       = "Team2"
    EmployeeID = "524956"
    Project    = "HR-Resource-Optimization"
  }
}

# API Gateway Lambda Invoke Policy
resource "aws_iam_role_policy" "api_gateway_lambda_invoke" {
  name = "Team2-Lambda-Invoke"
  role = aws_iam_role.api_gateway_execution_team2.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "lambda:InvokeFunction"
        Resource = "arn:aws:lambda:${var.aws_region}:*:function:*"
        Condition = {
          StringEquals = {
            "aws:ResourceTag/Team" = "Team2"
          }
        }
      }
    ]
  })
}
