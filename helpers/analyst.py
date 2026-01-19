import streamlit as st
import requests
import yfinance as yf

@st.cache_data(ttl=600)
def get_analyst_data(symbol):
    fh_key = st.secrets["FINNHUB_API_KEY"]
    target = 0.0
    rec = "Neutral"
    info = {}

    try:
        # Layer 1: Finnhub
        target_url = f"https://finnhub.io/api/v1/stock/price-target?symbol={symbol}&token={fh_key}"
        res = requests.get(target_url, timeout=5)
        if res.status_code == 200:
            target = float(res.json().get('targetMean', 0))
            # Manually fill info so process_analyst_buy.py sees it
            info['targetMeanPrice'] = target
        
        rec_url = f"https://finnhub.io/api/v1/stock/recommendation?symbol={symbol}&token={fh_key}"
        res_rec = requests.get(rec_url, timeout=5)
        if res_rec.status_code == 200:
            rec_data = res_rec.json()
            if rec_data:
                latest = rec_data[0]
                # logic to pick recommendation...
                # (your existing sb/b/h/s/ss logic here)
                info['recommendationKey'] = rec.lower().replace(" ", "_")
    except:
        pass

    # Layer 2: Yahoo Fallback
    if target == 0:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            target = info.get('targetMeanPrice') or info.get('targetMedianPrice') or 0.0
        except:
            pass

    return target, rec, info