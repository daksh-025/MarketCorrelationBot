import yfinance as yf
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import requests
from datetime import datetime, timedelta

# Load FinBERT Model
MODEL_NAME = "ProsusAI/finbert"
tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
model = BertForSequenceClassification.from_pretrained(MODEL_NAME)

# Replace with your actual bot token and chat ID
TELEGRAM_BOT_TOKEN = "7971750110:AAEMB0Gfhy4YqZkw24Xsm45ZS9ug9F9iYPo"
TELEGRAM_CHAT_ID = "1240430326"

# Define sentiment labels
sentiment_labels = ["Negative", "Neutral", "Positive"]

def analyze_sentiment(text):
    """Predict sentiment for a single block of text."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)

    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    sentiment_score = probs[0][2].item() * 100  # Probability of "Positive" sentiment
    sentiment_label = sentiment_labels[probs.argmax().item()]  # Get label

    return sentiment_score, sentiment_label

def clean_news_headlines(news_list):
    """Extract only the news title from mixed text + metadata."""
    cleaned_news = []
    
    for news in news_list:
        # Remove everything after the first { (which starts metadata)
        cleaned_text = re.split(r"\s*{", news, maxsplit=1)[0].strip()
        
        # Remove "None" or extra empty values
        if cleaned_text and cleaned_text.lower() != "none":
            cleaned_news.append(cleaned_text)
    
    return cleaned_news

def get_market_news(ticker="BTC-USD"):
    """Fetch recent news for the given ticker symbol from Yahoo Finance."""
    asset = yf.Ticker(ticker)
    news = asset.news  # Get news articles

    news_list = []
    for article in news:
        content = article.get("content", {})  # Get the 'content' dictionary safely
        title = content.get("title", "No Title")  # Extract the title
        link = content.get("clickThroughUrl", "No Link")  # Extract the URL (key varies)
        news_list.append(f"{title} {link}")

    return news_list

def fetch_sentiment_data(asset_name, ticker):
    """Fetch real sentiment data from news headlines over 10 days."""
    dates = [datetime.today() - timedelta(days=i) for i in range(10)]
    sentiment_scores = []
    sentiment_labels_list = []

    for date in dates:
        news = get_market_news(ticker)
        combined_news = " ".join(clean_news_headlines(news))
        sentiment_score, sentiment_label = analyze_sentiment(combined_news)
        sentiment_scores.append(sentiment_score)
        sentiment_labels_list.append(sentiment_label)

    data = pd.DataFrame({"Date": dates, "Sentiment": sentiment_scores, "Label": sentiment_labels_list})
    return data

def create_chart(data, asset_name):
    """Generate and save the sentiment analysis chart with custom colors."""
    plt.figure(figsize=(10, 5))
    colors = ["blue" if label == "Positive" else "red" for label in data["Label"]]
    plt.scatter(data["Date"], data["Sentiment"], color=colors, label="Sentiment", zorder=3)
    plt.plot(data["Date"], data["Sentiment"], linestyle="-", color="black", alpha=0.5, zorder=2)
    plt.title(f"{asset_name} Market Sentiment Analysis")
    plt.xlabel("Date")
    plt.ylabel("Sentiment Score")
    plt.grid(True, linestyle="--", alpha=0.7, zorder=1)
    plt.xticks(rotation=45)
    chart_filename = f"{asset_name}_sentiment_chart.png"
    plt.savefig(chart_filename)
    plt.close()
    return chart_filename

def send_telegram_image(image_path, caption=""):
    """Send an image to Telegram chat."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    with open(image_path, "rb") as image_file:
        response = requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption}, files={"photo": image_file})
    if response.status_code == 200:
        print("✅ Image sent successfully!")
    else:
        print(f"⚠️ Failed to send image: {response.text}")

# Run Analysis for BTC, ETH, and SOL
for asset, ticker in {"Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "Solana": "SOL-USD"}.items():
    sentiment_data = fetch_sentiment_data(asset, ticker)
    chart_path = create_chart(sentiment_data, asset)
    send_telegram_image(chart_path, f"📊 {asset} Market Sentiment Analysis")

print("✅ Sentiment analysis and Telegram notification completed!")
