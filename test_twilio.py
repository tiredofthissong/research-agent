# test_twilio.py — confirms our Twilio setup works by sending you a real SMS
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_number = os.getenv("TWILIO_FROM_NUMBER")
to_number = os.getenv("MY_PHONE_NUMBER")

client = Client(account_sid, auth_token)

message = client.messages.create(
    body="Hey Bromo — your research agent's SMS pipeline works. 🤖",
    from_=from_number,
    to=to_number
)

print(f"✅ SMS sent! Message SID: {message.sid}")
print(f"   From: {from_number}")
print(f"   To:   {to_number}")