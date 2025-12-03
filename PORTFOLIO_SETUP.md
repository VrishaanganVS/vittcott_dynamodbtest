# 🎯 Portfolio Analysis Implementation - Quick Setup Guide

## ✅ What's Been Implemented

I've built a **complete portfolio analysis system** with:

1. **Backend (FastAPI)**
   - S3 portfolio fetching
   - Excel/CSV parsing with pandas
   - AI analysis using Gemini
   - RESTful API endpoints

2. **Frontend**
   - Beautiful portfolio dashboard with dark theme
   - Interactive pie chart (Chart.js)
   - AI insights display
   - Responsive design

3. **CI/CD Pipeline (GitHub Actions)**
   - Automated testing
   - Docker image building
   - Terraform infrastructure deployment
   - Development and production workflows

4. **DevOps**
   - Docker containerization
   - Terraform S3 infrastructure
   - Environment configuration

---

## 🚀 Quick Start (5 Steps)

### Step 1: Install New Dependencies

```bash
cd backend
pip install pandas openpyxl boto3 botocore
```

Or simply:
```bash
pip install -r requirements.txt
```

### Step 2: Update Your `.env` File

Add these variables to `backend/.env`:

```bash
# AWS S3 Configuration
S3_PORTFOLIO_BUCKET=vittcott-portfolios
AWS_ACCESS_KEY_ID=your_aws_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_here
AWS_REGION=ap-south-1

# Already have these
GEMINI_API_KEY=your_existing_key
FINANCEHUB_API_KEY=your_existing_key
```

### Step 3: Create Sample Portfolio

```bash
# Create sample portfolio file
python create_sample_portfolio.py
```

This creates `sample_portfolio.xlsx` with 10 sample stocks.

### Step 4: Upload to S3

```bash
# Upload portfolio to S3 (replace YOUR_USER_ID with actual user ID)
aws s3 cp sample_portfolio.xlsx s3://vittcott-portfolios/portfolios/YOUR_USER_ID/
```

Or use AWS Console to upload to:
```
s3://vittcott-portfolios/portfolios/{user_id}/sample_portfolio.xlsx
```

### Step 5: Start Server & Test

```bash
# Start backend
cd backend/src
python -m uvicorn main:app --reload --port 8000

# Open browser
http://localhost:3000/pages/portfolio.html
```

Enter:
- **User ID**: `YOUR_USER_ID`
- **Filename**: `sample_portfolio.xlsx`

Click **"Analyze Portfolio"** 🎉

---

## 📁 New Files Created

```
backend/src/
├── services/
│   ├── __init__.py                    # NEW - Services package
│   └── portfolio_service.py           # NEW - S3 & Analysis logic
├── routes/
│   └── portfolio.py                   # NEW - API endpoints
├── models/
│   └── portfolio_models.py            # NEW - Pydantic models
└── frontend_build/pages/
    └── portfolio.html                 # NEW - Dashboard UI

.github/workflows/
├── ci-cd.yml                          # NEW - Production pipeline
└── dev-ci.yml                         # NEW - Development pipeline

create_sample_portfolio.py             # NEW - Sample generator
PORTFOLIO_IMPLEMENTATION.md            # NEW - Full documentation
PORTFOLIO_SETUP.md                     # NEW - This file
```

---

## 🎨 Portfolio File Format

Your Excel or CSV file needs these columns:

### Required:
- `symbol` - Stock ticker (e.g., AAPL, GOOGL)
- `quantity` - Number of shares
- `purchase_price` - Price when bought

### Optional (for P&L calculation):
- `current_price` - Current market price

### Example:

| symbol | quantity | purchase_price | current_price |
|--------|----------|----------------|---------------|
| AAPL   | 10       | 150.00         | 175.50        |
| GOOGL  | 5        | 2800.00        | 2950.00       |
| MSFT   | 15       | 300.00         | 380.00        |

---

## 📊 API Endpoints

### 1. List Portfolios
```bash
GET http://localhost:8000/api/portfolios/{user_id}
```

### 2. Analyze Portfolio
```bash
POST http://localhost:8000/api/portfolio/analyze
Content-Type: application/json

{
  "user_id": "user123",
  "filename": "my_portfolio.xlsx"
}
```

### 3. Get Sample Format
```bash
GET http://localhost:8000/api/portfolio/sample
```

---

## 🔧 Testing the Implementation

### Option 1: Via UI (Easiest)
1. Navigate to `http://localhost:3000/pages/portfolio.html`
2. Enter your User ID and filename
3. Click "Analyze Portfolio"

### Option 2: Via API (curl)
```bash
curl -X POST http://localhost:8000/api/portfolio/analyze \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test_user","filename":"sample_portfolio.xlsx"}'
```

### Option 3: Via Python
```python
import requests

response = requests.post(
    'http://localhost:8000/api/portfolio/analyze',
    json={
        'user_id': 'test_user',
        'filename': 'sample_portfolio.xlsx'
    }
)

data = response.json()
print(f"Total Invested: ₹{data['summary']['total_invested']:,.2f}")
print(f"AI Insights: {data['ai_insights']}")
```

---

## 🐳 CI/CD & DevOps

### GitHub Actions Setup

1. **Add GitHub Secrets** (Repository Settings > Secrets):
   ```
   AWS_ACCESS_KEY_ID
   AWS_SECRET_ACCESS_KEY
   GEMINI_API_KEY
   DOCKER_USERNAME
   DOCKER_PASSWORD
   ```

2. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add portfolio analysis feature"
   git push origin main
   ```

3. **Workflows will automatically**:
   - Run tests
   - Build Docker images
   - Deploy to AWS with Terraform
   - Send notifications

### Manual Docker Build

```bash
# Build backend image
docker build -f Dockerfile.python -t vittcott-backend .

# Run container
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  vittcott-backend
```

### Terraform Deployment

```bash
cd terraform
terraform init
terraform plan -var="environment=production"
terraform apply
```

---

## 🎯 Features

### Portfolio Metrics
- ✅ Total invested amount
- ✅ Current portfolio value
- ✅ Profit/Loss (absolute & %)
- ✅ Winner/Loser count
- ✅ Allocation percentages

### Visualizations
- ✅ Interactive pie chart
- ✅ Color-coded P&L (green/red)
- ✅ Responsive design
- ✅ Dark theme

### AI Insights (Powered by Gemini)
- ✅ Diversification analysis
- ✅ Risk assessment
- ✅ Actionable recommendations
- ✅ Market outlook

---

## 🔍 Troubleshooting

### Error: "Portfolio file not found"
**Fix**: Verify S3 path is `s3://YOUR_BUCKET/portfolios/{user_id}/{filename}`

### Error: "Missing required columns"
**Fix**: Ensure Excel/CSV has `symbol`, `quantity`, `purchase_price` columns

### Error: "GEMINI_API_KEY not set"
**Fix**: Add `GEMINI_API_KEY` to `backend/.env`

### Error: "ModuleNotFoundError: No module named 'pandas'"
**Fix**: Run `pip install -r backend/requirements.txt`

### CORS Error
**Fix**: Backend already configured for `localhost:3000`, verify servers are running

---

## 🌟 What You Get

1. **Beautiful UI** - Dark theme with gradient effects
2. **Real-time Analysis** - Instant portfolio insights
3. **AI-Powered** - Smart recommendations from Gemini
4. **Production Ready** - Full CI/CD pipeline
5. **Scalable** - Cloud-native with S3 and Docker

---

## 📈 Next Steps

1. **Test with your data**: Upload your actual portfolio
2. **Customize AI prompts**: Edit `services/portfolio_service.py`
3. **Add features**: Historical charts, comparisons, alerts
4. **Deploy**: Use GitHub Actions to deploy to production

---

## 📚 Full Documentation

See `PORTFOLIO_IMPLEMENTATION.md` for:
- Detailed architecture
- API documentation
- Advanced configuration
- Deployment guides
- Customization options

---

## 💡 Example Usage Flow

```
1. User uploads portfolio.xlsx to S3
   └─> s3://vittcott-portfolios/portfolios/user123/

2. User opens portfolio.html
   └─> Enters user_id and filename

3. Frontend calls POST /api/portfolio/analyze
   └─> Backend fetches from S3
   └─> Parses Excel with pandas
   └─> Calculates metrics
   └─> Calls Gemini AI for insights
   └─> Returns JSON response

4. Frontend displays:
   └─> Pie chart (allocation)
   └─> Summary metrics
   └─> Holdings table
   └─> AI insights
```

---

**🎉 You're all set! Your portfolio analysis system is ready to use.**

Questions? Check `PORTFOLIO_IMPLEMENTATION.md` or review the code comments.

Built with ❤️ using FastAPI, Gemini AI, Pandas, and Chart.js
