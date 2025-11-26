# OpenSearch Domain

resource "aws_opensearch_domain" "hr_search" {
  domain_name    = "hr-employee-search-team2"
  engine_version = "OpenSearch_2.11"
  
  cluster_config {
    instance_type          = "t3.medium.search"
    instance_count         = 2
    zone_awareness_enabled = true
    
    zone_awareness_config {
      availability_zone_count = 2
    }
  }
  
  ebs_options {
    ebs_enabled = true
    volume_type = "gp3"
    volume_size = 100
  }
  
  encrypt_at_rest {
    enabled = true
  }
  
  node_to_node_encryption {
    enabled = true
  }
  
  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }
  
  advanced_security_options {
    enabled                        = true
    internal_user_database_enabled = false
    
    master_user_options {
      master_user_arn = aws_iam_role.lambda_execution_team2.arn
    }
  }
  
  access_policies = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = aws_iam_role.lambda_execution_team2.arn
        }
        Action   = "es:*"
        Resource = "arn:aws:es:${var.aws_region}:*:domain/hr-employee-search-team2/*"
      }
    ]
  })
  
  tags = {
    Team        = "Team2"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
  }
}

output "opensearch_endpoint" {
  value       = aws_opensearch_domain.hr_search.endpoint
  description = "OpenSearch domain endpoint"
}
