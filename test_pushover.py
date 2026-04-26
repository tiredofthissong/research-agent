# test_pushover.py — confirms our Pushover setup works by sending a push notification
import os
import requests
from dotenv import load_dotenv

load_dotenv()

response = requests.post(
    "https://api.pushover.net/1/messages.json",
    data={
        "token": os.getenv("PUSHOVER_API_TOKEN"),
        "user": os.getenv("PUSHOVER_USER_KEY"),
        "message": "Hey Bromo — your research agent's push pipeline works. 🤖",
        "title": "Research Agent Test",
    }
)

if response.status_code == 200:
    print("✅ Push sent successfully!")
    print(f"   Response: {response.json()}")
else:
    print(f"❌ Failed with status {response.status_code}")
    print(f"   Response: {response.text}")