import os
import requests
from dotenv import load_dotenv

# load environment variables for security
load_dotenv()
API_KEY = os.getenv("NEWS_API_KEY")

def get_stock_sentiment(ticker):
    # default to neutral if api key is missing
    if not API_KEY:
        return 0.0 
    
    # build the request url for recent stock news
    url = f'https://newsapi.org/v2/everything?q={ticker}&apiKey={API_KEY}&language=en&pageSize=10&sortBy=relevancy'
    
    try:
        # fetch news data from the external api
        response = requests.get(url)
        data = response.json()
        
        # handle api errors like rate limits or bad keys
        if data.get('status') == 'error':
            print(f"newsapi error: {data.get('message')}")
            return 0.0

        # extract articles from the json response
        articles = data.get('articles', [])
        if not articles: 
            return 0.0

        score = 0
        # define positive and negative words for scoring
        pos = ['growth', 'profit', 'up', 'surge', 'buy', 'bull', 'strong', 'beat', 'higher']
        neg = ['drop', 'loss', 'down', 'fall', 'sell', 'bear', 'weak', 'miss', 'lower']

        for art in articles:
            # combine title and description for full text analysis
            text = (art.get('title', '') + " " + art.get('description', '')).lower()
            # increase score for bullish keywords
            for word in pos:
                if word in text: score += 1
            # decrease score for bearish keywords
            for word in neg:
                if word in text: score -= 1

        # normalize the total score to stay between -1.0 and 1.0
        return max(-1.0, min(1.0, score / 10)) 
    except Exception:
        # return neutral if any network or processing error occurs
        return 0.0