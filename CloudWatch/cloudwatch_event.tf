variable "lambda_function_name" {
}

data "aws_caller_identity" "current" {
}

data "aws_region" "current" {
}

resource "aws_cloudwatch_event_rule" "event_schedule" {
  name                = "set_cloudwatch_expire"
  description         = "Run Lambda set_cloudwatch_expire 
on the 1st of every month"
  schedule_expression = "cron(00 00 1 * ? *)"
}

resource "aws_cloudwatch_event_target" "event_schedule" {
  target_id = "SetCloudWatchExpire"
  arn       = "arn:aws:lambda:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:function:${var.lambda_function_name}"
  rule      = aws_cloudwatch_event_rule.event_schedule.name
}

resource "aws_lambda_permission" "allow_lambda_function" {
  statement_id  = "AllowExecutionSetCloudWatchExpire"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.event_schedule.arn
}

