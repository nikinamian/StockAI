import streamlit as st
import requests
import yfinance as yf

def get_analyst_data(symbol):
    # use secret keys for finnhub
    fh_key = st.secrets["FINNHUB_API_KEY"]
    
    # fetch wall street recommendation ratings from finnhub (reliable)
    fh_url = f"https://finnhub.io/api/v1/stock/recommendation?symbol={symbol}&token={fh_key}"
    
    try:
        # 1. get the recommendation tag from finnhub
        fh_r = requests.get(fh_url)
        fh_data = fh_r.json()
        
        if isinstance(fh_data, list) and len(fh_data) > 0:
            latest = fh_data[0]
            buy_score = latest.get('buy', 0)
            strong_buy = latest.get('strongBuy', 0)
            sell_score = latest.get('sell', 0)
            strong_sell = latest.get('strongSell', 0)
            hold_score = latest.get('hold', 0)

            if strong_buy > buy_score and strong_buy > hold_score:
                rec = "Strong Buy"
            elif buy_score >= hold_score and buy_score > sell_score:
                rec = "Buy"
            elif strong_sell > sell_score and strong_sell > hold_score:
                rec = "Strong Sell"
            elif sell_score > hold_score:
                rec = "Sell"
            else:
                rec = "Hold"
        else:
            rec = "Neutral"

        # 2. get ONLY the analyst target from yahoo finance
        # we create a session to help bypass the cloud rate limit
        ticker = yf.Ticker(symbol)
        
        # we only pull 'info' if we absolutely have to
        # yahoo finance sometimes hides the target in different places
        target = ticker.info.get('targetMeanPrice') or ticker.info.get('targetMedianPrice') or 0.0
        
        # if it's still zero, we try one last check
        if not target:
            target = 0.0

    except Exception:
        # if anything fails, return defaults so main.py doesn't crash
        target, rec, info = 0.0, "Neutral", {}

    # current price is handled by your predictor file
    current = 0 
    
    # return everything for further processing
    return current, target, rec, {}