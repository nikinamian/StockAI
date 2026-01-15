Try it out! https://tickertalkai.streamlit.app/ 

<img width="890" height="425" alt="Screenshot 2026-01-11 at 4 52 29 PM" src="https://github.com/user-attachments/assets/d92d946d-1f52-4731-b392-d0b34d2c485b" />

<img width="865" height="589" alt="Screenshot 2026-01-11 at 4 52 58 PM" src="https://github.com/user-attachments/assets/36c00cfc-535d-4232-9cb3-5b26dc6373f4" />

A personal stock analyzer pulling data from the news and real-time prices.
Limit your time researching with this quick AI analyzer!

Currently working on adding a snippet from the news to support verdict.
Also working on making math plot more informative. 

⚠️ Challenges:
Building this with free-tier infrastructure introduced a few real-world constraints that I've worked to mitigate:

- API Limits & Quotas: Since I'm using free keys (like Alpha Vantage), the app is subject to strict rate limits (e.g., 5 calls/min, 25 calls/day). If the limit is hit, some metrics may temporarily fall back to "N/A".

- Shared Infrastructure: Deploying on Streamlit Cloud means sharing IP addresses with other apps. If those apps heavily query the same data sources (like Yahoo Finance), our requests can occasionally be throttled or blocked.

- Data Gaps: Small-cap or recently IPO'd stocks (e.g., APLD) often lack deep analyst coverage in these specific databases, which is why some fields might appear as "Data limited".

- Mitigation Strategy: To maintain a smooth UX, I implemented a triple-layer failover (Finnhub → Yahoo Finance → N/A) and used Streamlit Caching (@st.cache_data) to persist data for 10 minutes per search, drastically reducing redundant API calls.
