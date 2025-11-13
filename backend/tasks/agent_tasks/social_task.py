"""
Social Sentiment Analysis Celery Task - With Alert Triggering
"""
from core import celery_app
import asyncio
from agents.social_agent import SocialAgent
from services.alert_manager import AlertManager


@celery_app.task(bind=True, name="social_analysis")
def social_task(self, token_symbol: str, platforms: list = None, alert_threshold: float = 0.7):
    """
    Social sentiment analysis with alert triggering
    
    Args:
        token_symbol: Token to analyze (e.g., "MNT", "ETH")
        platforms: List of platforms to check ["twitter", "farcaster", "reddit"]
        alert_threshold: Sentiment score threshold for alerts (0-1)
    """
    try:
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Fetching social sentiment...', 'progress': 0}
        )
        
        print(f'Running social sentiment analysis for: {token_symbol}')
        
        # Lazy import to avoid circular dependency
        from services.alert_manager import AlertManager
        
        # Initialize agents
        social_agent = SocialAgent()
        alert_manager = AlertManager()
        
        # Default platforms
        if platforms is None:
            platforms = ["twitter", "farcaster", "reddit"]
        
        # Run async agent code
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Analyzing sentiment across platforms...', 'progress': 30}
        )
        
        # Execute sentiment analysis
        sentiment_result = loop.run_until_complete(
            social_agent.analyze_sentiment(
                token_symbol=token_symbol,
                platforms=platforms
            )
        )
        
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Checking sentiment alerts...', 'progress': 70}
        )
        
        # Trigger alerts for extreme sentiment
        triggered_alerts = loop.run_until_complete(
            alert_manager.check_sentiment_alerts(
                token_symbol=token_symbol,
                sentiment_score=sentiment_result.overall_score,
                sentiment_trend=sentiment_result.trend,
                volume_change=sentiment_result.volume_change,
                threshold=alert_threshold
            )
        )
        
        loop.close()
        
        print(f'Social analysis completed: {sentiment_result.overall_score}')
        print(f'Triggered {len(triggered_alerts)} sentiment alerts')
        
        return {
            'status': 'completed',
            'token_symbol': token_symbol,
            'sentiment_analysis': sentiment_result.dict(),
            'platforms_analyzed': platforms,
            'alerts_triggered': len(triggered_alerts),
            'alerts': [alert.to_dict() for alert in triggered_alerts],
            'agent': 'social',
            'version': '2.0_with_alerts'
        }
        
    except Exception as e:
        print(f'Social analysis failed: {str(e)}')
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        
        return {
            'status': 'failed',
            'error': str(e),
            'agent': 'social'
        }
