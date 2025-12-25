import yfinance as yf

# CURRENTLY WORKING ON THIS

def get_supporting_quote(symbol):
    try:
        # initialize the ticker object to find news stories
        ticker = yf.Ticker(symbol)
        # fetch the most recent news articles for this ticker
        news = ticker.news
        
        # handle cases where no recent news is available
        if not news:
            return "no recent news found.", "n/a"
            
        # grab the very first story from the news list
        story = news[0]
        
        # check multiple fields to find the article title
        title = story.get('title') or \
                story.get('headline') or \
                "market update for " + symbol
        
        # identify the publisher or news provider
        source = story.get('publisher') or \
                 story.get('provider', {}).get('name', 'financial news')
                 
        # return the formatted headline and source
        return f"\"{title}\"", source
        
    except Exception:
        # return a fallback message if the fetch fails
        return "headline temporarily unavailable.", "yahoo"