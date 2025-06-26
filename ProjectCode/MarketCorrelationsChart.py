import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import requests

# Define assets and fetch historical data
assets = {
    "Asian Market": "^N225",  # Nikkei 225
    "US Market": "^GSPC",  # S&P 500
    "Gold": "GC=F",  # Gold Futures
    "BTC": "BTC-USD"  # Bitcoin
}

market_data = {}

for name, symbol in assets.items():
    df = yf.download(symbol, start="2024-01-01", end="2024-03-01")
    df_close = df["Close"].iloc[:, 0] 

    # Ensure 'Close' price exists
    if "Close" in df.columns:
        market_data[name] = df_close  # Store closing prices
        
    else:
        print(f"⚠️ No 'Close' price available for {name} ({symbol})")

# Convert dictionary to DataFrame (pandas automatically aligns by date)
df_market = pd.DataFrame(market_data)

# Drop missing values (some assets may have non-trading days)
df_market.dropna(inplace=True)

# Calculate rolling correlation with BTC
rolling_correlation = df_market.rolling(window=10).corr(df_market['BTC'])

# Plot correlation trends over time
plt.figure(figsize=(12, 6))
for market in ["Asian Market", "US Market", "Gold"]:
    plt.plot(rolling_correlation.index, rolling_correlation[market], label=f'{market} vs BTC')

plt.title("Bitcoin Correlation with Markets Over Time")
plt.xlabel("Date")
plt.ylabel("Correlation Coefficient")
plt.legend()
plt.grid()

# Save the plot
chart_filename = "btc_market_correlation.png"
plt.savefig(chart_filename)
plt.close()

# Telegram bot credentials
TELEGRAM_BOT_TOKEN = "7971750110:AAEMB0Gfhy4YqZkw24Xsm45ZS9ug9F9iYPo"
TELEGRAM_CHAT_ID = "1240430326"

def send_telegram_image(image_path, caption=""):
    """Send an image to Telegram chat."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    with open(image_path, "rb") as image_file:
        response = requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption}, files={"photo": image_file})
    
    if response.status_code == 200:
        print("✅ Image sent successfully!")
    else:
        print(f"⚠️ Failed to send image: {response.text}")

# Send the correlation chart to Telegram
send_telegram_image(chart_filename, "📊 Bitcoin Correlation with Global Markets")

print("✅ Correlation analysis and Telegram notification completed!")
