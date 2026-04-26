# agent.py — Personal Research Agent
# Usage: python agent.py "your research task here"
#
# The agent uses Claude as its brain, with two tools:
#   - web_search (via Tavily): search the web for info
#   - fetch_url (via Tavily Extract): grab the full content of a specific URL
# Pushover sends milestone updates to your phone.

import os
import time
import memory
import sys
import json
import requests
from dotenv import load_dotenv
from anthropic import Anthropic
from tavily import TavilyClient

load_dotenv()

# === Config ===
MODEL = "claude-sonnet-4-5"
MAX_AGENT_TURNS = 15  # Safety cap so the agent can't loop forever
MID_PROGRESS_THRESHOLD = 3  # Send "still working" ping after this many tool uses

# === Clients ===
anthropic_client = Anthropic()
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


# === Pushover helper ===
def send_push(message: str, title: str = "Research Agent", priority: int = 0):
    """Send a push notification to the user's phone."""
    try:
        requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": os.getenv("PUSHOVER_API_TOKEN"),
                "user": os.getenv("PUSHOVER_USER_KEY"),
                "title": title,
                "message": message,
                "priority": priority,
            },
            timeout=10,
        )
    except Exception as e:
        # Don't crash the agent if push fails — just log it
        print(f"⚠️  Push notification failed: {e}")


# === Tool implementations ===
def web_search(query: str) -> str:
    """Search the web using Tavily and return a JSON string of results."""
    print(f"   🔍 Searching: {query}")
    results = tavily_client.search(query=query, max_results=10, search_depth="advanced")
    # Simplify for the agent — title, url, snippet only
    simplified = [
        {
            "title": r["title"],
            "url": r["url"],
            "snippet": r.get("content", "")[:500],  # Cap length to save tokens
        }
        for r in results.get("results", [])
    ]
    return json.dumps(simplified, indent=2)


def fetch_url(url: str) -> str:
    """Fetch the full content of a URL using Tavily Extract."""
    print(f"   📄 Fetching: {url}")
    try:
        result = tavily_client.extract(urls=[url])
        if result.get("results"):
            content = result["results"][0].get("raw_content", "")
            # Cap content to avoid blowing the context window
            return content[:5000]
        return f"No content extracted from {url}"
    except Exception as e:
        return f"Error fetching {url}: {e}"


# === Tool definitions for Claude ===
TOOLS = [
    {
        "name": "web_search",
        "description": "Search the web for information on a query. Returns a list of relevant results with titles, URLs, and snippets.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query — be specific.",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "fetch_url",
        "description": "Fetch the full text content of a specific URL. Use this when a search result snippet isn't enough and you need the full page.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The full URL to fetch (must include https://).",
                }
            },
            "required": ["url"],
        },
    },
]


# === System prompt ===
SYSTEM_PROMPT = """You are a general-purpose personal research agent for Bromo.

Your job: take a research task, use the web_search and fetch_url tools to gather accurate, current information, and produce a concise, actionable summary.

Guidelines:
- Quality Bar: Consult at least 4 distinct sources. Prefer original, authoritative websites over content aggregators or SEO blogs.
- Verification: Always cross-reference crucial details like prices, hours, and availability to ensure data is not stale.
- Be efficient: Fetch full URLs only when search snippets are insufficient.
- Today's date matters — be aware of the current date for time-sensitive queries.
- Final summary should be SMS-friendly: short, scannable, lead with the answer. Include direct URLs in the format: "Source: https://..."
- If you can't find a good answer, say so directly — don't pad with weak results.
- Strategy: Execute 3-5 distinct search queries covering different angles for every complex task.

When done, return a final text response (no tool call). The system will deliver it to Bromo's phone."""


# === Main agent loop ===
def run_agent(task: str):
    

    messages = [{"role": "user", "content": task}]
    tool_use_count = 0
    mid_progress_sent = False

    for turn in range(MAX_AGENT_TURNS):
        print(f"--- Turn {turn + 1} ---")
        response = anthropic_client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        # If Claude is done (no tool use), deliver final answer
        if response.stop_reason == "end_turn":
            final_text = "".join(
                block.text for block in response.content if block.type == "text"
            )
            print(f"\n✅ Final answer:\n{final_text}\n")
            send_push(final_text, title="✅ Research Complete", priority=1)
    memory.save_session(task, final_text, [])
            return

        # Otherwise, process tool calls
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                tool_use_count += 1
                tool_name = block.name
                tool_input = block.input

                if tool_name == "web_search":
                    result = web_search(tool_input["query"])
                elif tool_name == "fetch_url":
                    result = fetch_url(tool_input["url"])
                else:
                    result = f"Unknown tool: {tool_name}"

                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    }
                )

        messages.append({"role": "user", "content": tool_results})

        # Pause to prevent rate limit crash
        time.sleep(15)

    # Hit max turns without finishing
    print("⚠️  Agent hit max turns without completing.")
    send_push(
        "Hit max turns without a clean answer. Check terminal for partial work.",
        title="⚠️ Research Incomplete",
    )


# === CLI entry point ===
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python agent.py "your research task"')
        sys.exit(1)
    task = " ".join(sys.argv[1:])
    run_agent(task)