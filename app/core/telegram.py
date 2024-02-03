import requests
import os 

def send_message(message):
    requests.post(f"https://api.telegram.org/bot{os.getenv('BOT_KEY')}/sendMessage", {
        "chat_id": os.environ.get('BOT_CHAT_ID'),
        "text": message
    })