import os
import requests
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

print(f"Token: {bot_token}")
print(f"Chat ID: {chat_id}")

url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
payload = {
    "chat_id": chat_id,
    "text": "Hello ini tes dari bot Anda!",
    "parse_mode": "HTML"
}
try:
    response = requests.post(url, json=payload, timeout=5)
    print(response.status_code)
    print(response.text)
except Exception as e:
    print(f"Exception: {e}")
