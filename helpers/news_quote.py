import streamlit as st
import requests
from datetime import datetime, timedelta

def get_supporting_quote(symbol):
    try:
        # 1. Use the Finnhub key we already know works
        fh_key = st.secrets["FINNHUB_API_KEY"]
        
        # 2. Get dates for the last 7 days
        end = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        # 3. Fetch company news from Finnhub
        url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from={start}&to={end}&token={fh_key}"
        res = requests.get(url, timeout=5)
        
        if res.status_code == 200:
            news = res.json()
            if news and len(news) > 0:
                story = news[0] # Get the most recent story
                
                # Finnhub uses 'headline' and 'source' directly
                title = story.get('headline', "Market update for " + symbol)
                source = story.get('source', "Financial News")
                
                return f"\"{title}\"", source
                
    except Exception as e:
        print(f"Error fetching quote: {e}")
        
    # Fallback if everything fails
    return "headline temporarily unavailable.", "API"