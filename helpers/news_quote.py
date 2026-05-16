import streamlit as st
import requests
from datetime import datetime, timedelta
from urllib.parse import urlparse # NEW: library to parse URLs

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
                pos_words = ['growth', 'profit', 'up', 'surge', 'buy', 'bull', 'strong', 'beat', 'higher', 'upgrade']
                neg_words = ['drop', 'loss', 'down', 'fall', 'sell', 'bear', 'weak', 'miss', 'lower', 'downgrade']
                exclude_words = [' over ', ' vs ', ' versus ', ' instead ']
                
                best_story = news[0] 
                
                for story in news[:15]:
                    title = story.get('headline', '').lower()
                    
                    if any(ex in title for ex in exclude_words):
                        continue
                    
                    if sentiment_score > 0.2 and any(w in title for w in pos_words):
                        best_story = story
                        break
                    elif sentiment_score < -0.2 and any(w in title for w in neg_words):
                        best_story = story
                        break
                    elif symbol.lower() in title:
                        best_story = story
                
                title = best_story.get('headline', "Market update for " + symbol)
                article_url = best_story.get('url', '#')
                
                # NEW: Force the source name to match the actual destination link
                if article_url != '#':
                    domain = urlparse(article_url).netloc
                    # Clean up the prefix for a cleaner UI (e.g., 'www.fool.com' -> 'FOOL.COM')
                    source = domain.replace('www.', '').replace('finance.', '').upper()
                else:
                    source = best_story.get('source', "FINANCIAL NEWS").upper()
                
                return f"\"{title}\"", source, article_url
                
    except Exception as e:
        print(f"Error fetching quote: {e}")
        
    return "headline temporarily unavailable.", "API", "#"