import yfinance as yf

def get_analyst_data(symbol):
    # initialize the ticker object to access market data
    ticker = yf.Ticker(symbol)
    # pull the full dictionary of company information
    info = ticker.info
    
    # try to get the current price from the info dictionary
    current = info.get('currentPrice')
    
    # if info price is missing check recent trading history
    if not current:
        # download the latest single day of data
        hist = ticker.history(period="1d")
        # use the last closing price if history is found
        current = hist['Close'].iloc[-1] if not hist.empty else 0
        
    # extract the average price target from wall street analysts
    target = info.get('targetMeanPrice', 0)
    # clean up the recommendation tag and format it for display
    rec = info.get('recommendationKey', 'Neutral').replace('_', ' ').title()
    
    # return everything including the raw dictionary for further processing
    return current, target, rec, info