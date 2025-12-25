# main.py
from helpers.predictor import predict_next_close, show_plot
from helpers.sentiment import get_stock_sentiment
from helpers.analyst import get_analyst_data
from src.process_analyst_buy import process_analyst_data
from helpers.news_quote import get_supporting_quote

def run_analysis():
    print("\n" + "="*45 + "\n      STOCK AI RESEARCH TOOL\n" + "="*45)
    symbol = input("Enter stock symbol (ex. GOOG): ").upper().strip()
    
    # if user enters nothing
    # prompt them to enter a valid stock symbol 
    if not symbol: 
        print("❌ Please enter a valid symbol.")
        # recursive approach
        return run_analysis()

    # fetch data
    ai_results = predict_next_close(symbol)
    # if a stock that doesn't exist was entered
    # prompt user again
    if ai_results is None:
        print(f"❌ Could not find data for {symbol}. Please try again.")
        # recursive approach
        return run_analysis()

    # fetch all data about the stock
    sentiment = get_stock_sentiment(symbol)
    curr_price, target, analyst_rec, raw_info = get_analyst_data(symbol)
    
    analyst_results = process_analyst_data(symbol, raw_info)
    
    # grab data from the news speaking on the stock
    evidence, source = get_supporting_quote(symbol)

    # print all information to the user 
    print(f"\n--- {symbol} ANALYSIS ---")
    print(f"💰 Current Price: ${ai_results['current_price']:.2f}")
    print(f"1. Market Sentiment: {sentiment:+.2f}")
    print(f"2. Math Prediction:  ${ai_results['prediction']:.2f} ({ai_results['pct_change']:+.2f}%)")
    print(f"3. Analyst Target:   ${analyst_results['target']:.2f} ({analyst_results['upside']:+.2f}% upside)")
    print(f"4. Wall Street Rec:  {analyst_results['rec']}")

    # verdict logic
    # initialize score
    score = 0
    # add to score is there is a positive mood on the stock 
    if sentiment > 0.1: score += 1
    # add to score if the percent change is positive (indicates increase)
    if ai_results['pct_change'] > 0: score += 1
    
    # add or subtract from score based on analyst ratings 
    if "Strong Buy" in analyst_results['rec']: 
        score += 2
    elif "Buy" in analyst_results['rec']: 
        score += 1
    elif "Strong Sell" in analyst_results['rec']: 
        score -= 2
    elif "Sell" in analyst_results['rec']: 
        score -= 1

    # decide verdict based on score 
    verdicts = {
        4: ("🟢 STRONG BUY", "AI and Analysts agree."),
        3: ("🟢 BUY", "Bullish expert support."),
        2: ("🟡 HOLD", "Mixed technicals vs analysts."),
        1: ("🟠 CAUTION", "Weak data detected."),
        0: ("🔴 SELL", "Bearish consensus.")
    }
    
    final_v, note = verdicts.get(max(0, score), ("⚪ NEUTRAL", "Mixed signals."))
    
    # print verdict and context to user based on score 
    print("-" * 45)
    print(f"OVERALL VERDICT: {final_v}\nREASONING: {note}")

    # currently working on adding snippet from news 
    print(f"\n📢 EVIDENCE FROM {source.upper()}:\n   {evidence}\n" + "="*45)

    # ask user if they want to see a chart 
    if input("\nShow chart? (yes/no): ").lower() == 'yes':
        # create window to show users the chart 
        show_plot(symbol, ai_results['plot_data'])

if __name__ == "__main__":
    run_analysis()