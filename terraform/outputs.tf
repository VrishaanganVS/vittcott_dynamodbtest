output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "node_backend_url" {
  description = "URL for Node backend"
  value       = "http://${aws_lb.main.dns_name}:3000"
}

output "python_backend_url" {
  description = "URL for Python backend"
  value       = "http://${aws_lb.main.dns_name}:8000"
}

output "streamlit_url" {
  description = "URL for Streamlit"
  value       = "http://${aws_lb.main.dns_name}:8501"
}

output "dynamodb_table_name" {
  description = "DynamoDB table name"
  value       = aws_dynamodb_table.users.name
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}
