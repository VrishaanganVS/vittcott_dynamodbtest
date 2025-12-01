variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "ap-south-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "vittcott"
}

variable "dynamodb_table_name" {
  description = "DynamoDB table name for users"
  type        = string
  default     = "Vittcott_Users"
}

variable "container_cpu" {
  description = "CPU units for ECS tasks"
  type        = number
  default     = 256
}

variable "container_memory" {
  description = "Memory for ECS tasks (MB)"
  type        = number
  default     = 512
}

variable "node_backend_image" {
  description = "Docker image for Node backend"
  type        = string
  default     = "vittcott-node:latest"
}

variable "python_backend_image" {
  description = "Docker image for Python backend"
  type        = string
  default     = "vittcott-python:latest"
}

variable "streamlit_image" {
  description = "Docker image for Streamlit"
  type        = string
  default     = "vittcott-streamlit:latest"
}

variable "jwt_secret" {
  description = "JWT secret for authentication"
  type        = string
  sensitive   = true
}

variable "gemini_api_key" {
  description = "Gemini API key"
  type        = string
  sensitive   = true
}
