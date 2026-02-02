import streamlit as st
import requests
import yfinance as yf

@st.cache_data(ttl=600)
def get_analyst_data(symbol):
    fh_key = st.secrets["FINNHUB_API_KEY"]
    target = 0.0
    rec = "Neutral" # Default starting point
    info = {}

    try:
        # Layer 1: Finnhub
        target_url = f"https://finnhub.io/api/v1/stock/price-target?symbol={symbol}&token={fh_key}"
        res = requests.get(target_url, timeout=5)
        if res.status_code == 200:
            target = float(res.json().get('targetMean', 0))
            info['targetMeanPrice'] = target
        
        rec_url = f"https://finnhub.io/api/v1/stock/recommendation?symbol={symbol}&token={fh_key}"
        res_rec = requests.get(rec_url, timeout=5)
        if res_rec.status_code == 200:
            rec_data = res_rec.json()
            if rec_data:
                # Get the most recent recommendation entry
                latest = rec_data[0]
                
                # Logic to determine the strongest recommendation category
                # We prioritize Buy/Sell over Hold
                if latest.get('strongBuy', 0) > 0: rec = "Strong Buy"
                elif latest.get('buy', 0) > 0: rec = "Buy"
                elif latest.get('strongSell', 0) > 0: rec = "Strong Sell"
                elif latest.get('sell', 0) > 0: rec = "Sell"
                else: rec = "Hold"
                
                # Update info so process_analyst_buy.py can format it correctly
                info['recommendationKey'] = rec.lower().replace(" ", "_")
    except:
        pass

    # Layer 2: Yahoo Fallback
    # If Finnhub fails or returns no target, try Yahoo Finance
    if target == 0 or rec == "Neutral":
        try:
            ticker = yf.Ticker(symbol)
            ticker_info = ticker.info
            info = ticker_info # Use Yahoo info dictionary
            target = info.get('targetMeanPrice') or info.get('targetMedianPrice') or 0.0
            
            # Extract recommendation from Yahoo info
            raw_rec = info.get('recommendationKey', 'neutral')
            rec = raw_rec.replace('_', ' ').title()
        except:
            pass

    return target, rec, info