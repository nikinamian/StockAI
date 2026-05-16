import streamlit as st
import requests
from datetime import datetime, timedelta

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
                
                # Filter out comparative articles to avoid the "Buy X over Y" trap
                exclude_words = [' over ', ' vs ', ' versus ', ' instead ']
                
                best_story = news[0] 
                
                # Scan the top 15 recent articles for a headline that matches the mood
                for story in news[:15]:
                    title = story.get('headline', '').lower()
                    
                    # Skip the story entirely if it contains comparative words
                    if any(ex in title for ex in exclude_words):
                        continue
                    
                    # If bullish, find a bullish headline
                    if sentiment_score > 0.2 and any(w in title for w in pos_words):
                        best_story = story
                        break
                    # If bearish, find a bearish headline
                    elif sentiment_score < -0.2 and any(w in title for w in neg_words):
                        best_story = story
                        break
                    # If neutral, try to find a headline mentioning the ticker
                    elif symbol.lower() in title:
                        best_story = story
                
                title = best_story.get('headline', "Market update for " + symbol)
                article_url = best_story.get('url', '#')
                
                # Grab Finnhub's official source string and make it uppercase
                raw_source = best_story.get('source', 'FINANCIAL NEWS').upper()
                
                # We map the raw source names to make them look professional
                source_map = {
                    'YAHOO': 'YAHOO FINANCE',
                    'MOTLEY FOOL': 'THE MOTLEY FOOL',
                    'SEEKINGALPHA': 'SEEKING ALPHA',
                    'PRNEWSWIRE': 'PR NEWSWIRE',
                    'GLOBENEWSWIRE': 'GLOBE NEWSWIRE',
                    'WSJ': 'THE WALL STREET JOURNAL',
                    'CNBC': 'CNBC',
                    'REUTERS': 'REUTERS',
                    'BLOOMBERG': 'BLOOMBERG',
                    'MARKETWATCH': 'MARKETWATCH'
                }
                
                # Look up the source in our map. If it's not there, just use the raw source.
                source = source_map.get(raw_source, raw_source)
                
                # Return all THREE variables back to main.py
                return f"\"{title}\"", source, article_url
                
    except Exception as e:
        print(f"Error fetching quote: {e}")
        
    # Make sure the fallback also returns three items so the app doesn't crash
    return "headline temporarily unavailable.", "API", "#"