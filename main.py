import streamlit as st 
from helpers.predictor import predict_next_close, show_plot
from helpers.sentiment import get_stock_sentiment
from helpers.analyst import get_analyst_data
from src.process_analyst_buy import process_analyst_data
from helpers.news_quote import get_supporting_quote

# page config for the web view
st.set_page_config(page_title="TICKER TALK", layout="wide")

def run_analysis():
    # 1. Sidebar for app management
    with st.sidebar:
        st.header("App Controls")
        if st.button("Reset App / Clear Cache"):
            st.cache_data.clear()
            st.success("Cache Cleared! Running a fresh analysis.")

    # 2. auto-reset logic: clear the search box if this is a fresh visit from a link
    if 'first_run' not in st.session_state:
        st.session_state.first_run = True
        # this wipes the last typed symbol so the user starts fresh
        if 'ticker_input' in st.session_state:
            st.session_state.ticker_input = ""

    st.title("      TICKER TALK")
    
    # 3. we give the input a key so we can control its reset behavior
    symbol = st.text_input(
        "Enter stock symbol (ex. GOOG):", 
        key="ticker_input"
    ).upper().strip()

    # fetch data button
    if st.button("Run Analysis"):
        if not symbol: 
            st.warning("❌ Please enter a valid symbol.")
            return
            
        with st.spinner(f"analyzing {symbol}..."): 
            # fetch data
            ai_results = predict_next_close(symbol)
            if ai_results is None:
                st.error(f"❌ Could not find data for {symbol}. Please try again.")
                return

            # fetch all data about the stock
            sentiment = get_stock_sentiment(symbol)
            # GET THE DATA: target and analyst_rec come from here
            target, analyst_rec, raw_info = get_analyst_data(symbol)
            
            process_analyst_data(symbol, raw_info)
            
            # calculate upside manually to ensure it is never zero
            current = ai_results['current_price']
            upside = ((target - current) / current) * 100 if target > 0 else 0

            # grab data from the news speaking on the stock
            evidence, source = get_supporting_quote(symbol)

            # print all information to the user using metrics
            st.header(f"--- {symbol} ANALYSIS ---")
            
            # Updated to 5 columns to show the Rating
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Current Price", f"${current:.2f}")
            col2.metric("Market Sentiment", f"{sentiment:+.2f}")
            col3.metric("AI Prediction", f"${ai_results['prediction']:.2f}", f"{ai_results['pct_change']:+.2f}%")
            
            # FIXED: Handle missing data gracefully for recruiter applications
            target_display = f"${target:.2f}" if target > 0 else "N/A"
            upside_display = f"{upside:+.2f}% upside" if target > 0 else "API limit hit"
            col4.metric("Analyst Target", target_display, upside_display)
            
            # NEW: This prints the "Buy/Strong Buy" rating on screen
            col5.metric("Analyst Rating", analyst_rec)

            # verdict logic
            score = 0
            if sentiment > 0.1: score += 1
            if ai_results['pct_change'] > 0: score += 1
            
            # we use analyst_rec for the scoring check
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
            
            st.divider()
            st.subheader(f"OVERALL VERDICT: {final_v}")
            st.write(f"**REASONING:** {note}")
            st.info(f"📢 EVIDENCE FROM {source.upper()}:\n   {evidence}")

            st.subheader("Visual Chart")
            # Pass the target price to ensure the plot matches the metrics
            show_plot(symbol, ai_results['plot_data'], analyst_target=target)

if __name__ == "__main__":
    run_analysis()