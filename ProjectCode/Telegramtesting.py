import requests

# Replace with your actual bot token and chat ID
TELEGRAM_BOT_TOKEN = "7971750110:AAEMB0Gfhy4YqZkw24Xsm45ZS9ug9F9iYPo"
TELEGRAM_CHAT_ID = "1240430326"

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

# Send a test message

send_telegram_message("Hi, this is a test message from my bot!")
