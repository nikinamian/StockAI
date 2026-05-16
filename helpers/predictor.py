import streamlit as st 
import requests 
import pandas as pd
import numpy as np
import matplotlib
# change backend to Agg so it works on the cloud server
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from threading import RLock

# prevent website from crashing when many people visit
_lock = RLock()

# remember data for 10 minutes to prevent over pinging
@st.cache_data(ttl=600) 
def predict_next_close(symbol):
    import yfinance as yf
    
    try:
        # 1. Fetch data via yfinance (No API key needed!)
        ticker = yf.Ticker(symbol)
        # 60 days is plenty for a short-term trendline
        data = ticker.history(period="60d")
        
        if data.empty:
            return None
            
        # 2. Format to match your original dataframe structure
        # yfinance returns 'Close', 'Open', etc. already.
        data.index = pd.to_datetime(data.index)
        data = data.sort_index().astype(float)
        
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

    # --- Your Original ML Logic (Keep this exactly as is) ---
    data['Day'] = np.arange(len(data))
    X = data[['Day']].values
    y = data['Close'].values.flatten()

    model = LinearRegression()
    model.fit(X, y)

    prediction = model.predict(np.array([[len(data)]])).item()
    current_price = y[-1]
    
    pct_change = ((prediction - current_price) / current_price) * 100
    y_trend = model.predict(X)
    std_dev = np.std(y - y_trend) 
    
    return {
        "symbol": symbol,
        "current_price": current_price,
        "prediction": prediction,
        "pct_change": pct_change,
        "plot_data": {
            'dates': data.index,
            'actual': y,
            'trend': y_trend,
            'upper_band': y_trend + std_dev, 
            'lower_band': y_trend - std_dev, 
            'target_price': prediction,
            "current_price": current_price
        }
    }

def show_plot(symbol, plot_data, analyst_target=0.0):
    # use a lock to handle multiple users safely
    with _lock:
        # clear the figure so plots don't overlap
        plt.clf()
        # setup the chart window size
        plt.figure(figsize=(5, 3.5))

        # plot the ai generated trendline
        plt.plot(plot_data['dates'], plot_data['trend'], label="Stock Trendline", color="red", linestyle="--")
        
        # plot the actual historical price
        plt.plot(plot_data['dates'], plot_data['actual'], label="Stock Price", color="#1f77b4", alpha=0.8)
        
        # plot the ai prediction
        plt.plot(plot_data['dates'][-1], plot_data['target_price'], 'o', color='green', markersize=8, label="AI Prediction for Next Close")

        # plot the current price
        plt.plot(plot_data['dates'][-1], plot_data['current_price'], 'o', color='blue', markersize=8, label="Current Price")

        # fill the volatility safety zone
        plt.fill_between(plot_data['dates'], plot_data['lower_band'], plot_data['upper_band'], color='gray', alpha=0.2, label="Safety Zone")
        
        # put the key in the top left so it's easy to read
        plt.legend(loc='lower left', prop={'size': 8})

        # finish and display the chart
        plt.title(f"AI Analysis: {symbol}")
        plt.tight_layout()
        st.pyplot(plt.gcf())