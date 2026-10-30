output "state_bucket_name" {
  description = "Pass as TF_STATE_BUCKET for the corresponding GitHub environment."
  value       = aws_s3_bucket.state.id
}
