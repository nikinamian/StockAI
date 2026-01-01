import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('MacOSX') 
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

def predict_next_close(symbol):
    # download one year of daily price data
    data = yf.download(symbol, period="1y", interval="1d", auto_adjust=True)
    if data.empty:
        return None
    
    # fetch analyst target
    ticker = yf.Ticker(symbol)

    # get standard average analyst target from Yahoo Finance
    analyst_target = ticker.info.get('targetMeanPrice', None)

    # prepare day count for linear regression input
    data['Day'] = np.arange(len(data))
    X = data[['Day']].values
    y = data['Close'].values.flatten()

    # initialize and train the linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # project price for the very next trading day
    next_day = np.array([[len(data)]])
    prediction = model.predict(next_day).item()
    current_price = y[-1]
    # calculate the percentage gap between current and predicted price
    pct_change = ((prediction - current_price) / current_price) * 100

    # determine trend label based on direction
    trend_label = "UP" if pct_change > 0 else "DOWN"

    # determine buy/sell/wait signal based on change threshold
    if pct_change > 1.5:
        buy_sell_signal = "BUY"
    elif pct_change < -1.5:
        buy_sell_signal = "SELL"
    else:
        buy_sell_signal = "HOLD/WAIT"
        
    # calculate the trendline and volatility bands
    y_trend = model.predict(X)
    std_dev = np.std(y - y_trend) 
    
    # package all findings into a dictionary for main to use
    results = {
            "symbol": symbol,
            "current_price": current_price,
            "prediction": prediction,
            "pct_change": pct_change,
            "trend": trend_label,
            "signal": buy_sell_signal,
            "data": data, 
            "plot_data": {
                'dates': data.index,
                'actual': y,
                'trend': y_trend,
                'upper_band': y_trend + std_dev, 
                'lower_band': y_trend - std_dev, 
                'target_price': prediction,
                'analyst_target' : analyst_target
            }
        }

    return results 

def show_plot(symbol, plot_data):
    # setup the chart window size
    plt.figure(figsize=(8, 5))

    # get analyst target from plot data dictionary
    analyst_target = plot_data.get('analyst_target')
    
    # plot the actual historical price
    plt.plot(plot_data['dates'], plot_data['actual'], label="Price", color="#1f77b4", alpha=0.8)
    # label the exact current price at the last data point
    current_price = plot_data['actual'][-1]
    plt.text(plot_data['dates'][-1], current_price, f'  ${current_price:.2f}', 
             verticalalignment='center', fontweight='bold', color='#1f77b4')
    # label the exact AI target price 
    prediction = plot_data['target_price']
    plt.text(plot_data['dates'][-1], prediction, f'  ${prediction:.2f}', 
             verticalalignment='center', fontweight='bold', color='#1f77b4')
    # add analyst target line and label
    plt.axhline(y=analyst_target, color='orange', linestyle='--', alpha=0.6, label="Analyst Target")
    plt.text(plot_data['dates'][0], analyst_target, f' Analyst Target: ${analyst_target:.2f}', 
             color='orange', fontweight='bold', va='bottom', fontsize=9)
    # plot the ai generated trendline
    plt.plot(plot_data['dates'], plot_data['trend'], label="AI Trend", color="red", linestyle="--")
    # fill the volatility safety zone
    plt.fill_between(plot_data['dates'], plot_data['lower_band'], plot_data['upper_band'], color='gray', alpha=0.2)
    # draw a horizontal line at the ai target price
    plt.axhline(y=plot_data['target_price'], color='green', linestyle=':', alpha=0.7)

    # add legend text for visual clarity
    info_text = "● Blue: Stock Price\n● Gray: Safety Zone\n● Green: AI Target\n● Red: Trendline"
    plt.text(0.02, 0.95, info_text, transform=plt.gca().transAxes, verticalalignment='top', fontsize=8, bbox=dict(facecolor='white', alpha=0.8))

    # finish and display the chart
    plt.title(f"AI Analysis: {symbol}")
    plt.tight_layout()
    plt.show()