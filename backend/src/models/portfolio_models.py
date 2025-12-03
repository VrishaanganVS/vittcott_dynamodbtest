"""Portfolio models for request/response"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class PortfolioListResponse(BaseModel):
    portfolios: List[Dict[str, Any]]
    count: int

class PortfolioAnalysisRequest(BaseModel):
    user_id: str
    filename: str

class PieChartData(BaseModel):
    symbol: str
    value: float
    percentage: float
    quantity: int

class PortfolioSummary(BaseModel):
    total_invested: float
    total_stocks: int
    total_current_value: Optional[float] = None
    total_profit_loss: Optional[float] = None
    total_return_pct: Optional[float] = None
    winners: Optional[int] = None
    losers: Optional[int] = None
    pie_chart_data: List[PieChartData]

class HoldingDetail(BaseModel):
    symbol: str
    quantity: int
    purchase_price: float
    invested_value: float
    allocation_pct: float
    current_price: Optional[float] = None
    current_value: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_loss_pct: Optional[float] = None

class PortfolioAnalysisResponse(BaseModel):
    summary: PortfolioSummary
    holdings: List[HoldingDetail]
    ai_insights: str
