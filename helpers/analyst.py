import streamlit as st
import requests
import yfinance as yf

# cache for 10 mins to reduce use of free API
@st.cache_data(ttl=600)
def get_analyst_data(symbol):
    fh_key = st.secrets["FINNHUB_API_KEY"]
    target = 0.0
    rec = "Neutral"
    info = {}

    # LAYER 1: Finnhub (Most reliable for free targets right now)
    try:
        # get price target
        target_url = f"https://finnhub.io/api/v1/stock/price-target?symbol={symbol}&token={fh_key}"
        res = requests.get(target_url, timeout=5)
        if res.status_code == 200:
            target = float(res.json().get('targetMean', 0))
        
        # get recommendation
        rec_url = f"https://finnhub.io/api/v1/stock/recommendation?symbol={symbol}&token={fh_key}"
        res_rec = requests.get(rec_url, timeout=5)
        rec_data = res_rec.json()
        if isinstance(rec_data, list) and len(rec_data) > 0:
            latest = rec_data[0]
            # picking the strongest rating category
            b, sb, h = latest.get('buy', 0), latest.get('strongBuy', 0), latest.get('hold', 0)
            s, ss = latest.get('sell', 0), latest.get('strongSell', 0)
            if sb > b and sb > h: rec = "Strong Buy"
            elif b >= h and b > s: rec = "Buy"
            elif ss > s and ss > h: rec = "Strong Sell"
            elif s > h: rec = "Sell"
            else: rec = "Hold"
    except Exception:
        pass

    # LAYER 2: Yahoo Finance (The "Browser Trick" Fallback)
    if target == 0:
        try:
            # i'm using a custom header to stop yahoo from blocking me
            session = requests.Session()
            session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            ticker = yf.Ticker(symbol, session=session)
            info = ticker.info
            target = info.get('targetMeanPrice') or info.get('targetMedianPrice') or 0.0
        except Exception:
            pass

    # LAYER 3: Hardcoded Safety (Only if the world is ending)
    # if everything fails, we return 0.0 but main.py will show "N/A"
    return target, rec, info