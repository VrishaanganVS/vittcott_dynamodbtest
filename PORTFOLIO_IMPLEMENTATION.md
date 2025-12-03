# VITTCOTT Portfolio Analysis - Implementation Guide

## 🎯 What We've Built

A complete portfolio analysis system with:
- **S3 Integration**: Fetch portfolio files from AWS S3
- **AI Analysis**: Gemini-powered insights and recommendations  
- **Pie Chart Visualization**: Interactive Chart.js portfolio breakdown
- **CI/CD Pipeline**: Automated testing and deployment with GitHub Actions

---

## 📋 Architecture Overview

```
User Uploads Portfolio → S3 Bucket (portfolios/{user_id}/{filename})
                            ↓
Frontend (portfolio.html) → Backend API (/api/portfolio/analyze)
                            ↓
Portfolio Service → Fetch from S3 → Parse Excel/CSV
                            ↓
                      Analyze Data → Calculate metrics
                            ↓
                      Gemini AI → Generate insights
                            ↓
                      Return JSON → Frontend displays charts & insights
```

---

## 🚀 Quick Start

### 1. Environment Setup

Update your `.env` file with:
```bash
# AWS Configuration
AWS_REGION=ap-south-1
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
S3_PORTFOLIO_BUCKET=vittcott-portfolios

# AI
GEMINI_API_KEY=your_gemini_key
```

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

New dependencies added:
- `pandas` - Data analysis
- `openpyxl` - Excel file parsing
- `boto3` - AWS SDK

### 3. S3 Bucket Structure

Upload your portfolio files to S3 with this structure:
```
s3://vittcott-portfolios/
  └── portfolios/
      └── {user_id}/
          ├── my_portfolio.xlsx
          ├── portfolio_2024.csv
          └── ...
```

### 4. Portfolio File Format

**Required columns:**
- `symbol` - Stock symbol (e.g., AAPL, GOOGL)
- `quantity` - Number of shares
- `purchase_price` - Price per share when purchased

**Optional columns:**
- `current_price` - Current market price (enables P&L calculation)

**Example (Excel or CSV):**
```csv
symbol,quantity,purchase_price,current_price
AAPL,10,150.00,175.50
GOOGL,5,2800.00,2950.00
MSFT,15,300.00,380.00
```

### 5. Start the Server

```bash
cd backend/src
python -m uvicorn main:app --reload --port 8000
```

### 6. Access Portfolio Dashboard

Navigate to: `http://localhost:3000/pages/portfolio.html`

---

## 🔧 API Endpoints

### 1. List User Portfolios
```http
GET /api/portfolios/{user_id}
```

**Response:**
```json
{
  "portfolios": [
    {
      "filename": "my_portfolio.xlsx",
      "size": 12345,
      "last_modified": "2025-12-03T10:30:00",
      "s3_key": "portfolios/user123/my_portfolio.xlsx"
    }
  ],
  "count": 1
}
```

### 2. Analyze Portfolio
```http
POST /api/portfolio/analyze
Content-Type: application/json

{
  "user_id": "user123",
  "filename": "my_portfolio.xlsx"
}
```

**Response:**
```json
{
  "summary": {
    "total_invested": 50000.00,
    "total_stocks": 10,
    "total_current_value": 55000.00,
    "total_profit_loss": 5000.00,
    "total_return_pct": 10.00,
    "winners": 7,
    "losers": 3,
    "pie_chart_data": [
      {
        "symbol": "AAPL",
        "value": 15000,
        "percentage": 30.0,
        "quantity": 100
      }
    ]
  },
  "holdings": [...],
  "ai_insights": "Your portfolio shows strong diversification..."
}
```

### 3. Get Sample Format
```http
GET /api/portfolio/sample
```

---

## 🔐 CI/CD Pipeline

### GitHub Actions Workflows

#### 1. Main Pipeline (`.github/workflows/ci-cd.yml`)
Triggered on: Push to `main` branch

**Steps:**
1. **Test Backend** - Run pytest with coverage
2. **Build Frontend** - Compile and bundle assets
3. **Docker Build** - Create and push images to Docker Hub
4. **Terraform Deploy** - Provision AWS infrastructure
5. **Notify** - Send deployment status

#### 2. Development Pipeline (`.github/workflows/dev-ci.yml`)
Triggered on: Push to `develop` or feature branches

**Steps:**
1. **Lint** - flake8 and black formatting checks
2. **Test** - Run unit tests
3. **Report** - Display test results

### Required GitHub Secrets

Add these to your repository settings:

```bash
AWS_ACCESS_KEY_ID          # AWS credentials
AWS_SECRET_ACCESS_KEY      # AWS credentials
GEMINI_API_KEY             # Gemini AI API key
DOCKER_USERNAME            # Docker Hub username
DOCKER_PASSWORD            # Docker Hub password/token
```

---

## 🧪 Testing

### Manual Testing

1. **Upload sample portfolio to S3:**
```bash
aws s3 cp sample_portfolio.xlsx s3://vittcott-portfolios/portfolios/test_user/
```

2. **Test via API:**
```bash
curl -X POST http://localhost:8000/api/portfolio/analyze \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "filename": "sample_portfolio.xlsx"}'
```

3. **Test via UI:**
   - Open `http://localhost:3000/pages/portfolio.html`
   - Enter User ID: `test_user`
   - Enter Filename: `sample_portfolio.xlsx`
   - Click "Analyze Portfolio"

### Automated Testing

```bash
cd backend/src
pytest tests/test_portfolio.py -v
```

---

## 📊 Features

### 1. Portfolio Metrics
- Total invested amount
- Current portfolio value
- Profit/Loss (absolute & percentage)
- Number of winning/losing positions
- Portfolio allocation percentages

### 2. Visualizations
- **Pie Chart**: Interactive allocation breakdown
- **Holdings Table**: Detailed position-by-position view
- **Color-coded P&L**: Green for profits, red for losses

### 3. AI Insights
Gemini AI provides:
- Diversification analysis
- Risk assessment
- Actionable recommendations
- Market outlook

---

## 🐳 Docker Deployment

### Build Images

```bash
# Backend
docker build -f Dockerfile.python -t vittcott-backend .

# Streamlit
docker build -f Dockerfile.streamlit -t vittcott-streamlit .
```

### Run with Docker Compose

```bash
docker-compose up -d
```

---

## 🌍 Terraform Infrastructure

### Deploy S3 Bucket

```bash
cd terraform
terraform init
terraform plan -var="environment=production"
terraform apply
```

This creates:
- S3 bucket with versioning
- CORS configuration
- Public access blocks
- Bucket policies

---

## 📝 Sample Portfolio Generator

Create `create_sample_portfolio.py`:

```python
import pandas as pd

data = {
    'symbol': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA'],
    'quantity': [10, 5, 15, 8, 12],
    'purchase_price': [150.00, 2800.00, 300.00, 3200.00, 700.00],
    'current_price': [175.50, 2950.00, 380.00, 3350.00, 850.00]
}

df = pd.DataFrame(data)
df.to_excel('sample_portfolio.xlsx', index=False)
print("Sample portfolio created!")
```

---

## 🔍 Troubleshooting

### Issue: "Portfolio file not found"
**Solution:** Check S3 bucket structure and user_id/filename

### Issue: "Missing required columns"
**Solution:** Ensure Excel/CSV has `symbol`, `quantity`, `purchase_price`

### Issue: AI insights not loading
**Solution:** Verify GEMINI_API_KEY is set in .env

### Issue: CORS errors
**Solution:** Check backend CORS middleware allows frontend origin

---

## 🎨 Customization

### Change Chart Colors

Edit `portfolio.html` - `generateColors()` function:
```javascript
const baseColors = [
    '#6366f1', // Indigo
    '#8b5cf6', // Purple
    '#ec4899', // Pink
    // Add more colors
];
```

### Modify AI Prompt

Edit `services/portfolio_service.py` - `generate_ai_insights()`:
```python
prompt = f"""Custom prompt here..."""
```

---

## 📈 Future Enhancements

- [ ] Real-time price updates from market APIs
- [ ] Historical performance charts
- [ ] Portfolio comparison features
- [ ] Export reports to PDF
- [ ] Email notifications for portfolio changes
- [ ] Multi-currency support
- [ ] Tax optimization suggestions

---

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Chart.js Documentation](https://www.chartjs.org/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/)

---

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review API documentation
3. Check application logs: `logs/backend.log`

---

**Built with ❤️ using FastAPI, Gemini AI, and Chart.js**
