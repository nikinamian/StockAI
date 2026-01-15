import streamlit as st
import requests
import yfinance as yf

# Cache results for 10 minutes to protect your API limits
@st.cache_data(ttl=600)
def get_analyst_data(symbol):
    # Load keys from Streamlit secrets
    av_key = st.secrets["ALPHA_VANTAGE_KEY"]
    fh_key = st.secrets["FINNHUB_API_KEY"]
    
    target = 0.0
    rec = "Neutral"
    info = {}

    # 1. PRIMARY SOURCE FOR TARGET: Alpha Vantage
    try:
        av_url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={av_key}'
        av_r = requests.get(av_url)
        av_data = av_r.json()
        # Alpha Vantage uses 'AnalystTargetPrice'
        target = float(av_data.get('AnalystTargetPrice', 0))
    except Exception:
        target = 0.0

    # 2. SOURCE FOR RATING: Finnhub
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

    # 3. BACKUP SOURCE FOR TARGET: Yahoo Finance
    # If Alpha Vantage returned 0, we try Yahoo Finance one last time
    try:
        session = requests.Session()
        session.headers.update({'User-Agent': 'Mozilla/5.0'})
        ticker = yf.Ticker(symbol, session=session)
        info = ticker.info
        
        if target == 0:
            target = info.get('targetMeanPrice') or info.get('targetMedianPrice') or 0.0
    except Exception:
        pass # Keep target as whatever it was before (likely 0)
    
    return target, rec, info