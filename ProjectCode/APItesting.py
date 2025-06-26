import yfinance as yf

# Fetch Bitcoin (BTC) price data
btc_data = yf.download("BTC-USD", start="2024-01-01", end="2024-03-01")
print(btc_data["Close"].shape)
print(type(btc_data["Close"]))  # Data type
df =btc_data["Close"].iloc[:, 0]
# Print available columns
print(btc_data.head())
#print(btc_data["Close"])  # Check data
print(df.shape) 