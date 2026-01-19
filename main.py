import streamlit as st 
from helpers.predictor import predict_next_close, show_plot
from helpers.sentiment import get_stock_sentiment
from helpers.analyst import get_analyst_data
from src.process_analyst_buy import process_analyst_data
from helpers.news_quote import get_supporting_quote

st.set_page_config(page_title="TICKER TALK", layout="wide")

def run_analysis():
    # sidebar controls for recruiters to reset the app
    with st.sidebar:
        st.info("Note: This app uses free-tier APIs. If 'N/A' appears, the daily limit may have been reached. Big stocks like AAPL or TSLA are most reliable for testing.")
        st.header("App Controls")
        if st.button("Reset App / Clear Cache"):
            st.cache_data.clear()
            st.success("Cache Cleared!")

    if 'first_run' not in st.session_state:
        st.session_state.first_run = True
        if 'ticker_input' in st.session_state:
            st.session_state.ticker_input = ""

    st.title("      TICKER TALK")
    
    symbol = st.text_input(
        "Enter stock symbol (ex. GOOG):", 
        key="ticker_input"
    ).upper().strip()

    if st.button("Run Analysis"):
        if not symbol: 
            st.warning("❌ Please enter a valid symbol.")
            return
            
        with st.spinner(f"analyzing {symbol}..."): 
            ai_results = predict_next_close(symbol)
            if ai_results is None:
                st.error(f"❌ Could not find data for {symbol}.")
                return

            sentiment = get_stock_sentiment(symbol)
            target, analyst_rec, raw_info = get_analyst_data(symbol)
            
            if raw_info:
                process_results = process_analyst_data(symbol, raw_info)
                # If the processor found a better target, use it; otherwise stick to 'target'
                final_target = process_results.get('target', target)
            else:
                final_target = target
            
            current = ai_results['current_price']
            upside = ((target - current) / current) * 100 if target > 0 else 0

            evidence, source = get_supporting_quote(symbol)

            st.header(f"--- {symbol} ANALYSIS ---")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Current Price", f"${current:.2f}")
            col2.metric("Market Sentiment", f"{sentiment:+.2f}")
            col3.metric("AI Prediction", f"${ai_results['prediction']:.2f}", f"{ai_results['pct_change']:+.2f}%")
            
            # format analyst data for a clean display
            target_val = f"${target:.2f}" if target > 0 else "N/A"
            upside_val = f"{upside:+.2f}% upside" if target > 0 else "Data limited"
            col4.metric("Analyst Target", target_val, upside_val)
            
            col5.metric("Analyst Rating", analyst_rec)

            # scoring logic for verdict
            score = 0
            if sentiment > 0.1: score += 1
            if ai_results['pct_change'] > 0: score += 1
            if "Strong Buy" in analyst_rec: score += 2
            elif "Buy" in analyst_rec: score += 1
            elif "Strong Sell" in analyst_rec: score -= 2
            elif "Sell" in analyst_rec: score -= 1

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
            show_plot(symbol, ai_results['plot_data'], analyst_target=target)

if __name__ == "__main__":
    run_analysis()