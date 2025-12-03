from fastapi import APIRouter, HTTPException
import httpx
import os
from datetime import datetime
import asyncio

router = APIRouter()

FINNHUB_API_KEY = os.getenv('FINANCEHUB_API_KEY', '')
FINNHUB_BASE_URL = 'https://finnhub.io/api/v1'

# Top US stocks (Finnhub free tier supports these)
INDIAN_STOCKS = {
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft Corporation',
    'GOOGL': 'Alphabet Inc.',
    'AMZN': 'Amazon.com Inc.',
    'NVDA': 'NVIDIA Corporation',
    'META': 'Meta Platforms Inc.',
    'TSLA': 'Tesla Inc.',
    'JPM': 'JPMorgan Chase & Co.',
    'V': 'Visa Inc.',
    'WMT': 'Walmart Inc.'
}

async def fetch_quote(client: httpx.AsyncClient, symbol: str, name: str):
    """Fetch stock quote from Finnhub"""
    try:
        response = await client.get(
            f"{FINNHUB_BASE_URL}/quote",
            params={'symbol': symbol, 'token': FINNHUB_API_KEY},
            timeout=15.0
        )
        
        if response.status_code == 200:
            data = response.json()
            
            current = data.get('c', 0)
            prev_close = data.get('pc', 0)
            high = data.get('h', 0)
            low = data.get('l', 0)
            open_price = data.get('o', 0)
            timestamp = data.get('t', 0)
            
            # Calculate change
            change = ((current - prev_close) / prev_close * 100) if prev_close else 0
            
            # Market status (if current price is 0, market is closed)
            is_market_open = current > 0
            
            return {
                'symbol': symbol.replace('.NS', ''),
                'name': name,
                'price': round(current if current else prev_close, 2),
                'change': round(change, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'open': round(open_price, 2),
                'previousClose': round(prev_close, 2),
                'isMarketOpen': is_market_open,
                'timestamp': timestamp
            }
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

@router.get("/stocks/live")
async def get_live_stocks():
    """Get real-time stock data from Finnhub API"""
    
    if not FINNHUB_API_KEY:
        raise HTTPException(status_code=500, detail="Finnhub API key not configured")
    
    stocks_data = []
    
    async with httpx.AsyncClient() as client:
        tasks = [fetch_quote(client, symbol, name) for symbol, name in INDIAN_STOCKS.items()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, dict):
                stocks_data.append(result)
    
    if not stocks_data:
        raise HTTPException(status_code=503, detail="Unable to fetch stock data")
    
    # Check if market is open
    market_status = any(stock.get('isMarketOpen') for stock in stocks_data)
    
    return {
        "stocks": stocks_data,
        "count": len(stocks_data),
        "marketOpen": market_status,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/stocks/indices")
async def get_market_indices():
    """Get US market indices"""
    
    if not FINNHUB_API_KEY:
        raise HTTPException(status_code=500, detail="Finnhub API key not configured")
    
    indices_symbols = {
        '^GSPC': 'S&P 500',
        '^DJI': 'Dow Jones',
        '^IXIC': 'NASDAQ'
    }
    
    indices_data = []
    
    async with httpx.AsyncClient() as client:
        tasks = [
            client.get(
                f"{FINNHUB_BASE_URL}/quote",
                params={'symbol': symbol, 'token': FINNHUB_API_KEY},
                timeout=15.0
            )
            for symbol in indices_symbols.keys()
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for (symbol, name), response in zip(indices_symbols.items(), responses):
            try:
                if isinstance(response, Exception):
                    continue
                    
                if response.status_code == 200:
                    data = response.json()
                    current = data.get('c', 0)
                    prev_close = data.get('pc', 0)
                    
                    # Use previous close if current is 0
                    price = current if current > 0 else prev_close
                    change = ((current - prev_close) / prev_close * 100) if prev_close > 0 else 0
                    
                    if price > 0:  # Only add if we have valid price data
                        indices_data.append({
                            'symbol': symbol,
                            'name': name,
                            'price': round(price, 2),
                            'change': round(change, 2)
                        })
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
                continue
    
    return {
        "indices": indices_data,
        "count": len(indices_data)
    }
