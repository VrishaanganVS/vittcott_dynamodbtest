# Vittcott Deployment Guide

## 🚀 Overview

This project includes comprehensive CI/CD automation with extensive testing for deploying Vittcott (FastAPI backend + Streamlit AI Assistant) to AWS Elastic Beanstalk.

## 📋 Architecture

- **Backend**: FastAPI on port 8000
- **AI Assistant**: Streamlit on port 8501
- **Deployment**: AWS Elastic Beanstalk (multi-process)
- **Proxy**: Nginx routes `/streamlit` → Streamlit app
- **CI/CD**: GitHub Actions with 7-stage pipeline

## 🔧 Deployment Configuration

### Procfile
```
web: cd backend/src && uvicorn main:app --host 0.0.0.0 --port 8000 & streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
```

Both FastAPI and Streamlit run as background processes managed by Elastic Beanstalk.

### Nginx Configuration
- FastAPI APIs: `/api/*` → `localhost:8000`
- Streamlit App: `/streamlit` → `localhost:8501`
- Static files: `/` → `localhost:8000`
- WebSocket support for Streamlit (`/_stcore/stream`)

## 🧪 CI/CD Pipeline Stages

### 1. **Environment Validation** 🔍
- Detects changed files (backend/frontend/infra)
- Validates Python dependencies
- Checks environment variable schema

### 2. **Code Quality & Security** 🔎
- Linting with flake8
- Code formatting check with black
- Security scanning with bandit
- Vulnerability checking with safety

### 3. **Unit Tests** 🧪
- Runs pytest with coverage
- Creates basic import tests if none exist
- Generates coverage reports

### 4. **Smoke Tests (Local)** 🔥
Tests include:
- API health check
- Homepage loading
- Stocks live data endpoint
- Portfolio page
- Static assets (CSS/JS)
- Error handling
- CORS configuration
- Streamlit endpoint

### 5. **Deploy to AWS** 🚀
- Configures AWS credentials
- Verifies AWS connectivity (S3, DynamoDB)
- Creates deployment package
- Deploys to Elastic Beanstalk
- Waits for deployment completion

### 6. **Post-Deployment Tests** ✅
Tests production environment:
- Homepage accessibility
- API health
- Stocks API functionality
- Streamlit endpoint
- AWS integrations (S3, DynamoDB)
- Performance benchmarks

### 7. **Notification & Reporting** 📊
- Generates deployment summary
- Reports job statuses
- Creates GitHub step summary

## 🧪 Test Scripts

### Smoke Tests
```bash
python scripts/smoke_test.py
```
Tests all API endpoints and static file serving.

### AWS Integration Tests
```bash
export AWS_REGION=ap-south-1
export S3_PORTFOLIO_BUCKET=vittcott-portfolios
export DYNAMODB_TABLE=VittcottPortfolios
python scripts/test_aws_integration.py
```
Tests S3 and DynamoDB connectivity and permissions.

### Streamlit Integration Tests
```bash
export VITTCOTT_BASE_URL=http://localhost:8000
export STREAMLIT_URL=http://localhost:8501
python scripts/test_streamlit_integration.py
```
Tests Streamlit server, WebSocket, and backend integration.

## 🌐 Production URLs

- **Main Application**: http://vittcott-prod.eba-qjideeem.ap-south-1.elasticbeanstalk.com
- **API Endpoints**: `http://vittcott-prod.../api/*`
- **AI Assistant**: `http://vittcott-prod.../streamlit`

## 🔑 Required Environment Variables

Set these in AWS Elastic Beanstalk:

```bash
FINANCEHUB_API_KEY=<your-financehub-key>
GEMINI_API_KEY=<your-gemini-api-key>
AWS_REGION=ap-south-1
DYNAMODB_TABLE=VittcottPortfolios
S3_PORTFOLIO_BUCKET=vittcott-portfolios
PYTHONPATH=/var/app/current/backend/src:$PYTHONPATH
```

## 📦 Local Development

### Start Backend
```bash
cd backend/src
uvicorn main:app --reload --port 8000
```

### Start Streamlit
```bash
streamlit run streamlit_app.py --server.port 8501
```

### Run All Tests Locally
```bash
# Smoke tests
python scripts/smoke_test.py

# AWS tests (requires credentials)
python scripts/test_aws_integration.py

# Streamlit integration tests
python scripts/test_streamlit_integration.py
```

## 🚀 Deployment Workflow

1. **Make changes** to code locally
2. **Commit and push** to `main` branch
3. **GitHub Actions triggers** comprehensive CI/CD pipeline:
   - Environment validation
   - Code quality checks
   - Unit tests
   - Smoke tests
   - Deploy to AWS
   - Post-deployment verification
   - Generate reports
4. **Monitor** GitHub Actions workflow for results
5. **Verify** production deployment at AWS URL

## 🔄 Deployment Checklist

Before pushing to production:

- [ ] All tests pass locally
- [ ] Environment variables configured in AWS
- [ ] Database tables exist (DynamoDB)
- [ ] S3 buckets created and accessible
- [ ] API keys are valid
- [ ] Code quality checks pass
- [ ] No security vulnerabilities

## 🛠️ Troubleshooting

### Streamlit Not Loading
- Check nginx config: `.ebextensions/02_nginx.config`
- Verify Procfile runs both processes
- Check logs: `eb logs` or CloudWatch

### API Errors
- Verify environment variables: `eb printenv`
- Check CloudWatch logs for stack traces
- Test endpoints with smoke tests

### Deployment Failures
- Review GitHub Actions logs
- Check AWS Elastic Beanstalk events
- Verify IAM permissions

## 📊 Monitoring

- **CloudWatch Logs**: `/aws/elasticbeanstalk/vittcott-prod/`
- **CloudWatch Alarms**: High/Low CPU utilization
- **GitHub Actions**: Workflow run history

## 🎯 Key Features

✅ **Multi-process deployment** (FastAPI + Streamlit)  
✅ **Comprehensive testing** (7 stages)  
✅ **Automated deployment** (push to main)  
✅ **Environment validation**  
✅ **Security scanning**  
✅ **AWS integration tests**  
✅ **Streamlit integration tests**  
✅ **Performance monitoring**  
✅ **Detailed reporting**

## 📝 Notes

- Deployment takes ~5-10 minutes
- Streamlit runs in headless mode on production
- WebSocket connections required for Streamlit interactivity
- All AI Assistant links now point to `/streamlit` endpoint
- Nginx handles routing and load balancing

## 🔗 Resources

- [AWS Elastic Beanstalk Docs](https://docs.aws.amazon.com/elasticbeanstalk/)
- [Streamlit Deployment Guide](https://docs.streamlit.io/knowledge-base/deploy)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
