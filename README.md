Try it out! https://tickertalkai.streamlit.app/ 

<img width="1020" height="472" alt="Screen Shot 2026-05-15 at 9 49 43 PM" src="https://github.com/user-attachments/assets/eb83b81a-50a3-4bde-ba29-954d0bcf1e92" />
<img width="1001" height="284" alt="Screen Shot 2026-05-15 at 9 49 55 PM" src="https://github.com/user-attachments/assets/023b69c4-1fc5-43cc-8cc7-bc1a2f6c41d2" />
<img width="969" height="403" alt="Screen Shot 2026-05-15 at 10 01 23 PM" src="https://github.com/user-attachments/assets/d36ca4cd-86ef-4700-b592-b3c66c8c4cec" />



A personal stock analyzer pulling data from the news and real-time prices.
Limit your time researching with this quick AI analyzer!

Currently working on adding a snippet from the news to support verdict.
Also working on grabbing more data using APIs to give the most accurate result.

⚠️ Challenges:
Building this with free-tier infrastructure introduced a few real-world constraints that I've worked to mitigate:

- API Limits & Quotas: Since I'm using free keys (like Alpha Vantage), the app is subject to strict rate limits (e.g., 5 calls/min, 25 calls/day). If the limit is hit, some metrics may temporarily fall back to "N/A".

- Shared Infrastructure: Deploying on Streamlit Cloud means sharing IP addresses with other apps. If those apps heavily query the same data sources (like Yahoo Finance), our requests can occasionally be throttled or blocked.

- Data Gaps: Small-cap or recently IPO'd stocks (e.g., APLD) often lack deep analyst coverage in these specific databases, which is why some fields might appear as "Data limited".

- Mitigation Strategy: To maintain a smooth UX, I implemented a triple-layer failover (Finnhub → Yahoo Finance → N/A) and used Streamlit Caching (@st.cache_data) to persist data for 10 minutes per search, drastically reducing redundant API calls.
