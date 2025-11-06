"""
Social Sentiment Analysis Celery Task
Integrates Muhammad's Social Agent with Freeman's Celery infrastructure
Based on Electus's social sentiment research
"""
from core import celery_app
import asyncio
from agents.social_agent import SocialAgent

@celery_app.task(bind=True, name="social_sentiment_analysis")
def social_task(self, timeframe: str = "24h", focus_tokens: list = None):
    """
    Background task for social sentiment analysis
    
    Args:
        timeframe: Time period to analyze (1h, 24h, 7d)
        focus_tokens: Optional list of tokens to focus analysis on
    
    Returns:
        dict: Sentiment analysis results
    """
    try:
        # Update task state
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Analyzing social sentiment...', 'progress': 0}
        )
        
        print(f'Running social sentiment analysis for timeframe: {timeframe}')
        
        # Initialize Social Agent (using Electus's research)
        social_agent = SocialAgent(use_mock=True)  # Week 1: mock data
        
        # Run async agent code in sync Celery task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Update progress
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Detecting narratives and influencer signals...', 'progress': 50}
        )
        
        # Execute sentiment analysis
        sentiment = loop.run_until_complete(
            social_agent.analyze_sentiment(timeframe, focus_tokens)
        )
        loop.close()
        
        print(f'Sentiment analysis completed: {sentiment.level.value}')
        
        # Return structured result
        return {
            'status': 'completed',
            'timeframe': timeframe,
            'focus_tokens': focus_tokens,
            'sentiment_analysis': sentiment.to_dict(),
            'agent': 'social'
        }
        
    except Exception as e:
        print(f'Social sentiment analysis failed: {str(e)}')
        
        # Update task state to failure
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        
        return {
            'status': 'failed',
            'error': str(e),
            'agent': 'social'
        }
