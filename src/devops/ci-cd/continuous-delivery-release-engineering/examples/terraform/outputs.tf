output "lambda_name" {
  value = aws_lambda_function.demo.function_name
}

output "live_alias_arn" {
  value = aws_lambda_alias.live.arn
}

output "aws_account_id" {
  value = data.aws_caller_identity.current.account_id
}
