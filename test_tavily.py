# test_tavily.py — confirms our Tavily API key works
import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Quick search to verify
response = client.search(
    query="Museum of Illusions Denver hours",
    max_results=3
)

print("✅ Tavily responded with results:\n")
for i, result in enumerate(response["results"], 1):
    print(f"{i}. {result['title']}")
    print(f"   {result['url']}\n")