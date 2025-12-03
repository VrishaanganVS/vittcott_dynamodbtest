import pandas as pd

# Read the file
df = pd.read_excel('holdings_test.xlsx', header=None)

print('\n📋 ALL rows of the file:')
print('='*100)
for idx, row in df.iterrows():
    print(f"Row {idx}: {row.tolist()}")

print('\n\n🔍 Searching for "Stock Name" header row...')
for i in range(len(df)):
    row_values = [str(x).lower() for x in df.iloc[i].values if pd.notna(x)]
    row_str = ' '.join(row_values)
    if 'stock' in row_str and ('quantity' in row_str or 'average' in row_str):
        print(f'\n✅ Found stock data headers at row {i}!')
        print(f'Header row: {df.iloc[i].tolist()}')
        
        # Read with correct header
        df_clean = pd.read_excel('holdings_test.xlsx', skiprows=i)
        print(f'\n📊 Columns: {df_clean.columns.tolist()}')
        print(f'\n📈 Stock data:')
        print(df_clean.dropna(how='all').to_string())
        break
