import streamlit as st 
from helpers.predictor import predict_next_close, show_plot
from helpers.sentiment import get_stock_sentiment
from helpers.analyst import get_analyst_data
from src.process_analyst_buy import process_analyst_data
from helpers.news_quote import get_supporting_quote

st.set_page_config(page_title="TICKER TALK", layout="wide")

def run_analysis():
    st.title("TICKER TALK")
    
    symbol = st.text_input("Enter stock symbol (ex. GOOG):", key="ticker_input").upper().strip()

    if st.button("Run Analysis"):
        if not symbol: 
            st.warning("❌ Please enter a valid symbol.")
            return
            
        with st.spinner(f"analyzing {symbol}..."): 
            # 1. Fetch AI prediction
            ai_results = predict_next_close(symbol)
            if ai_results is None:
                st.error(f"❌ Could not find data for {symbol}.")
                return

            # 2. Fetch Analyst data (Target and Rating)
            target, analyst_rec, raw_info = get_analyst_data(symbol)
            
            # 3. Process data for storage
            process_analyst_data(symbol, raw_info)
            
            # 4. Fetch sentiment and quotes
            sentiment = get_stock_sentiment(symbol)
            evidence, source = get_supporting_quote(symbol)

            # Calculation for display
            current = ai_results['current_price']
            upside = ((target - current) / current) * 100 if target > 0 else 0

            # UI Display
            st.header(f"--- {symbol} ANALYSIS ---")
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Current Price", f"${current:.2f}")
            col2.metric("Market Sentiment", f"{sentiment:+.2f}")
            col3.metric("AI Prediction", f"${ai_results['prediction']:.2f}", f"{ai_results['pct_change']:+.2f}%")
            col4.metric("Analyst Target", f"${target:.2f}", f"{upside:+.2f}% upside")
            col5.metric("Analyst Rating", analyst_rec)

            # Verdict logic
            score = 0
            if sentiment > 0.1: score += 1
            if ai_results['pct_change'] > 0: score += 1
            if "Strong Buy" in analyst_rec: score += 2
            elif "Buy" in analyst_rec: score += 1
            
            verdicts = {4: ("🟢 STRONG BUY", "AI and Analysts agree."), 3: ("🟢 BUY", "Bullish support."), 2: ("🟡 HOLD", "Mixed technicals."), 1: ("🟠 CAUTION", "Weak data."), 0: ("🔴 SELL", "Bearish consensus.")}
            final_v, note = verdicts.get(max(0, score), ("⚪ NEUTRAL", "Mixed signals."))
            
            st.divider()
            st.subheader(f"OVERALL VERDICT: {final_v}")
            st.write(f"**REASONING:** {note}")
            st.info(f"📢 EVIDENCE FROM {source.upper()}:\n   {evidence}")

            st.subheader("Visual Chart")
            show_plot(symbol, ai_results['plot_data'], analyst_target=target)

if __name__ == "__main__":
    run_analysis()