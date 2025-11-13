"""
Macro Market Analysis Celery Task - With Alert Triggering
"""
from core import celery_app
import asyncio
# REMOVE THIS LINE: from services.alert_manager import AlertManager


@celery_app.task(bind=True, name="macro_analysis")
def macro_task(self, protocol: str = None, alert_on_correlation: bool = True):
    """
    Macro market analysis with Mantle protocol correlation
    """
    try:
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Fetching macro indicators...', 'progress': 0}
        )
        
        print(f'Running macro analysis for protocol: {protocol or "all"}')
        
        # Lazy import to avoid circular dependency
        from services.alert_manager import AlertManager
        from agents.macro_agent import MacroAgent
        
        # Initialize agents
        macro_agent = MacroAgent()
        alert_manager = AlertManager()
        
        # Run async analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Analyzing market correlations...', 'progress': 40}
        )
        
        # Execute macro analysis (placeholder)
        # TODO: Implement actual macro analysis
        macro_result = {
            'market_condition': 'bullish',
            'correlation_score': 0.8,
            'yield_impact': 'positive'
        }
        
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Checking correlation alerts...', 'progress': 80}
        )
        
        # Trigger alerts for significant market shifts (placeholder)
        triggered_alerts = []
        
        loop.close()
        
        print(f'Macro analysis completed: {macro_result["market_condition"]}')
        print(f'Triggered {len(triggered_alerts)} macro alerts')
        
        return {
            'status': 'completed',
            'protocol': protocol or 'all_mantle_protocols',
            'macro_analysis': macro_result,
            'alerts_triggered': len(triggered_alerts),
            'alerts': triggered_alerts,
            'agent': 'macro',
            'version': '2.0_with_alerts'
        }
        
    except Exception as e:
        print(f'Macro analysis failed: {str(e)}')
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        
        return {
            'status': 'failed',
            'error': str(e),
            'agent': 'macro'
        }
