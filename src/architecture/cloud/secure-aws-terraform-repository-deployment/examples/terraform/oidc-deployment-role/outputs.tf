output "deployment_role_arn" {
  value       = aws_iam_role.deploy.arn
  description = "Set as environment-scoped GitHub variable AWS_DEPLOY_ROLE_ARN."
}
