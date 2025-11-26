# S3 Buckets

resource "aws_s3_bucket" "frontend_hosting" {
  bucket = "${var.project_name}-frontend-hosting-${var.environment}"
  
  tags = {
    Team        = "Team2"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
    Purpose     = "Frontend Static Website Hosting"
  }
}

resource "aws_s3_bucket_website_configuration" "frontend_hosting" {
  bucket = aws_s3_bucket.frontend_hosting.id
  
  index_document {
    suffix = "index.html"
  }
  
  error_document {
    key = "error.html"
  }
}

resource "aws_s3_bucket_public_access_block" "frontend_hosting" {
  bucket = aws_s3_bucket.frontend_hosting.id
  
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_cors_configuration" "frontend_hosting" {
  bucket = aws_s3_bucket.frontend_hosting.id
  
  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = ["*"]
    max_age_seconds = 3000
  }
}

resource "aws_s3_bucket" "resumes" {
  bucket = "${var.project_name}-resumes-${var.environment}"
  
  tags = {
    Team        = "Team2"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
    Purpose     = "Resume Storage"
  }
}

resource "aws_s3_bucket_versioning" "resumes" {
  bucket = aws_s3_bucket.resumes.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "resumes" {
  bucket = aws_s3_bucket.resumes.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "resumes" {
  bucket = aws_s3_bucket.resumes.id
  
  rule {
    id     = "ArchiveOldResumes"
    status = "Enabled"
    
    filter {}
    
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}

resource "aws_s3_bucket_notification" "resumes" {
  bucket = aws_s3_bucket.resumes.id
  
  lambda_function {
    lambda_function_arn = aws_lambda_function.resume_parser.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "uploads/"
    filter_suffix       = ".pdf"
  }
  
  depends_on = [aws_lambda_permission.allow_s3_resume_parser]
}

resource "aws_s3_bucket" "reports" {
  bucket = "${var.project_name}-reports-${var.environment}"
  
  tags = {
    Team        = "Team2"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
    Purpose     = "Reports and Dashboard Data"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "reports" {
  bucket = aws_s3_bucket.reports.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "reports" {
  bucket = aws_s3_bucket.reports.id
  
  rule {
    id     = "DeleteOldReports"
    status = "Enabled"
    
    filter {}
    
    expiration {
      days = 365
    }
  }
}

resource "aws_s3_bucket" "data_lake" {
  bucket = "${var.project_name}-data-lake-${var.environment}"
  
  tags = {
    Team        = "Team2"
    Project     = "HR-Resource-Optimization"
    Environment = var.environment
    Purpose     = "Raw Data and Logs"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id
  
  rule {
    id     = "TransitionToIA"
    status = "Enabled"
    
    filter {}
    
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
    
    transition {
      days          = 180
      storage_class = "GLACIER"
    }
  }
}
