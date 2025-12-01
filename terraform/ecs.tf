# ECR Repositories
resource "aws_ecr_repository" "node_backend" {
  name                 = "${var.project_name}-node-backend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "${var.project_name}-node-backend-repo"
  }
}

resource "aws_ecr_repository" "python_backend" {
  name                 = "${var.project_name}-python-backend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "${var.project_name}-python-backend-repo"
  }
}

resource "aws_ecr_repository" "streamlit" {
  name                 = "${var.project_name}-streamlit"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "${var.project_name}-streamlit-repo"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name = "${var.project_name}-ecs-cluster"
  }
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "node_backend" {
  name              = "/ecs/${var.project_name}/node-backend"
  retention_in_days = 7

  tags = {
    Name = "${var.project_name}-node-backend-logs"
  }
}

resource "aws_cloudwatch_log_group" "python_backend" {
  name              = "/ecs/${var.project_name}/python-backend"
  retention_in_days = 7

  tags = {
    Name = "${var.project_name}-python-backend-logs"
  }
}

resource "aws_cloudwatch_log_group" "streamlit" {
  name              = "/ecs/${var.project_name}/streamlit"
  retention_in_days = 7

  tags = {
    Name = "${var.project_name}-streamlit-logs"
  }
}

# ECS Task Definition - Node Backend
resource "aws_ecs_task_definition" "node_backend" {
  family                   = "${var.project_name}-node-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.container_cpu
  memory                   = var.container_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name  = "node-backend"
    image = "${aws_ecr_repository.node_backend.repository_url}:latest"
    
    portMappings = [{
      containerPort = 3000
      protocol      = "tcp"
    }]

    environment = [
      { name = "NODE_ENV", value = "production" },
      { name = "AWS_REGION", value = var.aws_region },
      { name = "USERS_TABLE", value = var.dynamodb_table_name },
      { name = "FRONTEND_ORIGINS", value = "http://${aws_lb.main.dns_name}" }
    ]

    secrets = [
      { name = "JWT_SECRET", valueFrom = aws_secretsmanager_secret.jwt_secret.arn }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.node_backend.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }

    healthCheck = {
      command     = ["CMD-SHELL", "node -e \"require('http').get('http://localhost:3000/', (r) => process.exit(r.statusCode === 200 ? 0 : 1))\""]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
  }])

  tags = {
    Name = "${var.project_name}-node-backend-task"
  }
}

# ECS Task Definition - Python Backend
resource "aws_ecs_task_definition" "python_backend" {
  family                   = "${var.project_name}-python-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.container_cpu
  memory                   = var.container_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name  = "python-backend"
    image = "${aws_ecr_repository.python_backend.repository_url}:latest"
    
    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]

    environment = [
      { name = "AWS_REGION", value = var.aws_region },
      { name = "PORT", value = "8000" },
      { name = "RELOAD", value = "false" }
    ]

    secrets = [
      { name = "GEMINI_API_KEY", valueFrom = aws_secretsmanager_secret.gemini_api_key.arn }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.python_backend.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }

    healthCheck = {
      command     = ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8000/api').read()\""]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
  }])

  tags = {
    Name = "${var.project_name}-python-backend-task"
  }
}

# ECS Task Definition - Streamlit
resource "aws_ecs_task_definition" "streamlit" {
  family                   = "${var.project_name}-streamlit"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.container_cpu
  memory                   = var.container_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name  = "streamlit"
    image = "${aws_ecr_repository.streamlit.repository_url}:latest"
    
    portMappings = [{
      containerPort = 8501
      protocol      = "tcp"
    }]

    environment = [
      { name = "VITTCOTT_BACKEND_URL", value = "http://${aws_lb.main.dns_name}:8000" }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.streamlit.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }

    healthCheck = {
      command     = ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health').read()\""]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
  }])

  tags = {
    Name = "${var.project_name}-streamlit-task"
  }
}

# ECS Services
resource "aws_ecs_service" "node_backend" {
  name            = "${var.project_name}-node-backend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.node_backend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.private_1.id, aws_subnet.private_2.id]
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.node_backend.arn
    container_name   = "node-backend"
    container_port   = 3000
  }

  depends_on = [aws_lb_listener.http]

  tags = {
    Name = "${var.project_name}-node-backend-service"
  }
}

resource "aws_ecs_service" "python_backend" {
  name            = "${var.project_name}-python-backend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.python_backend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.private_1.id, aws_subnet.private_2.id]
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.python_backend.arn
    container_name   = "python-backend"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.http]

  tags = {
    Name = "${var.project_name}-python-backend-service"
  }
}

resource "aws_ecs_service" "streamlit" {
  name            = "${var.project_name}-streamlit"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.streamlit.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.private_1.id, aws_subnet.private_2.id]
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.streamlit.arn
    container_name   = "streamlit"
    container_port   = 8501
  }

  depends_on = [aws_lb_listener.http]

  tags = {
    Name = "${var.project_name}-streamlit-service"
  }
}
