terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "lakehouse_raw" {
  bucket = var.raw_bucket_name
}

resource "aws_s3_bucket_versioning" "lakehouse_raw_versioning" {
  bucket = aws_s3_bucket.lakehouse_raw.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket" "lakehouse_processed" {
  bucket = var.processed_bucket_name
}

resource "aws_s3_bucket_versioning" "lakehouse_processed_versioning" {
  bucket = aws_s3_bucket.lakehouse_processed.id
  versioning_configuration {
    status = "Enabled"
  }
}

