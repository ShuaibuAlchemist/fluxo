"""
Sentiment Analysis Service
Analyzes sentiment from social media data
"""
from typing import List, Dict
import re
from collections import Counter


class SentimentAnalyzer:
    """Analyze sentiment from social media posts"""
    
    def __init__(self):
        # Positive and negative keywords
        self.positive_keywords = {
            'bullish', 'moon', 'buy', 'long', 'pump', 'gains', 'profit',
            'green', 'up', 'growth', 'strong', 'solid', 'good', 'great',
            'excellent', 'amazing', 'fantastic', 'love', 'best', '🚀', '📈',
            '💎', '🔥', '✅', '💪', 'gem', 'potential', 'promising'
        }
        
        self.negative_keywords = {
            'bearish', 'dump', 'sell', 'short', 'crash', 'loss', 'red',
            'down', 'weak', 'bad', 'terrible', 'awful', 'worst', 'hate',
            'scam', 'rug', '📉', '⚠', '❌', '💩', 'avoid', 'warning',
            'risky', 'danger', 'failing', 'dead'
        }
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analyze sentiment of a single text
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis result
        """
        text_lower = text.lower()
        
        # Count positive and negative keywords
        positive_count = sum(1 for word in self.positive_keywords if word in text_lower)
        negative_count = sum(1 for word in self.negative_keywords if word in text_lower)
        
        # Calculate sentiment score (-1 to 1)
        total = positive_count + negative_count
        if total == 0:
            score = 0.0
        else:
            score = (positive_count - negative_count) / total
        
        # Classify sentiment
        if score > 0.2:
            sentiment = "positive"
        elif score < -0.2:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "score": score,
            "sentiment": sentiment,
            "positive_signals": positive_count,
            "negative_signals": negative_count
        }
    
    def analyze_batch(self, posts: List[Dict]) -> Dict:
        """
        Analyze sentiment across multiple posts
        
        Args:
            posts: List of social media posts
            
        Returns:
            Aggregated sentiment analysis
        """
        if not posts:
            return {
                "overall_score": 0.0,
                "overall_sentiment": "neutral",
                "total_posts": 0,
                "sentiment_distribution": {
                    "positive": 0,
                    "neutral": 0,
                    "negative": 0
                }
            }
        
        sentiments = []
        sentiment_counts = Counter()
        
        for post in posts:
            text = post.get("text", "") or post.get("title", "")
            if text:
                result = self.analyze_text(text)
                sentiments.append(result["score"])
                sentiment_counts[result["sentiment"]] += 1
        
        # Calculate overall metrics
        overall_score = sum(sentiments) / len(sentiments) if sentiments else 0.0
        
        if overall_score > 0.2:
            overall_sentiment = "positive"
        elif overall_score < -0.2:
            overall_sentiment = "negative"
        else:
            overall_sentiment = "neutral"
        
        return {
            "overall_score": round(overall_score, 3),
            "overall_sentiment": overall_sentiment,
            "total_posts": len(posts),
            "sentiment_distribution": {
                "positive": sentiment_counts.get("positive", 0),
                "neutral": sentiment_counts.get("neutral", 0),
                "negative": sentiment_counts.get("negative", 0)
            },
            "positive_percentage": round(sentiment_counts.get("positive", 0) / len(posts) * 100, 1),
            "neutral_percentage": round(sentiment_counts.get("neutral", 0) / len(posts) * 100, 1),
            "negative_percentage": round(sentiment_counts.get("negative", 0) / len(posts) * 100, 1)
        }
    
    def analyze_by_platform(self, all_data: Dict[str, List[Dict]]) -> Dict:
        """
        Analyze sentiment for each platform separately
        
        Args:
            all_data: Dictionary with data from each platform
            
        Returns:
            Platform-specific sentiment analysis
        """
        results = {}
        
        for platform, posts in all_data.items():
            results[platform] = self.analyze_batch(posts)
        
        # Calculate weighted overall sentiment
        total_posts = sum(r["total_posts"] for r in results.values())
        if total_posts > 0:
            weighted_score = sum(
                r["overall_score"] * r["total_posts"]
                for r in results.values()
            ) / total_posts
        else:
            weighted_score = 0.0
        
        if weighted_score > 0.2:
            overall_sentiment = "positive"
        elif weighted_score < -0.2:
            overall_sentiment = "negative"
        else:
            overall_sentiment = "neutral"
        
        return {
            "by_platform": results,
            "overall_score": round(weighted_score, 3),
            "overall_sentiment": overall_sentiment,
            "total_posts_analyzed": total_posts
        }
