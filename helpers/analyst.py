import streamlit as st
import requests

def get_analyst_data(symbol):
    # use secret keys from streamlit settings
    av_key = st.secrets["ALPHA_VANTAGE_KEY"]
    fh_key = st.secrets["FINNHUB_API_KEY"]
    
    # fetch company info from alpha vantage overview
    av_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={av_key}"
    # fetch wall street recommendation ratings from finnhub
    fh_url = f"https://finnhub.io/api/v1/stock/recommendation?symbol={symbol}&token={fh_key}"
    
    try:
        # 1. get company info and target price
        av_r = requests.get(av_url)
        info = av_r.json()
        
        # Alpha Vantage uses 'AnalystTargetPrice'
        target_val = info.get('AnalystTargetPrice')
        
        # convert string to float safely; if missing, use 0
        if target_val and target_val != 'None':
            target = float(target_val)
        else:
            target = 0.0
            
        current = 0 # predictor.py handles the actual current price display
        
        # 2. get the recommendation tag from finnhub
        fh_r = requests.get(fh_url)
        fh_data = fh_r.json()
        
        # determine majority rating to match your previous format
        if isinstance(fh_data, list) and len(fh_data) > 0:
            latest = fh_data[0] # Get the most recent month of analyst data
            
            # Scoring logic to find the strongest recommendation
            buy_score = latest.get('buy', 0)
            strong_buy = latest.get('strongBuy', 0)
            sell_score = latest.get('sell', 0)
            strong_sell = latest.get('strongSell', 0)
            hold_score = latest.get('hold', 0)

            # Assign the string that main.py is looking for
            if strong_buy > buy_score and strong_buy > hold_score:
                rec = "Strong Buy"
            elif buy_score >= hold_score and buy_score > sell_score:
                rec = "Buy"
            elif strong_sell > sell_score and strong_sell > hold_score:
                rec = "Strong Sell"
            elif sell_score > hold_score:
                rec = "Sell"
            else:
                rec = "Hold"
        else:
            rec = "Neutral"

    except Exception:
        # if apis fail, return defaults so main.py doesn't crash
        current, target, rec, info = 0.0, 0.0, "Neutral", {}

    # return everything including the raw dictionary for further processing
    return current, target, rec, info