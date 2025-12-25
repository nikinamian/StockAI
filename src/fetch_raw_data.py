import yfinance as yf
import os
import pandas as pd

def run_fetch(ticker_symbol):
    # create raw data folder if it doesn't exist
    os.makedirs('data/raw', exist_ok=True)
    # initialize the ticker object to pull data
    ticker = yf.Ticker(ticker_symbol)
    
    # historical prices
    # download one year of daily price history
    prices = ticker.history(period="1y")
    # save price data to a local csv file
    prices.to_csv(f'data/raw/{ticker_symbol}_prices.csv')
    
    # analyst recommendations and info
    # pull summary of wall street analyst ratings
    recs = ticker.recommendations_summary
    if recs is not None:
        # save analyst summary if data is available
        recs.to_csv(f'data/raw/{ticker_symbol}_analyst_summary.csv')
    
    # fetch general company information and convert to dataframe
    info = pd.DataFrame([ticker.info])
    # save company metadata to raw folder
    info.to_csv(f'data/raw/{ticker_symbol}_info.csv')
    
    # notify user that the raw data download is finished
    print(f"--- raw data for {ticker_symbol} saved ---")