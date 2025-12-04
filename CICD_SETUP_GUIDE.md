# 🚀 CI/CD Setup Guide for Vittcott

## What is CI/CD?

**CI/CD** = **Continuous Integration / Continuous Deployment**

- **Continuous Integration (CI):** Automatically tests your code every time you push to GitHub
- **Continuous Deployment (CD):** Automatically deploys your code to production when tests pass

## ✅ What I've Created

### 1. **Main CI/CD Pipeline** (`.github/workflows/ci-cd.yml`)
Runs on every push to `main` or `develop` branch:
- ✅ Tests Python backend
- ✅ Checks code quality with Flake8
- ✅ Builds frontend (Node.js)
- ✅ Validates all code
- ✅ Shows summary in GitHub Actions tab

### 2. **AWS Deployment** (`.github/workflows/deploy-aws.yml`)
Deploys to AWS when you push to `main`:
- ✅ Packages your backend
- ✅ Uploads to S3
- ✅ Ready for AWS Lambda/Elastic Beanstalk/App Runner

### 3. **Code Quality Checks** (`.github/workflows/code-quality.yml`)
Runs on pull requests:
- ✅ Code formatting checks (Black)
- ✅ Security scans (Bandit)
- ✅ Dependency vulnerability checks
- ✅ Import sorting

---

## 🔧 Setup Steps (You Need to Do This!)

### Step 1: Add Secrets to GitHub

Go to your GitHub repository:
1. Click **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add these secrets:

| Secret Name | Value | Where to Get It |
|------------|-------|-----------------|
| `GEMINI_API_KEY` | Your Gemini API key | Google AI Studio |
| `FINANCEHUB_API_KEY` | Your Finnhub API key | Finnhub.io |
| `AWS_ACCESS_KEY_ID` | Your AWS access key | AWS IAM Console |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret key | AWS IAM Console |
| `S3_PORTFOLIO_BUCKET` | `vittcott-uploads-xyz123` | Your S3 bucket name |
| `DEPLOYMENT_BUCKET` | (Optional) S3 bucket for deployments | AWS S3 Console |

#### How to Get AWS Keys:
1. Go to [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. Click **Users** → Your username → **Security credentials**
3. Click **Create access key**
4. Copy **Access key ID** and **Secret access key**
5. Paste them in GitHub secrets

### Step 2: Commit and Push

```bash
# Stage the new workflow files
git add .github/workflows/
git add CICD_SETUP_GUIDE.md

# Commit
git commit -m "Add CI/CD pipelines with GitHub Actions"

# Push to GitHub
git push origin main
```

### Step 3: Check GitHub Actions

1. Go to your repo on GitHub: `https://github.com/VrishaanganVS/vittcott_dynamodbtest`
2. Click the **Actions** tab
3. You'll see your workflows running!

---

## 📊 What Happens After Push?

### Every time you push code:
1. ✅ **Tests run automatically** (Python backend tests)
2. ✅ **Code quality checks** (Flake8, formatting)
3. ✅ **Frontend builds** (Node.js validation)
4. ✅ **Results shown** in GitHub Actions tab
5. ✅ **Green checkmark** if all pass ✓
6. ❌ **Red X** if something fails

### Example workflow:
```
You push code → GitHub detects push → Workflows trigger → Tests run → Results shown
```

---

## 🎯 How to Use Each Workflow

### 1. **Automatic CI (ci-cd.yml)**
- **Triggers:** Automatically on every push to `main` or `develop`
- **Purpose:** Validate code quality and run tests
- **What it does:**
  - Runs Python tests
  - Checks code formatting
  - Validates Node.js
  - Shows pass/fail status

### 2. **AWS Deployment (deploy-aws.yml)**
- **Triggers:** 
  - Push to `main` branch
  - Manual trigger (click "Run workflow" button)
- **Purpose:** Deploy to AWS
- **What it does:**
  - Packages backend code
  - Uploads to S3
  - Ready for AWS services

### 3. **Code Quality (code-quality.yml)**
- **Triggers:** Pull requests to `main` or `develop`
- **Purpose:** Ensure code quality before merging
- **What it does:**
  - Checks formatting with Black
  - Scans for security issues
  - Validates dependencies

---

## 🔍 How to View Results

### In GitHub:
1. Go to **Actions** tab
2. Click on any workflow run
3. See detailed logs and test results

### In Pull Requests:
- Green checkmark ✅ = All tests passed
- Red X ❌ = Tests failed (click to see why)
- Yellow dot 🟡 = Tests running

---

## 🚀 Advanced: Deploy to AWS

### Option A: AWS Lambda (Serverless)
```bash
# Install Serverless Framework
npm install -g serverless

# Deploy backend as Lambda function
cd backend
serverless deploy
```

### Option B: AWS Elastic Beanstalk
```bash
# Install EB CLI
pip install awsebcli

# Initialize and deploy
eb init -p python-3.11 vittcott-backend
eb create vittcott-prod
eb deploy
```

### Option C: AWS App Runner (Easiest)
1. Go to AWS App Runner console
2. Create service from source code
3. Connect to GitHub repo
4. App Runner builds and deploys automatically

---

## 📝 Workflow Status Badges

Add these to your README.md to show build status:

```markdown
![CI/CD](https://github.com/VrishaanganVS/vittcott_dynamodbtest/workflows/CI%2FCD%20Pipeline/badge.svg)
![Deploy](https://github.com/VrishaanganVS/vittcott_dynamodbtest/workflows/Deploy%20to%20AWS/badge.svg)
```

---

## 🐛 Troubleshooting

### "Secrets not found"
→ Make sure you added all secrets in GitHub Settings → Secrets

### "Tests failed"
→ Click on the failed workflow to see error details

### "Permission denied"
→ Check AWS IAM permissions for your access keys

### "Workflow not running"
→ Make sure you pushed the `.github/workflows/` folder

---

## 📚 Next Steps

1. ✅ **Add secrets to GitHub** (Step 1 above)
2. ✅ **Push to GitHub** (Step 2 above)
3. ✅ **Watch workflows run** (Step 3 above)
4. 🚀 **Deploy to AWS** (when ready)

---

## 🎓 Learn More

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS Deployment Guide](https://aws.amazon.com/getting-started/)
- [CI/CD Best Practices](https://www.atlassian.com/continuous-delivery/principles/continuous-integration-vs-delivery-vs-deployment)

---

**Your CI/CD is now set up! Every push will automatically test your code. 🎉**
