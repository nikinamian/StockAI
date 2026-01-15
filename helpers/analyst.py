import streamlit as st
import requests
import yfinance as yf

# Cache results for 10 minutes to save API limits
@st.cache_data(ttl=600)
def get_analyst_data(symbol):
    # use our secrets for the api keys
    fh_key = st.secrets["FINNHUB_API_KEY"]
    
    rec = "Neutral"

    # 1. Get the recommendation string from Finnhub
    try:
        fh_url = f"https://finnhub.io/api/v1/stock/recommendation?symbol={symbol}&token={fh_key}"
        fh_r = requests.get(fh_url)
        fh_data = fh_r.json()
        
        if isinstance(fh_data, list) and len(fh_data) > 0:
            latest = fh_data[0]
            # check the buy/sell counts to pick the label
            b, sb, s, ss, h = latest.get('buy', 0), latest.get('strongBuy', 0), latest.get('sell', 0), latest.get('strongSell', 0), latest.get('hold', 0)
            
            if sb > b and sb > h: rec = "Strong Buy"
            elif b >= h and b > s: rec = "Buy"
            elif ss > s and ss > h: rec = "Strong Sell"
            elif s > h: rec = "Sell"
            else: rec = "Hold"
    except Exception:
        rec = "Neutral"

    # 2. Get target price and raw info from Yahoo Finance
    # This is more sustainable than hitting Alpha Vantage twice
    info = {}
    target = 0.0
    try:
        # setup a session to look like a real browser
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0'})
        ticker = yf.Ticker(symbol, session=session)
        info = ticker.info
        # grab the target from the info dict
        target = info.get('targetMeanPrice') or info.get('targetMedianPrice') or 0.0
    except Exception:
        info = {}
    
    return target, rec, info