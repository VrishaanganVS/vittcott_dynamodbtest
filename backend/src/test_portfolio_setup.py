"""Test portfolio functionality"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print("✅ Testing Portfolio Implementation\n")

# Test 1: Import modules
print("1. Testing imports...")
try:
    from services.portfolio_service import portfolio_service
    from models.portfolio_models import PortfolioAnalysisRequest
    from routes.portfolio import router
    print("   ✓ All modules imported successfully")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Check pandas
print("\n2. Testing pandas...")
try:
    import pandas as pd
    df = pd.DataFrame({
        'symbol': ['AAPL', 'GOOGL'],
        'quantity': [10, 5],
        'purchase_price': [150.0, 2800.0],
        'current_price': [175.0, 2950.0]
    })
    print(f"   ✓ Pandas working - created test DataFrame with {len(df)} rows")
except Exception as e:
    print(f"   ✗ Pandas test failed: {e}")

# Test 3: Analyze sample data
print("\n3. Testing portfolio analysis...")
try:
    analysis = portfolio_service.analyze_portfolio(df)
    summary = analysis['summary']
    print(f"   ✓ Analysis successful:")
    print(f"     - Total Invested: ₹{summary['total_invested']:,.2f}")
    print(f"     - Stocks: {summary['total_stocks']}")
    print(f"     - Total P&L: ₹{summary['total_profit_loss']:,.2f}")
    print(f"     - Return: {summary['total_return_pct']:.2f}%")
except Exception as e:
    print(f"   ✗ Analysis failed: {e}")

# Test 4: Check boto3
print("\n4. Testing AWS SDK (boto3)...")
try:
    import boto3
    print("   ✓ boto3 imported successfully")
    print("   ℹ S3 client will be initialized when credentials are configured")
except Exception as e:
    print(f"   ✗ boto3 test failed: {e}")

# Test 5: Check environment
print("\n5. Checking configuration...")
try:
    from config import settings
    has_aws = bool(settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY)
    has_gemini = bool(settings.GEMINI_API_KEY)
    
    print(f"   - AWS credentials: {'✓ Configured' if has_aws else '✗ Not set'}")
    print(f"   - Gemini API key: {'✓ Configured' if has_gemini else '✗ Not set'}")
    print(f"   - S3 bucket: {settings.S3_PORTFOLIO_BUCKET}")
    print(f"   - AWS region: {settings.AWS_REGION}")
except Exception as e:
    print(f"   ✗ Config check failed: {e}")

print("\n" + "="*50)
print("Portfolio implementation test completed!")
print("="*50)
print("\n📝 Next steps:")
print("1. Update .env with AWS credentials")
print("2. Upload portfolio to S3")
print("3. Start server: python -m uvicorn main:app --reload")
print("4. Test at: http://localhost:3000/pages/portfolio.html")
