# DEMO ONLY: provision in an isolated AWS sandbox. Requires function.zip to exist.
data "aws_caller_identity" "current" {}
resource "aws_iam_role" "lambda_exec" {
  name_prefix = "cd-suite-demo-lambda-"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
  tags = { Purpose = "training", Owner = var.owner_tag }
}
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/cd-suite-demo-${var.suffix}"
  retention_in_days = 7
  tags = { Purpose = "training", Owner = var.owner_tag }
}
resource "aws_lambda_function" "demo" {
  function_name    = "cd-suite-demo-${var.suffix}"
  role             = aws_iam_role.lambda_exec.arn
  filename         = "${path.module}/../lambda/function.zip"
  source_code_hash = filebase64sha256("${path.module}/../lambda/function.zip")
  handler          = "function.handler"
  runtime          = "python3.12"
  timeout          = 5
  publish          = true
  depends_on       = [aws_iam_role_policy_attachment.lambda_logs, aws_cloudwatch_log_group.lambda_logs]
  tags             = { Purpose = "training", Owner = var.owner_tag }
}
resource "aws_lambda_alias" "live" {
  name             = "live"
  function_name    = aws_lambda_function.demo.function_name
  function_version = aws_lambda_function.demo.version
}
