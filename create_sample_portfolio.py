"""Create sample portfolio file for testing"""
import pandas as pd

# Sample portfolio data
data = {
    'symbol': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'JPM', 'V', 'WMT'],
    'quantity': [10, 5, 15, 8, 12, 20, 7, 25, 18, 30],
    'purchase_price': [150.00, 2800.00, 300.00, 3200.00, 700.00, 450.00, 320.00, 140.00, 220.00, 145.00],
    'current_price': [175.50, 2950.00, 380.00, 3350.00, 850.00, 485.00, 340.00, 150.00, 240.00, 152.00]
}

df = pd.DataFrame(data)

# Save as Excel
df.to_excel('sample_portfolio.xlsx', index=False)
print("✅ Sample portfolio created: sample_portfolio.xlsx")
print(f"\nPortfolio Summary:")
print(f"- Stocks: {len(df)}")
print(f"- Total Invested: ${(df['quantity'] * df['purchase_price']).sum():,.2f}")
print(f"- Current Value: ${(df['quantity'] * df['current_price']).sum():,.2f}")
print(f"- Profit: ${((df['quantity'] * df['current_price']) - (df['quantity'] * df['purchase_price'])).sum():,.2f}")

# Also save as CSV
df.to_csv('sample_portfolio.csv', index=False)
print("\n✅ Also created: sample_portfolio.csv")
