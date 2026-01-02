import streamlit as st
import requests
import yfinance as yf

def get_analyst_data(symbol):
    # use secret keys for finnhub
    fh_key = st.secrets["FINNHUB_API_KEY"]
    
    # fetch wall street recommendation ratings from finnhub (reliable)
    fh_url = f"https://finnhub.io/api/v1/stock/recommendation?symbol={symbol}&token={fh_key}"
    
    # setup a session to help yahoo finance bypass cloud blocks
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    try:
        # 1. get the recommendation tag from finnhub
        fh_r = requests.get(fh_url)
        fh_data = fh_r.json()
        
        if isinstance(fh_data, list) and len(fh_data) > 0:
            latest = fh_data[0]
            # determine majority rating string for scoring in main.py
            b, sb, s, ss, h = latest.get('buy', 0), latest.get('strongBuy', 0), latest.get('sell', 0), latest.get('strongSell', 0), latest.get('hold', 0)
            
            if sb > b and sb > h: rec = "Strong Buy"
            elif b >= h and b > s: rec = "Buy"
            elif ss > s and ss > h: rec = "Strong Sell"
            elif s > h: rec = "Sell"
            else: rec = "Hold"
        else:
            rec = "Neutral"

        # 2. get the analyst target price from yahoo using the session bypass
        ticker = yf.Ticker(symbol, session=session)
        
        # pull the mean target price
        info = ticker.info
        target = info.get('targetMeanPrice') or info.get('targetMedianPrice') or 0.0
        
        # if yahoo still returns zero, try the specific analyst method
        if not target:
            targets = ticker.get_analyst_price_targets()
            target = targets.get('mean') or 0.0

    except Exception:
        # if anything fails, return defaults so app doesn't crash
        target, rec, info = 0.0, "Neutral", {}

    # current price is handled by your predictor file
    current = 0 
    
    # return everything including the raw dictionary for further processing
    return current, target, rec, info