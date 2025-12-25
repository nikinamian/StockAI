import pandas as pd
import os

def process_analyst_data(ticker_symbol, info_data):
    # create processed folder if it doesn't exist
    os.makedirs('data/processed', exist_ok=True)
    
    # pull raw price data from info dictionary
    current_price = info_data.get('currentPrice', 0)
    target_price = info_data.get('targetMeanPrice', 0)
    
    # calculate the gap between target and current price
    upside = 0
    if current_price > 0:
        # standard math for percentage growth
        upside = ((target_price - current_price) / current_price) * 100
    
    # save a local csv record of the analyst data
    pd.DataFrame({
        'Ticker': [ticker_symbol],
        'Upside': [round(upside, 2)],
        'Rec': [info_data.get('recommendationKey')]
    }).to_csv(f'data/processed/{ticker_symbol}_analyst.csv', index=False)
    
    # return a clean dictionary for main to use
    return {
        "target": target_price,
        "upside": upside,
        # format the recommendation string (e.g. strong_buy becomes Strong Buy)
        "rec": info_data.get('recommendationKey', 'N/A').replace('_', ' ').title()
    }