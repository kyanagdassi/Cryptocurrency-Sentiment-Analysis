import requests, pandas as pd, datetime, time

VS = "usd"
DAYS = 30
OUTFILE = "bitcoin_market_cap_monthly.csv"

print("Fetching Bitcoin market cap data for the last month...")

time.sleep(2)

try:
    print("Fetching Bitcoin market cap data...")
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": VS, "days": DAYS, "interval": "daily"}
    
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    
    market_caps = data.get("market_caps", [])
    
    if not market_caps:
        print("No market cap data received")
        exit(1)
    
    dates = []
    btc_market_caps = []
    
    for ts_ms, mcap in market_caps:
        dt = datetime.datetime.utcfromtimestamp(ts_ms/1000.0).date()
        dates.append(dt.isoformat())
        btc_market_caps.append(float(mcap))
    
    df = pd.DataFrame({
        'Date': dates,
        'Bitcoin Market Cap USD': btc_market_caps
    })
    
    df.to_csv(OUTFILE, index=False)
    print(f"\nWrote {len(df)} rows to {OUTFILE}")
    
    current_btc = btc_market_caps[-1]
    
    print(f"\nBitcoin Market Cap Summary (Last 30 Days):")
    print(f"Current: ${current_btc:,.0f}")
    print(f"Current: ${current_btc/1e12:.3f}T")
    print(f"Average: ${sum(btc_market_caps)/len(btc_market_caps):,.0f}")
    print(f"Min: ${min(btc_market_caps):,.0f}")
    print(f"Max: ${max(btc_market_caps):,.0f}")
    
    change_pct = ((btc_market_caps[-1] - btc_market_caps[0]) / btc_market_caps[0]) * 100
    print(f"30-day change: {change_pct:+.2f}%")
    
    print(f"\nFirst few rows:")
    print(df.head())
    
    print(f"\nLast few rows:")
    print(df.tail())

except Exception as e:
    print(f"Error: {e}")
    print("This might be due to rate limiting. Please try again later.")
