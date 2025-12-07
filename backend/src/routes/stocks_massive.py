from fastapi import APIRouter, HTTPException
import httpx
import os
from datetime import datetime, timedelta
import asyncio
from typing import Optional, Dict, Any

router = APIRouter()

# API Keys
MASSIVE_API_KEY = os.getenv('STOCKS_API_KEY', '')
FINNHUB_API_KEY = os.getenv('FINANCEHUB_API_KEY', '')

# API Base URLs
MASSIVE_BASE_URL = 'https://api.polygon.io'
FINNHUB_BASE_URL = 'https://finnhub.io/api/v1'

# Top US stocks for live tracking
POPULAR_STOCKS = {
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft Corporation',
    'GOOGL': 'Alphabet Inc.',
    'AMZN': 'Amazon.com Inc.',
    'NVDA': 'NVIDIA Corporation',
    'META': 'Meta Platforms Inc.',
    'TSLA': 'Tesla Inc.',
    'JPM': 'JPMorgan Chase & Co.',
    'V': 'Visa Inc.',
    'WMT': 'Walmart Inc.',
    'JNJ': 'Johnson & Johnson',
    'PG': 'Procter & Gamble',
    'DIS': 'The Walt Disney Company',
    'NFLX': 'Netflix Inc.',
    'ADBE': 'Adobe Inc.'
}

async def fetch_massive_quote(client: httpx.AsyncClient, symbol: str, name: str) -> Optional[Dict[str, Any]]:
    """Fetch stock quote from Massive (Polygon) API - Primary source"""
    try:
        # Get previous day's data
        response = await client.get(
            f"{MASSIVE_BASE_URL}/v2/aggs/ticker/{symbol}/prev",
            params={'apiKey': MASSIVE_API_KEY},
            timeout=15.0
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'OK' and data.get('results'):
                result = data['results'][0]
                
                open_price = result.get('o', 0)
                high = result.get('h', 0)
                low = result.get('l', 0)
                close = result.get('c', 0)
                volume = result.get('v', 0)
                vwap = result.get('vw', 0)  # Volume Weighted Average Price
                
                # Get current day quote for real-time price
                current_response = await client.get(
                    f"{MASSIVE_BASE_URL}/v2/snapshot/locale/us/markets/stocks/tickers/{symbol}",
                    params={'apiKey': MASSIVE_API_KEY},
                    timeout=15.0
                )
                
                current_price = close
                change_percent = 0
                
                if current_response.status_code == 200:
                    current_data = current_response.json()
                    if current_data.get('status') == 'OK' and current_data.get('ticker'):
                        ticker_data = current_data['ticker']
                        current_price = ticker_data.get('day', {}).get('c', close)
                        prev_close = ticker_data.get('prevDay', {}).get('c', close)
                        change_percent = ((current_price - prev_close) / prev_close * 100) if prev_close else 0
                
                return {
                    'symbol': symbol,
                    'name': name,
                    'price': round(current_price, 2),
                    'change': round(change_percent, 2),
                    'high': round(high, 2),
                    'low': round(low, 2),
                    'open': round(open_price, 2),
                    'volume': int(volume),
                    'vwap': round(vwap, 2),
                    'previousClose': round(close, 2),
                    'isMarketOpen': True,
                    'source': 'Massive API',
                    'timestamp': result.get('t', 0)
                }
    except Exception as e:
        print(f"Massive API error for {symbol}: {e}")
        return None

async def fetch_finnhub_quote(client: httpx.AsyncClient, symbol: str, name: str) -> Optional[Dict[str, Any]]:
    """Fetch stock quote from FinanceHub API - Fallback source"""
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
            
            change = ((current - prev_close) / prev_close * 100) if prev_close else 0
            is_market_open = current > 0
            
            return {
                'symbol': symbol,
                'name': name,
                'price': round(current if current else prev_close, 2),
                'change': round(change, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'open': round(open_price, 2),
                'volume': 0,  # FinanceHub doesn't provide volume in quote
                'vwap': 0,
                'previousClose': round(prev_close, 2),
                'isMarketOpen': is_market_open,
                'source': 'FinanceHub API',
                'timestamp': timestamp
            }
    except Exception as e:
        print(f"FinanceHub API error for {symbol}: {e}")
        return None

async def fetch_stock_with_fallback(client: httpx.AsyncClient, symbol: str, name: str) -> Optional[Dict[str, Any]]:
    """Fetch stock data with automatic fallback"""
    # Try Massive API first
    if MASSIVE_API_KEY:
        result = await fetch_massive_quote(client, symbol, name)
        if result:
            return result
    
    # Fallback to FinanceHub
    if FINNHUB_API_KEY:
        result = await fetch_finnhub_quote(client, symbol, name)
        if result:
            return result
    
    return None

@router.get("/stocks/live")
async def get_live_stocks():
    """Get real-time stock data with Massive API (fallback to FinanceHub)"""
    
    if not MASSIVE_API_KEY and not FINNHUB_API_KEY:
        raise HTTPException(status_code=500, detail="No stock API keys configured")
    
    stocks_data = []
    
    async with httpx.AsyncClient() as client:
        tasks = [fetch_stock_with_fallback(client, symbol, name) for symbol, name in POPULAR_STOCKS.items()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, dict):
                stocks_data.append(result)
    
    if not stocks_data:
        raise HTTPException(status_code=503, detail="Unable to fetch stock data from any source")
    
    # Check API source being used
    api_source = stocks_data[0].get('source', 'Unknown') if stocks_data else 'Unknown'
    market_status = any(stock.get('isMarketOpen') for stock in stocks_data)
    
    return {
        "stocks": stocks_data,
        "count": len(stocks_data),
        "marketOpen": market_status,
        "apiSource": api_source,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/stocks/search/{query}")
async def search_stocks(query: str):
    """Search for stocks by symbol or name"""
    
    if not MASSIVE_API_KEY:
        raise HTTPException(status_code=500, detail="Massive API key not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{MASSIVE_BASE_URL}/v3/reference/tickers",
                params={
                    'search': query,
                    'market': 'stocks',
                    'active': 'true',
                    'limit': 10,
                    'apiKey': MASSIVE_API_KEY
                },
                timeout=15.0
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                stocks = [{
                    'symbol': r.get('ticker'),
                    'name': r.get('name'),
                    'market': r.get('market'),
                    'type': r.get('type'),
                    'active': r.get('active')
                } for r in results]
                
                return {"results": stocks, "count": len(stocks)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/stocks/details/{symbol}")
async def get_stock_details(symbol: str):
    """Get detailed information about a specific stock"""
    
    if not MASSIVE_API_KEY:
        raise HTTPException(status_code=500, detail="Massive API key not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            # Get ticker details
            details_response = await client.get(
                f"{MASSIVE_BASE_URL}/v3/reference/tickers/{symbol}",
                params={'apiKey': MASSIVE_API_KEY},
                timeout=15.0
            )
            
            if details_response.status_code != 200:
                raise HTTPException(status_code=404, detail="Stock not found")
            
            details_data = details_response.json()
            results = details_data.get('results', {})
            
            return {
                'symbol': results.get('ticker'),
                'name': results.get('name'),
                'market': results.get('market'),
                'locale': results.get('locale'),
                'primaryExchange': results.get('primary_exchange'),
                'type': results.get('type'),
                'active': results.get('active'),
                'currencyName': results.get('currency_name'),
                'description': results.get('description'),
                'marketCap': results.get('market_cap'),
                'phoneNumber': results.get('phone_number'),
                'address': results.get('address', {}),
                'homepage': results.get('homepage_url'),
                'totalEmployees': results.get('total_employees')
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stock details: {str(e)}")

@router.get("/stocks/chart/{symbol}")
async def get_stock_chart_data(symbol: str, timespan: str = "day", range: str = "1"):
    """Get historical chart data for a stock
    
    Args:
        symbol: Stock symbol
        timespan: minute, hour, day, week, month, quarter, year
        range: Number of timespans (e.g., "5" for 5 days)
    """
    
    if not MASSIVE_API_KEY:
        raise HTTPException(status_code=500, detail="Massive API key not configured")
    
    try:
        # Calculate date range
        end_date = datetime.now()
        
        range_int = int(range)
        if timespan == "day":
            start_date = end_date - timedelta(days=range_int)
        elif timespan == "week":
            start_date = end_date - timedelta(weeks=range_int)
        elif timespan == "month":
            start_date = end_date - timedelta(days=range_int * 30)
        else:
            start_date = end_date - timedelta(days=range_int)
        
        from_date = start_date.strftime('%Y-%m-%d')
        to_date = end_date.strftime('%Y-%m-%d')
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{MASSIVE_BASE_URL}/v2/aggs/ticker/{symbol}/range/1/{timespan}/{from_date}/{to_date}",
                params={
                    'adjusted': 'true',
                    'sort': 'asc',
                    'apiKey': MASSIVE_API_KEY
                },
                timeout=20.0
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'OK' and data.get('results'):
                    chart_data = [{
                        'timestamp': r.get('t'),
                        'date': datetime.fromtimestamp(r.get('t') / 1000).strftime('%Y-%m-%d %H:%M'),
                        'open': r.get('o'),
                        'high': r.get('h'),
                        'low': r.get('l'),
                        'close': r.get('c'),
                        'volume': r.get('v'),
                        'vwap': r.get('vw')
                    } for r in data['results']]
                    
                    return {
                        'symbol': symbol,
                        'timespan': timespan,
                        'range': range,
                        'data': chart_data,
                        'count': len(chart_data)
                    }
                else:
                    raise HTTPException(status_code=404, detail="No chart data available")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch chart data: {str(e)}")

@router.get("/stocks/api-status")
async def get_api_status():
    """Check which API is currently being used"""
    
    status = {
        'massiveConfigured': bool(MASSIVE_API_KEY),
        'finnhubConfigured': bool(FINNHUB_API_KEY),
        'primaryAPI': 'Massive' if MASSIVE_API_KEY else 'FinanceHub' if FINNHUB_API_KEY else 'None',
        'fallbackAvailable': bool(MASSIVE_API_KEY and FINNHUB_API_KEY)
    }
    
    return status
