import os
import tweepy
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# Twitter API credentials (set in .env)
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")


def get_twitter_client():
    """Get authenticated Twitter client"""
    if not all([TWITTER_BEARER_TOKEN, TWITTER_API_KEY, TWITTER_API_SECRET]):
        return None
    
    try:
        client = tweepy.Client(
            bearer_token=TWITTER_BEARER_TOKEN,
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True
        )
        return client
    except Exception as e:
        print(f"Error creating Twitter client: {e}")
        return None


def search_disaster_tweets(query: str = "disaster OR fire OR flood OR earthquake", max_results: int = 10) -> List[Dict]:
    """
    Search Twitter for disaster-related tweets
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of tweet dictionaries with text, location, etc.
    """
    client = get_twitter_client()
    if not client:
        return []
    
    try:
        tweets = client.search_recent_tweets(
            query=query,
            max_results=min(max_results, 100),
            tweet_fields=['created_at', 'author_id', 'geo', 'text'],
            expansions=['author_id', 'geo.place_id']
        )
        
        if not tweets.data:
            return []
        
        results = []
        for tweet in tweets.data:
            results.append({
                "text": tweet.text,
                "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
                "author_id": tweet.author_id,
                "id": tweet.id,
                "source": "twitter"
            })
        
        return results
        
    except Exception as e:
        print(f"Error searching Twitter: {e}")
        return []


def monitor_twitter_stream(keywords: List[str] = None):
    """
    Monitor Twitter stream for disaster keywords
    
    Args:
        keywords: List of keywords to monitor (default: disaster-related)
        
    Returns:
        Generator of tweet dictionaries
    """
    if keywords is None:
        keywords = ["fire", "flood", "earthquake", "disaster", "emergency", "evacuation"]
    
    client = get_twitter_client()
    if not client:
        return
    
    # Note: Streaming requires Twitter API v2 with elevated access
    # This is a placeholder for the streaming implementation
    try:
        # For now, return search results
        query = " OR ".join(keywords)
        tweets = search_disaster_tweets(query, max_results=10)
        for tweet in tweets:
            yield tweet
    except Exception as e:
        print(f"Error in Twitter stream: {e}")

