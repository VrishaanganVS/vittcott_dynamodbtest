# Docker Setup Guide for VittCott

## Files Created
- `backend/Dockerfile` - Node.js authentication service
- `Dockerfile.python` - Python FastAPI backend
- `Dockerfile.streamlit` - Streamlit AI assistant
- `docker-compose.yml` - Orchestrates all services
- `.dockerignore` - Excludes unnecessary files
- `.env.example` - Environment variables template

## Quick Start with Docker

### 1. Ensure .env file exists
```powershell
# Copy the example if you don't have .env yet
Copy-Item .env.example .env
# Then edit .env with your actual credentials
```

### 2. Build and Run All Services
```powershell
# Build images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### 3. Access Your Application
- **Node Backend:** http://localhost:3000
- **Python Backend:** http://localhost:8000
- **Streamlit:** http://localhost:8501

## Individual Docker Commands

### Build Individual Services
```powershell
# Node backend
docker build -t vittcott-node ./backend

# Python backend
docker build -f Dockerfile.python -t vittcott-python .

# Streamlit
docker build -f Dockerfile.streamlit -t vittcott-streamlit .
```

### Run Individual Containers
```powershell
# Node backend
docker run -d -p 3000:3000 --env-file .env --name node-backend vittcott-node

# Python backend
docker run -d -p 8000:8000 --env-file .env --name python-backend vittcott-python

# Streamlit
docker run -d -p 8501:8501 --env-file .env --name streamlit vittcott-streamlit
```

## Useful Docker Commands

```powershell
# Check running containers
docker ps

# View logs for specific service
docker-compose logs -f node-backend
docker-compose logs -f python-backend
docker-compose logs -f streamlit

# Restart a service
docker-compose restart node-backend

# Rebuild and restart after code changes
docker-compose up -d --build

# Stop and remove all containers
docker-compose down

# Remove all containers, networks, and volumes
docker-compose down -v

# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}"

# Execute command in running container
docker-compose exec node-backend sh
docker-compose exec python-backend bash
docker-compose exec streamlit bash
```

## Troubleshooting

### Port Already in Use
```powershell
# Find process using port
netstat -ano | Select-String "3000"

# Stop specific container
docker stop vittcott-node-backend

# Or stop all
docker-compose down
```

### Container Won't Start
```powershell
# Check logs
docker-compose logs node-backend

# Remove and rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Environment Variables Not Loading
```powershell
# Verify .env file exists
Get-Content .env

# Restart with fresh env
docker-compose down
docker-compose up -d
```

## Production Deployment

### Push to Docker Hub
```powershell
# Login to Docker Hub
docker login

# Tag images
docker tag vittcott-node yourusername/vittcott-node:latest
docker tag vittcott-python yourusername/vittcott-python:latest
docker tag vittcott-streamlit yourusername/vittcott-streamlit:latest

# Push images
docker push yourusername/vittcott-node:latest
docker push yourusername/vittcott-python:latest
docker push yourusername/vittcott-streamlit:latest
```

### Deploy to AWS ECS
- Upload images to AWS ECR
- Create ECS Task Definitions using these images
- Configure ECS Service with load balancer
- Set environment variables in task definitions

## Next Steps
1. ✅ Docker setup complete
2. Create CI/CD pipeline (GitHub Actions)
3. Set up nginx reverse proxy
4. Add monitoring (CloudWatch/Prometheus)
5. Implement auto-scaling
