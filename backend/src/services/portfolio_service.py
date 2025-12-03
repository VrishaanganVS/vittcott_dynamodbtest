"""
Portfolio Service - Handles S3 portfolio fetching and analysis
"""
import io
import pandas as pd
import boto3
from typing import Dict, List, Optional
from config import settings
from config.logging_config import logger

class PortfolioService:
    def __init__(self):
        """Initialize S3 client"""
        self.s3_client = boto3.client(
            's3',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.bucket_name = settings.S3_PORTFOLIO_BUCKET
    
    async def fetch_portfolio_from_s3(self, user_id: str, filename: str) -> pd.DataFrame:
        """
        Fetch portfolio file from S3 and parse it
        
        Args:
            user_id: User ID for S3 folder structure
            filename: Portfolio filename
            
        Returns:
            DataFrame with portfolio data
        """
        try:
            # S3 key structure: users/{user_id}/{filename}
            s3_key = f"users/{user_id}/{filename}"
            
            logger.info(f"Fetching portfolio from S3: {s3_key}")
            
            # Download file from S3
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            # Read file content
            file_content = response['Body'].read()
            
            # Parse based on file extension
            if filename.endswith('.xlsx') or filename.endswith('.xls'):
                # Read Excel file and auto-detect header row
                df = self._read_excel_with_auto_header(io.BytesIO(file_content))
            elif filename.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(file_content))
            else:
                raise ValueError(f"Unsupported file format: {filename}")
            
            # Normalize column names to handle different formats (Groww, Zerodha, etc.)
            df = self._normalize_columns(df)
            
            logger.info(f"Successfully parsed portfolio with {len(df)} rows")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching portfolio from S3: {str(e)}")
            raise
    
    async def list_user_portfolios(self, user_id: str) -> List[Dict[str, str]]:
        """
        List all portfolio files for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List of portfolio files with metadata
        """
        try:
            prefix = f"users/{user_id}/"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            portfolios = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    # Skip folder markers
                    if obj['Key'].endswith('/'):
                        continue
                    
                    filename = obj['Key'].split('/')[-1]
                    portfolios.append({
                        'filename': filename,
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        's3_key': obj['Key']
                    })
            
            return portfolios
            
        except Exception as e:
            logger.error(f"Error listing portfolios: {str(e)}")
            raise
    
    def _read_excel_with_auto_header(self, file_content) -> pd.DataFrame:
        """
        Read Excel file and automatically detect the header row.
        Handles files with title rows, summary rows, etc. (Groww format)
        """
        # Read all rows without headers first
        df_raw = pd.read_excel(file_content, header=None)
        file_content.seek(0)
        
        # Look for the row containing "Stock Name" and "Quantity"
        for i in range(len(df_raw)):
            row_values = [str(x).lower() for x in df_raw.iloc[i].values if pd.notna(x)]
            row_str = ' '.join(row_values)
            
            # Check if this row has stock data headers
            if 'stock' in row_str and 'quantity' in row_str and ('average' in row_str or 'price' in row_str):
                logger.info(f"Found stock data headers at row {i}")
                # Read the file with the correct header row
                df = pd.read_excel(file_content, skiprows=i)
                file_content.seek(0)
                
                # Remove any completely empty rows
                df = df.dropna(how='all')
                
                # Remove rows where Stock Name is NaN
                if 'Stock Name' in df.columns:
                    df = df[df['Stock Name'].notna()]
                elif df.columns[0] in ['Stock Name', 'stock name', 'Stock name']:
                    df = df[df[df.columns[0]].notna()]
                
                return df
        
        # If no specific header found, use default
        file_content.seek(0)
        logger.warning("No stock data headers found, using default parsing")
        return pd.read_excel(file_content)
    
    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize column names from different broker formats to standard format
        
        Standard format:
        - symbol: Stock symbol/name
        - quantity: Number of shares
        - purchase_price: Average buy price per share
        - current_price: Current market price (optional)
        
        Supported formats:
        - Groww: 'Stock Name', 'Quantity', 'Average buy price', 'Closing price'
        - Zerodha: 'Tradingsymbol', 'Quantity', 'Average price', 'LTP'
        - Generic: 'symbol', 'quantity', 'purchase_price', 'current_price'
        """
        # Column mapping for different formats
        column_mappings = {
            # Groww format
            'Stock Name': 'symbol',
            'stock name': 'symbol',
            'Quantity': 'quantity',
            'quantity': 'quantity',
            'Average buy price': 'purchase_price',
            'average buy price': 'purchase_price',
            'Closing price': 'current_price',
            'closing price': 'current_price',
            'Closing Price': 'current_price',
            
            # Zerodha format
            'Tradingsymbol': 'symbol',
            'tradingsymbol': 'symbol',
            'Average price': 'purchase_price',
            'average price': 'purchase_price',
            'LTP': 'current_price',
            'ltp': 'current_price',
            
            # Standard format (already correct)
            'symbol': 'symbol',
            'Symbol': 'symbol',
            'purchase_price': 'purchase_price',
            'current_price': 'current_price'
        }
        
        # Rename columns based on mapping
        df_renamed = df.rename(columns=column_mappings)
        
        # Verify required columns exist
        required_cols = ['symbol', 'quantity', 'purchase_price']
        missing_cols = [col for col in required_cols if col not in df_renamed.columns]
        
        if missing_cols:
            available_cols = list(df.columns)
            raise ValueError(
                f"Missing required columns: {missing_cols}. "
                f"Available columns in file: {available_cols}. "
                f"Please ensure your file has: Stock Name, Quantity, and Average buy price (or equivalent)."
            )
        
        # Keep only relevant columns
        keep_cols = ['symbol', 'quantity', 'purchase_price']
        if 'current_price' in df_renamed.columns:
            keep_cols.append('current_price')
        
        return df_renamed[keep_cols]
    
    async def analyze_portfolio(self, df: pd.DataFrame) -> Dict:
        """
        Analyze portfolio data and calculate metrics
        
        Expected columns: symbol, quantity, purchase_price, current_price (optional)
        
        Args:
            df: Portfolio DataFrame (already normalized)
            
        Returns:
            Dictionary with analysis metrics
        """
        try:
            # Calculate investment value
            df['invested_value'] = df['quantity'] * df['purchase_price']
            
            # If current_price exists, calculate current value and P&L
            if 'current_price' in df.columns:
                df['current_value'] = df['quantity'] * df['current_price']
                df['profit_loss'] = df['current_value'] - df['invested_value']
                df['profit_loss_pct'] = (df['profit_loss'] / df['invested_value']) * 100
            
            # Calculate allocation percentages
            total_invested = df['invested_value'].sum()
            df['allocation_pct'] = (df['invested_value'] / total_invested) * 100
            
            # Prepare pie chart data
            pie_data = []
            for _, row in df.iterrows():
                pie_data.append({
                    'symbol': row['symbol'],
                    'value': float(row['invested_value']),
                    'percentage': float(row['allocation_pct']),
                    'quantity': int(row['quantity'])
                })
            
            # Calculate summary metrics
            summary = {
                'total_invested': float(total_invested),
                'total_stocks': len(df),
                'pie_chart_data': pie_data
            }
            
            # Add current value metrics if available
            if 'current_value' in df.columns:
                total_current = df['current_value'].sum()
                total_pl = df['profit_loss'].sum()
                
                summary.update({
                    'total_current_value': float(total_current),
                    'total_profit_loss': float(total_pl),
                    'total_return_pct': float((total_pl / total_invested) * 100),
                    'winners': int((df['profit_loss'] > 0).sum()),
                    'losers': int((df['profit_loss'] < 0).sum())
                })
            
            # Detailed holdings
            holdings = []
            for _, row in df.iterrows():
                holding = {
                    'symbol': row['symbol'],
                    'quantity': int(row['quantity']),
                    'purchase_price': float(row['purchase_price']),
                    'invested_value': float(row['invested_value']),
                    'allocation_pct': float(row['allocation_pct'])
                }
                
                if 'current_price' in df.columns:
                    holding.update({
                        'current_price': float(row['current_price']),
                        'current_value': float(row['current_value']),
                        'profit_loss': float(row['profit_loss']),
                        'profit_loss_pct': float(row['profit_loss_pct'])
                    })
                
                holdings.append(holding)
            
            return {
                'summary': summary,
                'holdings': holdings
            }
            
        except Exception as e:
            logger.error(f"Error analyzing portfolio: {str(e)}")
            raise
    
    async def generate_ai_insights(self, analysis: Dict, model) -> str:
        """
        Generate AI insights using Gemini
        
        Args:
            analysis: Portfolio analysis data
            model: Gemini model instance
            
        Returns:
            AI-generated insights text
        """
        try:
            summary = analysis['summary']
            holdings = analysis['holdings']
            
            # Build prompt for AI
            prompt = f"""Analyze this investment portfolio and provide insights:

**Portfolio Summary:**
- Total Invested: ₹{summary['total_invested']:,.2f}
- Number of Stocks: {summary['total_stocks']}

**Top Holdings:**
{self._format_holdings_for_ai(holdings[:5])}

Please provide:
1. **Diversification Analysis**: Comment on the portfolio concentration and diversification
2. **Risk Assessment**: Identify potential risks based on allocation
3. **Recommendations**: Suggest 2-3 actionable improvements
4. **Market Outlook**: Brief perspective on the holdings

Keep the response concise (max 300 words) and actionable."""

            # Add P&L context if available
            if 'total_profit_loss' in summary:
                prompt += f"""

**Performance Metrics:**
- Current Value: ₹{summary['total_current_value']:,.2f}
- Total P&L: ₹{summary['total_profit_loss']:,.2f} ({summary['total_return_pct']:.2f}%)
- Winners: {summary['winners']} | Losers: {summary['losers']}
"""
            
            # Generate AI response
            response = model.generate_content(prompt)
            insights = response.text
            
            logger.info("AI insights generated successfully")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {str(e)}")
            return "Unable to generate AI insights at this time. Please try again later."
    
    def _format_holdings_for_ai(self, holdings: List[Dict]) -> str:
        """Format holdings for AI prompt"""
        lines = []
        for h in holdings:
            line = f"- {h['symbol']}: {h['allocation_pct']:.1f}% (₹{h['invested_value']:,.0f})"
            if 'profit_loss_pct' in h:
                line += f" | P&L: {h['profit_loss_pct']:+.2f}%"
            lines.append(line)
        return "\n".join(lines)


# Singleton instance
portfolio_service = PortfolioService()
