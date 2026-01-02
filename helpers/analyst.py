import streamlit as st
import requests

def get_analyst_data(symbol):
    # use secret keys from streamlit settings
    av_key = st.secrets["ALPHA_VANTAGE_KEY"]
    fh_key = st.secrets["FINNHUB_API_KEY"]
    
    # fetch current price and analyst target from alpha vantage
    av_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={av_key}"
    # fetch wall street recommendation ratings from finnhub
    fh_url = f"https://finnhub.io/api/v1/stock/recommendation?symbol={symbol}&token={fh_key}"
    
    try:
        # pull the full dictionary of company information
        av_r = requests.get(av_url)
        info = av_r.json()
        
        # extract the average price target from wall street analysts
        target = float(info.get('AnalystTargetPrice', 0))
        current = 0 # predictor.py handles the actual current price display
        
        # pull the recommendation tag from finnhub
        fh_r = requests.get(fh_url)
        fh_data = fh_r.json()
        
        # clean up the recommendation tag and format it for display
        if fh_data and len(fh_data) > 0:
            latest = fh_data[0]
            # determine majority rating to match your previous format
            if latest['strongBuy'] > latest['buy']: rec = "Strong Buy"
            elif latest['buy'] > latest['hold']: rec = "Buy"
            elif latest['strongSell'] > latest['sell']: rec = "Strong Sell"
            elif latest['sell'] > latest['hold']: rec = "Sell"
            else: rec = "Hold"
        else:
            rec = "Neutral"

    except Exception:
        # if apis fail, return defaults so main.py doesn't crash
        current, target, rec, info = 0, 0, "Neutral", {}

    # return everything including the raw dictionary for further processing
    return current, target, rec, info