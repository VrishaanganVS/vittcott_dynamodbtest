"""Portfolio API Routes"""
from fastapi import APIRouter, HTTPException, Request
from typing import List
from models.portfolio_models import (
    PortfolioListResponse,
    PortfolioAnalysisRequest,
    PortfolioAnalysisResponse
)
from services.portfolio_service import portfolio_service
from config.logging_config import logger

router = APIRouter()

@router.get("/portfolios/{user_id}", response_model=PortfolioListResponse)
async def list_user_portfolios(user_id: str):
    """
    List all portfolio files for a user
    
    GET /api/portfolios/{user_id}
    """
    try:
        portfolios = await portfolio_service.list_user_portfolios(user_id)
        
        return PortfolioListResponse(
            portfolios=portfolios,
            count=len(portfolios)
        )
        
    except Exception as e:
        logger.error(f"Error listing portfolios: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/portfolio/analyze", response_model=PortfolioAnalysisResponse)
async def analyze_portfolio(request_body: PortfolioAnalysisRequest, app_request: Request):
    """
    Analyze a portfolio file and generate insights
    
    POST /api/portfolio/analyze
    Body: {
        "user_id": "user123",
        "filename": "my_portfolio.xlsx"
    }
    """
    try:
        # Fetch portfolio from S3
        logger.info(f"Analyzing portfolio: {request_body.filename} for user: {request_body.user_id}")
        
        df = await portfolio_service.fetch_portfolio_from_s3(
            request_body.user_id,
            request_body.filename
        )
        
        # Analyze portfolio data
        analysis = portfolio_service.analyze_portfolio(df)
        
        # Generate AI insights
        model = app_request.app.state.model
        ai_insights = await portfolio_service.generate_ai_insights(analysis, model)
        
        # Combine results
        response_data = {
            **analysis,
            'ai_insights': ai_insights
        }
        
        return PortfolioAnalysisResponse(**response_data)
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Portfolio file not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/portfolio/sample")
async def get_sample_portfolio():
    """
    Get sample portfolio data structure
    
    GET /api/portfolio/sample
    """
    return {
        "description": "Sample portfolio file structure",
        "format": "Excel (.xlsx) or CSV (.csv)",
        "required_columns": [
            "symbol",
            "quantity",
            "purchase_price"
        ],
        "optional_columns": [
            "current_price"
        ],
        "example": [
            {
                "symbol": "AAPL",
                "quantity": 10,
                "purchase_price": 150.00,
                "current_price": 175.00
            },
            {
                "symbol": "GOOGL",
                "quantity": 5,
                "purchase_price": 2800.00,
                "current_price": 2950.00
            }
        ]
    }
