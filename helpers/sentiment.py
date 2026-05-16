import streamlit as st 
import requests
from datetime import datetime, timedelta

def get_stock_sentiment(ticker):
    try:
        # Use Finnhub instead of NewsAPI
        fh_key = st.secrets["FINNHUB_API_KEY"]
        end = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={start}&to={end}&token={fh_key}"
        res = requests.get(url, timeout=5)
        
        if res.status_code != 200:
            return 0.0
            
        articles = res.json()
        if not articles:
            return 0.0

        score = 0
        pos = ['growth', 'profit', 'up', 'surge', 'buy', 'bull', 'strong', 'beat', 'higher']
        neg = ['drop', 'loss', 'down', 'fall', 'sell', 'bear', 'weak', 'miss', 'lower']

        # Scan the 10 most recent articles
        for art in articles[:10]:
            # Combine Finnhub's headline and summary
            text = (art.get('headline', '') + " " + art.get('summary', '')).lower()
            
            for word in pos:
                if word in text: score += 1
            for word in neg:
                if word in text: score -= 1

        return max(-1.0, min(1.0, score / 10))
        
    except Exception as e:
        print(f"Sentiment error: {e}")
        return 0.0