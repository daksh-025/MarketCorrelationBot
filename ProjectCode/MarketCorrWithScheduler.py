import yfinance as yf
import pandas as pd
import schedule
import time
import requests
from datetime import datetime

# Telegram & NTFY Configuration
# Replace with your actual bot token and chat ID
TELEGRAM_BOT_TOKEN = "7971750110:AAEMB0Gfhy4YqZkw24Xsm45ZS9ug9F9iYPo"
TELEGRAM_CHAT_ID = "1240430326"
#NTFY_TOPIC = "your-ntfy-topic"

def fetch_market_data():
    """Fetch historical market data for correlation analysis."""
    assets = {
        "Asian Market": "^N225",  # Nikkei 225
        "US Market": "^GSPC",  # S&P 500
        "Gold": "GC=F",  # Gold Futures
        "BTC": "BTC-USD"  # Bitcoin
    }

    market_data = {}

    for name, symbol in assets.items():
        df = yf.download(symbol, start="2024-01-01", end=datetime.today().strftime('%Y-%m-%d'))
        df_close = df["Close"].iloc[:, 0]
        # Ensure 'Close' price exists
        if "Close" in df.columns:
            market_data[name] = df_close  # Each should be a Series
        else:
            print(f"⚠️ No 'Close' price available for {name} ({symbol})")

    # Convert to DataFrame
    df_market = pd.DataFrame(market_data)

    # Drop missing values (some assets may have non-trading days)
    df_market.dropna(inplace=True)

    return df_market

def calculate_correlation():
    """Calculate correlation matrix between Bitcoin and other assets."""
    df_market = fetch_market_data()
    
    # Compute correlation matrix
    correlation_matrix = df_market.corr()
    btc_correlation = correlation_matrix["BTC"]

    return btc_correlation

#def send_ntfy_notification(message):
    """Send a notification via NTFY."""
    requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=message.encode("utf-8"))

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("✅ Message sent successfully!")
    else:
        print(f"⚠️ Failed to send message: {response.text}")
def run_correlation_analysis():
    """Main function to fetch data, calculate correlation, and send results."""
    btc_correlation = calculate_correlation()

    # Prepare report
    report = f"""
📊 **Daily Bitcoin Correlation Report**  
📅 Date: {datetime.today().strftime('%Y-%m-%d')}

🔗 **Bitcoin Correlations**:
🌏 Asian Market: {btc_correlation['Asian Market']:.3f}  
🇺🇸 US Market: {btc_correlation['US Market']:.3f}  
🏅 Gold: {btc_correlation['Gold']:.3f}  

📌 A positive value means BTC moves **in sync** with the asset.  
📌 A negative value means BTC moves **opposite** to the asset.  
"""

    # Send notifications
    #send_ntfy_notification(report)
    print(report)
    send_telegram_message(report)

    print("📢 Correlation report sent successfully!")

# Schedule the script to run daily at a fixed time
schedule.every().day.at("13:59").do(run_correlation_analysis)  # Change time if needed
#run_correlation_analysis()
print("🕒 Correlation script scheduled. Running daily at 09:30 AM.")

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(60)
