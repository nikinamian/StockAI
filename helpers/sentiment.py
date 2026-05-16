import streamlit as st 
import requests

def get_stock_sentiment(ticker):
    # Pull the key from .streamlit/secrets.toml
    API_KEY = st.secrets.get("NEWS_API_KEY") 
    
    if not API_KEY:
        return 0.0 
    
    # Instead of just the ticker, search for the ticker + stock
    url = f'https://newsapi.org/v2/everything?q={ticker} stock&apiKey={API_KEY}&language=en&pageSize=10&sortBy=relevancy'
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get('status') == 'error':
            # This helps you see why it's failing in the Streamlit logs
            print(f"newsapi error: {data.get('message')}")
            return 0.0

        articles = data.get('articles', [])
        if not articles: 
            return 0.0

        score = 0
        pos = ['growth', 'profit', 'up', 'surge', 'buy', 'bull', 'strong', 'beat', 'higher']
        neg = ['drop', 'loss', 'down', 'fall', 'sell', 'bear', 'weak', 'miss', 'lower']

        for art in articles:
            text = (art.get('title', '') + " " + art.get('description', '')).lower()
            for word in pos:
                if word in text: score += 1
            for word in neg:
                if word in text: score -= 1

        return max(-1.0, min(1.0, score / 10)) 
    except Exception:
        return 0.0