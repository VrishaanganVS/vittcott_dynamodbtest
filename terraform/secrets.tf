# AWS Secrets Manager - JWT Secret
resource "aws_secretsmanager_secret" "jwt_secret" {
  name                    = "${var.project_name}-jwt-secret"
  recovery_window_in_days = 7

  tags = {
    Name = "${var.project_name}-jwt-secret"
  }
}

resource "aws_secretsmanager_secret_version" "jwt_secret" {
  secret_id     = aws_secretsmanager_secret.jwt_secret.id
  secret_string = var.jwt_secret
}

# AWS Secrets Manager - Gemini API Key
resource "aws_secretsmanager_secret" "gemini_api_key" {
  name                    = "${var.project_name}-gemini-api-key"
  recovery_window_in_days = 7

  tags = {
    Name = "${var.project_name}-gemini-api-key"
  }
}

resource "aws_secretsmanager_secret_version" "gemini_api_key" {
  secret_id     = aws_secretsmanager_secret.gemini_api_key.id
  secret_string = var.gemini_api_key
}
