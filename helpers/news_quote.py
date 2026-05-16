import streamlit as st
import requests
from datetime import datetime, timedelta

# We added 'sentiment_score' as an input parameter
def get_supporting_quote(symbol, sentiment_score=0.0):
    try:
        fh_key = st.secrets["FINNHUB_API_KEY"]
        end = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from={start}&to={end}&token={fh_key}"
        res = requests.get(url, timeout=5)
        
        if res.status_code == 200:
            news = res.json()
            if news and len(news) > 0:
                pos_words = ['growth', 'profit', 'up', 'surge', 'buy', 'bull', 'strong', 'beat', 'higher']
                neg_words = ['drop', 'loss', 'down', 'fall', 'sell', 'bear', 'weak', 'miss', 'lower']
                
                # Default to the most recent story if we can't find a perfect match
                best_story = news[0] 
                
                # Scan the top 15 recent articles for a headline that matches the mood
                for story in news[:15]:
                    title = story.get('headline', '').lower()
                    
                    # If the app is bullish, find a bullish headline
                    if sentiment_score > 0.2 and any(w in title for w in pos_words):
                        best_story = story
                        break
                    # If the app is bearish, find a bearish headline
                    elif sentiment_score < -0.2 and any(w in title for w in neg_words):
                        best_story = story
                        break
                    # If neutral, try to find a headline that at least mentions the ticker explicitly
                    elif symbol.lower() in title:
                        best_story = story
                        break
                
                title = best_story.get('headline', "Market update for " + symbol)
                source = best_story.get('source', "Financial News")
                
                return f"\"{title}\"", source
                
    except Exception as e:
        print(f"Error fetching quote: {e}")
        
    return "headline temporarily unavailable.", "API"