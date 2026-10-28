# DELIBERATELY MISCONFIGURED. Never `terraform apply` this — it exists only for Checkov to scan.
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" {
  region = "us-east-1"
}

# VULN: public-read bucket, no encryption, no versioning, no logging
resource "aws_s3_bucket" "notes_backups" {
  bucket = "devsecops-lab-notes-backups"
}

resource "aws_s3_bucket_acl" "notes_backups" {
  bucket = aws_s3_bucket.notes_backups.id
  acl    = "public-read"
}

# VULN: SSH open to the internet
resource "aws_security_group" "app" {
  name        = "notes-app"
  description = "notes app"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# VULN: wildcard IAM policy
resource "aws_iam_policy" "app" {
  name = "notes-app"
  policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Action = "*", Resource = "*" }]
  })
}
