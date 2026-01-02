import streamlit as st 
from helpers.predictor import predict_next_close, show_plot
from helpers.sentiment import get_stock_sentiment
from helpers.analyst import get_analyst_data
from src.process_analyst_buy import process_analyst_data
from helpers.news_quote import get_supporting_quote

# page config for the web view
st.set_page_config(page_title="StockAI", layout="wide")

def run_analysis():
    st.title("      STOCK AI RESEARCH TOOL")
    
    # enter stock symbol (ex. GOOG)
    symbol = st.text_input("Enter stock symbol (ex. GOOG):").upper().strip()

    # fetch data button
    if st.button("Run Analysis"):
        # if user enters nothing prompt them to enter a valid stock symbol 
        if not symbol: 
            st.warning("❌ Please enter a valid symbol.")
            return
            
        with st.spinner(f"analyzing {symbol}..."): 
            # fetch data
            ai_results = predict_next_close(symbol)
            # if a stock that doesn't exist was entered prompt user again
            if ai_results is None:
                st.error(f"❌ Could not find data for {symbol}. Please try again.")
                return

            # fetch all data about the stock
            sentiment = get_stock_sentiment(symbol)
            curr_price, target, analyst_rec, raw_info = get_analyst_data(symbol)
            
            analyst_results = process_analyst_data(symbol, raw_info)
            
            # grab data from the news speaking on the stock
            evidence, source = get_supporting_quote(symbol)

            # print all information to the user using metrics
            st.header(f"--- {symbol} ANALYSIS ---")
            
            # Updated to 5 columns to fit the Analyst Rating
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Current Price", f"${ai_results['current_price']:.2f}")
            col2.metric("Market Sentiment", f"{sentiment:+.2f}")
            col3.metric("AI Prediction", f"${ai_results['prediction']:.2f}", f"{ai_results['pct_change']:+.2f}%")
            col4.metric("Analyst Target", f"${analyst_results['target']:.2f}", f"{analyst_results['upside']:+.2f}% upside")
            # NEW: Display the rating directly
            col5.metric("Analyst Rating", analyst_rec)

            # verdict logic
            score = 0
            if sentiment > 0.1: score += 1
            if ai_results['pct_change'] > 0: score += 1
            
            # add or subtract from score based on analyst ratings 
            # we use analyst_rec here to be consistent with the metric above
            if "Strong Buy" in analyst_rec: 
                score += 2
            elif "Buy" in analyst_rec: 
                score += 1
            elif "Strong Sell" in analyst_rec: 
                score -= 2
            elif "Sell" in analyst_rec: 
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
            st.divider()
            st.subheader(f"OVERALL VERDICT: {final_v}")
            st.write(f"**REASONING:** {note}")

            # currently working on adding snippet from news 
            st.info(f"📢 EVIDENCE FROM {source.upper()}:\n   {evidence}")

            # show chart
            st.subheader("Visual Chart")
            show_plot(symbol, ai_results['plot_data'])

if __name__ == "__main__":
    run_analysis()