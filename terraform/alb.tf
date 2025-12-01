# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = [aws_subnet.public_1.id, aws_subnet.public_2.id]

  enable_deletion_protection = false

  tags = {
    Name = "${var.project_name}-alb"
  }
}

# Target Groups
resource "aws_lb_target_group" "node_backend" {
  name        = "${var.project_name}-node-tg"
  port        = 3000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/"
    healthy_threshold   = 2
    unhealthy_threshold = 10
    timeout             = 30
    interval            = 60
    matcher             = "200"
  }

  tags = {
    Name = "${var.project_name}-node-tg"
  }
}

resource "aws_lb_target_group" "python_backend" {
  name        = "${var.project_name}-python-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/api"
    healthy_threshold   = 2
    unhealthy_threshold = 10
    timeout             = 30
    interval            = 60
    matcher             = "200"
  }

  tags = {
    Name = "${var.project_name}-python-tg"
  }
}

resource "aws_lb_target_group" "streamlit" {
  name        = "${var.project_name}-streamlit-tg"
  port        = 8501
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/_stcore/health"
    healthy_threshold   = 2
    unhealthy_threshold = 10
    timeout             = 30
    interval            = 60
    matcher             = "200"
  }

  tags = {
    Name = "${var.project_name}-streamlit-tg"
  }
}

# ALB Listener
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.python_backend.arn
  }
}

# Listener Rules for routing
resource "aws_lb_listener_rule" "node_backend" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.node_backend.arn
  }

  condition {
    path_pattern {
      values = ["/auth/*", "/register", "/login", "/me"]
    }
  }
}

resource "aws_lb_listener_rule" "streamlit" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 200

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.streamlit.arn
  }

  condition {
    path_pattern {
      values = ["/assistant/*", "/_stcore/*"]
    }
  }
}
