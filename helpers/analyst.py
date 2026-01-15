import streamlit as st
import requests
import yfinance as yf

@st.cache_data(ttl=600)
def get_analyst_data(symbol):
    fmp_key = st.secrets["FMP_API_KEY"]
    fh_key = st.secrets["FINNHUB_API_KEY"]
    
    target = 0.0
    rec = "Neutral"
    info = {}

    # pull consensus target from fmp
    try:
        fmp_url = f"https://financialmodelingprep.com/api/v3/price-target-consensus?symbol={symbol}&apikey={fmp_key}"
        fmp_r = requests.get(fmp_url)
        fmp_data = fmp_r.json()
        
        if isinstance(fmp_data, list) and len(fmp_data) > 0:
            target = float(fmp_data[0].get('targetConsensus', 0))
    except Exception:
        target = 0.0

    # pull recommendation counts from finnhub
    try:
        fh_url = f"https://finnhub.io/api/v1/stock/recommendation?symbol={symbol}&token={fh_key}"
        fh_r = requests.get(fh_url)
        fh_data = fh_r.json()
        
        if isinstance(fh_data, list) and len(fh_data) > 0:
            latest = fh_data[0]
            b, sb, s, ss, h = latest.get('buy', 0), latest.get('strongBuy', 0), latest.get('sell', 0), latest.get('strongSell', 0), latest.get('hold', 0)
            
            if sb > b and sb > h: rec = "Strong Buy"
            elif b >= h and b > s: rec = "Buy"
            elif ss > s and ss > h: rec = "Strong Sell"
            elif s > h: rec = "Sell"
            else: rec = "Hold"
    except Exception:
        rec = "Neutral"

    # fallback to yahoo finance if fmp returns nothing
    if target == 0:
        try:
            session = requests.Session()
            session.headers.update({'User-Agent': 'Mozilla/5.0'})
            ticker = yf.Ticker(symbol, session=session)
            info = ticker.info
            target = info.get('targetMeanPrice') or info.get('targetMedianPrice') or 0.0
        except Exception:
            info = {}
    
    return target, rec, info