# 🚀 Quick Start: Push to GitHub and Activate CI/CD

## Step 1: Add GitHub Secrets (REQUIRED!)

Go to this URL:
```
https://github.com/VrishaanganVS/vittcott_dynamodbtest/settings/secrets/actions
```

Click **"New repository secret"** and add each of these:

| Secret Name | Where to Find It |
|------------|------------------|
| `GEMINI_API_KEY` | Google AI Studio: https://makersuite.google.com/app/apikey |
| `FINANCEHUB_API_KEY` | Finnhub: https://finnhub.io/dashboard |
| `AWS_ACCESS_KEY_ID` | AWS IAM: https://console.aws.amazon.com/iam/ → Users → Security credentials |
| `AWS_SECRET_ACCESS_KEY` | Same as above |
| `S3_PORTFOLIO_BUCKET` | Type: `vittcott-uploads-xyz123` |

## Step 2: Push to GitHub

Copy and paste these commands:

```powershell
# Stage all workflow files
git add .github/workflows/ CICD_SETUP_GUIDE.md QUICK_START.md

# Commit
git commit -m "Add CI/CD workflows for automated testing and deployment"

# Push to GitHub
git push origin main
```

## Step 3: Watch It Work!

1. Go to: https://github.com/VrishaanganVS/vittcott_dynamodbtest/actions
2. You'll see workflows running automatically
3. Green ✅ = all tests passed
4. Red ❌ = something failed (click to see details)

## What Happens Automatically?

Every time you push code:
- ✅ Python tests run
- ✅ Code quality checks
- ✅ Frontend validation
- ✅ Security scans
- ✅ Results shown in Actions tab

## Need Help?

Open `CICD_SETUP_GUIDE.md` for detailed instructions.
