import streamlit as st
import requests
import yfinance as yf

def get_analyst_data(symbol):
    # pull the 12-month analyst target from alpha vantage (reliable official api)
    av_key = st.secrets["ALPHA_VANTAGE_KEY"]
    av_url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={av_key}'
    
    target = 0.0
    try:
        av_r = requests.get(av_url)
        av_data = av_r.json()
        # pull the target price from the overview dictionary
        target = float(av_data.get('AnalystTargetPrice', 0))
    except Exception:
        # if alpha vantage fails, target stays 0.0
        pass

    # get the recommendation ratings from finnhub (standard keys)
    fh_key = st.secrets["FINNHUB_API_KEY"]
    fh_url = f"https://finnhub.io/api/v1/stock/recommendation?symbol={symbol}&token={fh_key}"
    
    rec = "Neutral"
    try:
        fh_r = requests.get(fh_url)
        fh_data = fh_r.json()
        
        if isinstance(fh_data, list) and len(fh_data) > 0:
            latest = fh_data[0]
            # determine majority rating for the scoring system in main.py
            b, sb, s, ss, h = latest.get('buy', 0), latest.get('strongBuy', 0), latest.get('sell', 0), latest.get('strongSell', 0), latest.get('hold', 0)
            
            if sb > b and sb > h: rec = "Strong Buy"
            elif b >= h and b > s: rec = "Buy"
            elif ss > s and ss > h: rec = "Strong Sell"
            elif s > h: rec = "Sell"
            else: rec = "Hold"
    except Exception:
        # fallback to neutral if finnhub is down
        pass

    # get general company info from yahoo using a session bypass
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    try:
        ticker = yf.Ticker(symbol, session=session)
        info = ticker.info
        
        # only use yahoo for the target if alpha vantage returned zero
        if not target:
            target = info.get('targetMeanPrice') or 0.0
    except Exception:
        info = {}

    # current price is handled by the predictor file 
    current = 0 
    
    # return the cleaned data for the ui to display
    return current, target, rec, info