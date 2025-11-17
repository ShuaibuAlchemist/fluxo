"""
AI Insights Engine
Uses Claude API to generate intelligent portfolio insights
"""
import os
import json
import aiohttp
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class AIInsightsEngine:
    """Generate AI-powered portfolio insights using Claude"""
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.model = "claude-sonnet-4-20250514"
        self.api_url = "https://api.anthropic.com/v1/messages"
    
    async def generate_portfolio_insights(
        self,
        wallet_address: str,
        risk_analysis: Dict,
        social_sentiment: Optional[Dict] = None,
        macro_conditions: Optional[Dict] = None
    ) -> Dict:
        """
        Generate comprehensive portfolio insights
        
        Args:
            wallet_address: Wallet being analyzed
            risk_analysis: Risk agent output
            social_sentiment: Social agent output (optional)
            macro_conditions: Macro agent output (optional)
            
        Returns:
            AI-generated insights
        """
        try:
            # Build context for Claude
            context = self._build_context(
                wallet_address,
                risk_analysis,
                social_sentiment,
                macro_conditions
            )
            
            # Generate insights using Claude
            insights = await self._call_claude(context)
            
            return {
                "wallet_address": wallet_address,
                "insights": insights,
                "data_sources": {
                    "risk_analysis": bool(risk_analysis),
                    "social_sentiment": bool(social_sentiment),
                    "macro_conditions": bool(macro_conditions)
                }
            }
            
        except Exception as e:
            logger.error(f"AI insights generation failed: {str(e)}")
            return self._get_fallback_insights(wallet_address, risk_analysis)
    
    def _build_context(
        self,
        wallet_address: str,
        risk_analysis: Dict,
        social_sentiment: Optional[Dict],
        macro_conditions: Optional[Dict]
    ) -> str:
        """Build context prompt for Claude"""
        
        context = f"""You are Fluxo, an AI-powered DeFi portfolio analyst. Analyze this portfolio and provide actionable insights.

WALLET: {wallet_address}

RISK ANALYSIS:
- Risk Score: {risk_analysis.get('risk_score', 'N/A')}/10
- Risk Level: {risk_analysis.get('risk_level', 'N/A')}
- Concentration Risk: {risk_analysis.get('concentration_risk', 'N/A')}
- Liquidity Score: {risk_analysis.get('liquidity_score', 'N/A')}
"""
        
        if risk_analysis.get('top_holdings'):
            context += "\nTop Holdings:\n"
            for holding in risk_analysis['top_holdings'][:3]:
                context += f"  - {holding.get('token', 'Unknown')}: {holding.get('percentage', 0):.1f}% (${holding.get('value_usd', 0):,.0f})\n"
        
        if social_sentiment:
            context += f"""
SOCIAL SENTIMENT:
- Overall Sentiment: {social_sentiment.get('overall_sentiment', 'N/A')}
- Sentiment Score: {social_sentiment.get('overall_score', 0):.2f}
- Posts Analyzed: {social_sentiment.get('total_posts_analyzed', 0)}
"""
            
            if social_sentiment.get('by_platform'):
                context += "\nPlatform Breakdown:\n"
                for platform, data in social_sentiment['by_platform'].items():
                    context += f"  - {platform.capitalize()}: {data.get('overall_sentiment', 'N/A')} ({data.get('total_posts', 0)} posts)\n"
        
        if macro_conditions:
            context += f"""
MACRO CONDITIONS:
- Market Condition: {macro_conditions.get('market_condition', 'N/A')}
- Correlation Score: {macro_conditions.get('correlation_score', 'N/A')}
"""
        
        context += """

Please provide:
1. Portfolio Health Summary (2-3 sentences)
2. Key Risks (top 3, bullet points)
3. Opportunities (top 2-3, bullet points)
4. Actionable Recommendations (3-4 specific actions)
5. Market Context (if social/macro data available)

Format as JSON with keys: summary, risks, opportunities, recommendations, market_context
Keep it concise, actionable, and investor-friendly.
"""
        
        return context
    
    async def _call_claude(self, context: str) -> Dict:
        """Call Claude API"""
        
        if not self.api_key:
            logger.warning("No Anthropic API key - using fallback insights")
            return self._parse_fallback_response()
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": self.model,
            "max_tokens": 1500,
            "messages": [
                {
                    "role": "user",
                    "content": context
                }
            ]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract text from response
                        content = data.get('content', [])
                        if content and len(content) > 0:
                            text = content[0].get('text', '')
                            
                            # Try to parse as JSON
                            try:
                                # Find JSON in response
                                json_start = text.find('{')
                                json_end = text.rfind('}') + 1
                                
                                if json_start >= 0 and json_end > json_start:
                                    json_str = text[json_start:json_end]
                                    insights = json.loads(json_str)
                                    return insights
                                else:
                                    # Fallback: structure the text
                                    return {
                                        "summary": text[:200],
                                        "risks": ["Analysis provided in summary"],
                                        "opportunities": ["See detailed analysis"],
                                        "recommendations": [text],
                                        "market_context": "AI-generated insights"
                                    }
                            except json.JSONDecodeError:
                                logger.error("Failed to parse Claude response as JSON")
                                return self._parse_fallback_response()
                    else:
                        logger.error(f"Claude API error: {response.status}")
                        return self._parse_fallback_response()
                        
        except Exception as e:
            logger.error(f"Claude API call failed: {str(e)}")
            return self._parse_fallback_response()
    
    def _parse_fallback_response(self) -> Dict:
        """Generate structured fallback insights"""
        return {
            "summary": "Portfolio analysis completed using risk metrics and market data. Review detailed breakdown below.",
            "risks": [
                "Monitor portfolio concentration levels",
                "Track liquidity conditions in DeFi protocols",
                "Stay aware of market volatility"
            ],
            "opportunities": [
                "Consider diversification across L2 ecosystems",
                "Explore yield optimization strategies"
            ],
            "recommendations": [
                "Review top holdings allocation",
                "Monitor social sentiment for tokens held",
                "Set up automated risk alerts",
                "Rebalance if concentration exceeds 40%"
            ],
            "market_context": "Analysis based on available on-chain and social data"
        }
    
    def _get_fallback_insights(
        self,
        wallet_address: str,
        risk_analysis: Dict
    ) -> Dict:
        """Fallback insights when AI fails"""
        return {
            "wallet_address": wallet_address,
            "insights": self._parse_fallback_response(),
            "data_sources": {
                "risk_analysis": True,
                "social_sentiment": False,
                "macro_conditions": False
            },
            "note": "Generated using rule-based analysis (AI service unavailable)"
        }
    
    async def generate_comparison_insights(
        self,
        portfolios: List[Dict]
    ) -> Dict:
        """
        Generate comparative insights across multiple portfolios
        
        Args:
            portfolios: List of portfolio analyses
            
        Returns:
            Comparative insights
        """
        if len(portfolios) < 2:
            return {
                "error": "Need at least 2 portfolios for comparison"
            }
        
        # Build comparison context
        context = "Compare these DeFi portfolios and provide insights:\n\n"
        
        for i, portfolio in enumerate(portfolios, 1):
            context += f"Portfolio {i}:\n"
            context += f"  Risk Score: {portfolio.get('risk_score', 'N/A')}/10\n"
            context += f"  Risk Level: {portfolio.get('risk_level', 'N/A')}\n"
            context += f"  Total Value: ${portfolio.get('total_value_usd', 0):,.0f}\n\n"
        
        context += "Provide: 1) Relative risk ranking, 2) Diversification comparison, 3) Best practices from top performer"
        
        # Generate insights
        insights = await self._call_claude(context)
        
        return {
            "portfolios_compared": len(portfolios),
            "comparison_insights": insights
        }
