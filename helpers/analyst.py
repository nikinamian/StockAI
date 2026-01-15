import streamlit as st
import requests
import yfinance as yf

@st.cache_data(ttl=600)
def get_analyst_data(symbol):
    # check that these names match your streamlit secrets EXACTLY
    fmp_key = st.secrets["FMP_API_KEY"]
    fh_key = st.secrets["FINNHUB_API_KEY"]
    
    target = 0.0
    rec = "Neutral"
    info = {}

    # try fmp consensus first
    try:
        url = f"https://financialmodelingprep.com/api/v3/price-target-consensus?symbol={symbol}&apikey={fmp_key}"
        r = requests.get(url, timeout=5) # add timeout so it doesn't hang
        data = r.json()
        
        if isinstance(data, list) and len(data) > 0:
            target = float(data[0].get('targetConsensus', 0))
    except Exception as e:
        print(f"FMP error: {e}")
        target = 0.0

    # get analyst ratings from finnhub
    try:
        fh_url = f"https://finnhub.io/api/v1/stock/recommendation?symbol={symbol}&token={fh_key}"
        fh_r = requests.get(fh_url, timeout=5)
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

    # backup: if fmp returned 0, we MUST try yahoo
    if target == 0:
        try:
            # use a session to prevent being blocked as a bot
            session = requests.Session()
            session.headers.update({'User-Agent': 'Mozilla/5.0'})
            ticker = yf.Ticker(symbol, session=session)
            info = ticker.info
            # try mean target first, then median
            target = info.get('targetMeanPrice') or info.get('targetMedianPrice') or 0.0
        except Exception:
            info = {}
    
    return target, rec, info