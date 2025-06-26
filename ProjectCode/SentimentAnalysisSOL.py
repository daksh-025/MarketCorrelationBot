import yfinance as yf
import re
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import requests
# Load FinBERT pre-trained model
MODEL_NAME = "ProsusAI/finbert"
tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
model = BertForSequenceClassification.from_pretrained(MODEL_NAME)
# Replace with your actual bot token and chat ID
TELEGRAM_BOT_TOKEN = "7971750110:AAEMB0Gfhy4YqZkw24Xsm45ZS9ug9F9iYPo"
TELEGRAM_CHAT_ID = "1240430326"
# Define sentiment labels
sentiment_labels = ["Negative", "Neutral", "Positive"]
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
def analyze_sentiment(text):
    """Predict sentiment for a single block of text."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)

    # Convert logits to probabilities
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    sentiment = sentiment_labels[probs.argmax()]

    return sentiment


def clean_news_headlines(news_list):
    """Extract only the news title from mixed text + metadata."""
    cleaned_news = []
    
    for news in news_list:
        # Remove everything after the first `{` (which starts metadata)
        cleaned_text = re.split(r"\s*{", news, maxsplit=1)[0].strip()
        
        # Remove "None" or extra empty values
        if cleaned_text and cleaned_text.lower() != "none":
            cleaned_news.append(cleaned_text)
    
    return cleaned_news

def get_market_news(ticker="SOL-USD"):
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

# Example usage
btc_news = get_market_news("SOL-USD")
btc_news_cleaned = clean_news_headlines(btc_news)

print(btc_news[:5])  
#print(btc_news_cleaned) 
# Join all news headlines into one single string
btc_news_combined = " ".join(btc_news_cleaned)
print(btc_news_combined) 
sentimnentresult = analyze_sentiment(btc_news_combined)

print(f"Overall SOL Market Sentiment: {sentimnentresult}")
send_telegram_message(f"Overall SOL Market Sentiment: {sentimnentresult}")