output "raw_bucket_name"       { value = aws_s3_bucket.lakehouse_raw.id }
output "processed_bucket_name" { value = aws_s3_bucket.lakehouse_processed.id }