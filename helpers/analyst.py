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

    # LAYER 1: Finnhub
    try:
        # get price target
        target_url = f"https://finnhub.io/api/v1/stock/price-target?symbol={symbol}&token={fh_key}"
        res = requests.get(target_url, timeout=5)
        if res.status_code == 200:
            target_val = float(res.json().get('targetMean', 0))
            target = target_val
            # Populate the info dict for process_analyst_data
            info['targetMeanPrice'] = target_val
        
        # get recommendation
        rec_url = f"https://finnhub.io/api/v1/stock/recommendation?symbol={symbol}&token={fh_key}"
        res_rec = requests.get(rec_url, timeout=5)
        rec_data = res_rec.json()
        if isinstance(rec_data, list) and len(rec_data) > 0:
            latest = rec_data[0]
            b, sb, h = latest.get('buy', 0), latest.get('strongBuy', 0), latest.get('hold', 0)
            s, ss = latest.get('sell', 0), latest.get('strongSell', 0)
            
            if sb > b and sb > h: rec = "Strong Buy"
            elif b >= h and b > s: rec = "Buy"
            elif ss > s and ss > h: rec = "Strong Sell"
            elif s > h: rec = "Sell"
            else: rec = "Hold"
            
            # Add recommendationKey so process_analyst_data doesn't return 'N/A'
            info['recommendationKey'] = rec.lower().replace(" ", "_")
            
    except Exception:
        pass

    # LAYER 2: Yahoo Finance Fallback
    if target == 0:
        try:
            session = requests.Session()
            session.headers.update({'User-Agent': 'Mozilla/5.0'})
            ticker = yf.Ticker(symbol, session=session)
            # Overwrite the empty info dict with Yahoo's full data
            info = ticker.info 
            target = info.get('targetMeanPrice') or info.get('targetMedianPrice') or 0.0
        except Exception:
            pass

    return target, rec, info