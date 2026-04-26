# test_claude.py — confirms our Anthropic API key works
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()  # Loads .env file into environment

client = Anthropic()  # Auto-reads ANTHROPIC_API_KEY from env

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=100,
    messages=[
        {"role": "user", "content": "Say hello and confirm you're working in 1 sentence."}
    ]
)

print("✅ Claude responded:")
print(response.content[0].text)