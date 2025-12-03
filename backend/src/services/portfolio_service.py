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
            # S3 key structure: portfolios/{user_id}/{filename}
            s3_key = f"portfolios/{user_id}/{filename}"
            
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
                df = pd.read_excel(io.BytesIO(file_content))
            elif filename.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(file_content))
            else:
                raise ValueError(f"Unsupported file format: {filename}")
            
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
            prefix = f"portfolios/{user_id}/"
            
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
    
    def analyze_portfolio(self, df: pd.DataFrame) -> Dict:
        """
        Analyze portfolio data and calculate metrics
        
        Expected columns: symbol, quantity, purchase_price, current_price
        
        Args:
            df: Portfolio DataFrame
            
        Returns:
            Dictionary with analysis metrics
        """
        try:
            # Ensure required columns exist
            required_cols = ['symbol', 'quantity', 'purchase_price']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                # Try case-insensitive matching
                df.columns = df.columns.str.lower().str.strip()
                missing_cols = [col for col in required_cols if col not in df.columns]
                
                if missing_cols:
                    raise ValueError(f"Missing required columns: {missing_cols}")
            
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
