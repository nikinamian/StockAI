import streamlit as st 
import requests 
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from threading import RLock

_lock = RLock()

@st.cache_data(ttl=600) 
def predict_next_close(symbol):
    api_key = st.secrets["ALPHA_VANTAGE_KEY"]
    
    # download daily price data
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}&outputsize=compact'
    
    try:
        r = requests.get(url)
        json_data = r.json()
        if "Time Series (Daily)" not in json_data:
            return None
            
        data = pd.DataFrame.from_dict(json_data["Time Series (Daily)"], orient='index')
        data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        data.index = pd.to_datetime(data.index)
        data = data.sort_index().astype(float)
    except Exception:
        return None

    # Linear Regression Logic
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
    with _lock:
        plt.clf()
        plt.figure(figsize=(8, 5))

        plt.plot(plot_data['dates'], plot_data['trend'], label="AI Trend", color="red", linestyle="--")
        plt.plot(plot_data['dates'], plot_data['actual'], label="Price", color="#1f77b4", alpha=0.8)
        
        # Plot Analyst Target if available
        if analyst_target > 0:
            plt.plot(plot_data['dates'][-1], analyst_target, 'o', color='orange', markersize=8)
            plt.text(plot_data['dates'][-1], analyst_target, f' Analyst: ${analyst_target:.2f}', color='orange', fontweight='bold')

        # Plot AI Prediction
        plt.plot(plot_data['dates'][-1], plot_data['target_price'], 'o', color='green', markersize=8)
        plt.text(plot_data['dates'][-1], plot_data['target_price'], f' AI Prediction: ${plot_data['target_price']:.2f}', color='green', fontweight='bold')

        # Plot Current Price
        plt.plot(plot_data['dates'][-1], plot_data['current_price'], 'o', color='blue', markersize=8)
        plt.text(plot_data['dates'][-1], plot_data['current_price'], f' Current Price: ${plot_data['current_price']:.2f}', color='blue', fontweight='bold')

        plt.fill_between(plot_data['dates'], plot_data['lower_band'], plot_data['upper_band'], color='gray', alpha=0.2)
        plt.title(f"AI Analysis: {symbol}")
        st.pyplot(plt.gcf())