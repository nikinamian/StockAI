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
    # fetch alpha vantage api key from streamlit secrets
    api_key = st.secrets["ALPHA_VANTAGE_KEY"]
    
    # download daily price data using alpha vantage
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}&outputsize=compact'
    
    try:
        r = requests.get(url)
        json_data = r.json()
        
        # verify if valid data was returned
        if "Time Series (Daily)" not in json_data:
            return None
            
        # convert json to the same dataframe format used before
        data = pd.DataFrame.from_dict(json_data["Time Series (Daily)"], orient='index')
        data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        data.index = pd.to_datetime(data.index)
        # sort oldest to newest to match previous behavior
        data = data.sort_index().astype(float)
    except Exception:
        return None

    # prepare day count for linear regression input
    data['Day'] = np.arange(len(data))
    X = data[['Day']].values
    y = data['Close'].values.flatten()

    # initialize and train the linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # project price for the very next trading day
    prediction = model.predict(np.array([[len(data)]])).item()
    current_price = y[-1]
    
    # calculate the percentage gap between current and predicted price
    pct_change = ((prediction - current_price) / current_price) * 100
    
    # calculate the trendline and volatility bands
    y_trend = model.predict(X)
    std_dev = np.std(y - y_trend) 
    
    # package all findings into a dictionary for main to use
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
        plt.figure(figsize=(8, 5))

        # plot the ai generated trendline
        plt.plot(plot_data['dates'], plot_data['trend'], label="AI Trend", color="red", linestyle="--")
        
        # plot the actual historical price
        plt.plot(plot_data['dates'], plot_data['actual'], label="Price", color="#1f77b4", alpha=0.8)
        
        # add analyst target and label if it exists
        if analyst_target > 0:
            plt.plot(plot_data['dates'][-1], analyst_target, 'o', color='orange', markersize=8)
            plt.text(plot_data['dates'][-1], analyst_target, f' Analyst: ${analyst_target:.2f}', color='orange', fontweight='bold')

        # plot the ai prediction
        plt.plot(plot_data['dates'][-1], plot_data['target_price'], 'o', color='green', markersize=8)
        plt.text(plot_data['dates'][-1], plot_data['target_price'], f' AI Prediction: ${plot_data['target_price']:.2f}', color='green', fontweight='bold')

        # plot the current price
        plt.plot(plot_data['dates'][-1], plot_data['current_price'], 'o', color='blue', markersize=8)
        plt.text(plot_data['dates'][-1], plot_data['current_price'], f' Current Price: ${plot_data['current_price']:.2f}', color='blue', fontweight='bold')

        # fill the volatility safety zone
        plt.fill_between(plot_data['dates'], plot_data['lower_band'], plot_data['upper_band'], color='gray', alpha=0.2)
        
        # finish and display the chart
        plt.title(f"AI Analysis: {symbol}")
        plt.tight_layout()
        st.pyplot(plt.gcf())