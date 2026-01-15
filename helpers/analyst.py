import streamlit as st
import requests
import yfinance as yf

# cache data for 10 minutes so i don't blow up my api limits
@st.cache_data(ttl=600)
def get_analyst_data(symbol):
    # grab my key from streamlit secrets
    fh_key = st.secrets["FINNHUB_API_KEY"]
    
    target = 0.0
    rec = "Neutral"
    info = {}

    # try to get the price target from finnhub first
    try:
        # standard rest call to finnhub target endpoint
        fh_url = f"https://finnhub.io/api/v1/stock/price-target?symbol={symbol}&token={fh_key}"
        fh_r = requests.get(fh_url, timeout=5)
        fh_data = fh_r.json()
        
        # pull the mean target if it exists
        if fh_data:
            target = float(fh_data.get('targetMean', 0))
    except Exception:
        target = 0.0

    # pull the expert ratings like buy/sell from finnhub
    try:
        # endpoint for rating counts
        fh_rec_url = f"https://finnhub.io/api/v1/stock/recommendation?symbol={symbol}&token={fh_key}"
        fh_rec_r = requests.get(fh_rec_url, timeout=5)
        fh_rec_data = fh_rec_r.json()
        
        if isinstance(fh_rec_data, list) and len(fh_rec_data) > 0:
            latest = fh_rec_data[0]
            # count up the votes for each category
            b, sb, s, ss, h = latest.get('buy', 0), latest.get('strongBuy', 0), latest.get('sell', 0), latest.get('strongSell', 0), latest.get('hold', 0)
            
            # pick the rating based on which category has the most weight
            if sb > b and sb > h: rec = "Strong Buy"
            elif b >= h and b > s: rec = "Buy"
            elif ss > s and ss > h: rec = "Strong Sell"
            elif s > h: rec = "Sell"
            else: rec = "Hold"
    except Exception:
        rec = "Neutral"

    # backup plan: if finnhub target is zero then hit yahoo finance
    if target == 0:
        try:
            # use a session to trick yahoo into thinking i'm a browser
            session = requests.Session()
            session.headers.update({'User-Agent': 'Mozilla/5.0'})
            ticker = yf.Ticker(symbol, session=session)
            info = ticker.info
            # try to grab the mean or median target from yahoo info
            target = info.get('targetMeanPrice') or info.get('targetMedianPrice') or 0.0
        except Exception:
            info = {}
    
    return target, rec, info