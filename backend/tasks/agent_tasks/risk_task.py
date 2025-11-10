"""
Risk Analysis Celery Task - Enhanced
Integrates enhanced Risk Agent with market correlation
"""
from core import celery_app
import asyncio
from agents.risk_agent import RiskAgent
from api.models.schemas import PortfolioInput

@celery_app.task(bind=True, name="risk_analysis")
def risk_task(self, wallet_address: str, network: str = "mantle", market_correlation: float = None):
    """
    Enhanced background task for portfolio risk analysis
    
    Args:
        wallet_address: Wallet address to analyze
        network: Blockchain network (default: mantle)
        market_correlation: Optional market correlation from Macro Agent (0-1)
    
    Returns:
        dict: Risk analysis results with market context
    """
    try:
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Analyzing portfolio risk...', 'progress': 0}
        )
        
        print(f'Running enhanced risk analysis for wallet: {wallet_address}')
        if market_correlation is not None:
            print(f'Market correlation: {market_correlation:.2f}')
        
        # Initialize Risk Agent
        risk_agent = RiskAgent()
        
        # Run async agent code
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Calculating risk factors with market context...', 'progress': 50}
        )
        
        # Execute enhanced risk analysis with correlation
        risk_score = loop.run_until_complete(
            risk_agent.analyze_portfolio(wallet_address, market_correlation)
        )
        loop.close()
        
        print(f'Risk analysis completed: Score {risk_score.score}, Market: {risk_score.market_condition}')
        
        # Return structured result
        return {
            'status': 'completed',
            'wallet_address': wallet_address,
            'network': network,
            'risk_analysis': risk_score.dict(),
            'market_condition': risk_score.market_condition,
            'agent': 'risk',
            'version': '2.0_enhanced'
        }
        
    except Exception as e:
        print(f'Risk analysis failed: {str(e)}')
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        
        return {
            'status': 'failed',
            'error': str(e),
            'agent': 'risk'
        }
