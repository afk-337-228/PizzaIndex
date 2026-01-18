from http.server import BaseHTTPRequestHandler
import os
import json
import requests
from bs4 import BeautifulSoup
import time
import random

# Configuration
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
CRON_SECRET = os.environ.get("CRON_SECRET")
IS_TEST_MODE = os.environ.get("IS_TEST_MODE", "False").lower() == "true"

# Target Locations
LOCATIONS = [
    {"name": "Domino's Pizza", "query": "Domino's Pizza 15th St S Arlington VA busyness"},
    {"name": "Papa John's Pizza", "query": "Papa John's Pizza 23rd St S Arlington VA busyness"},
    {"name": "Wiseguy Pizza", "query": "Wiseguy Pizza 710 12th St S Arlington VA busyness"}
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

def scrape_google_busyness(query):
    """
    Scrapes Google Search for busyness data.
    Returns: int (0-100) or None if not found.
    """
    url = f"https://www.google.com/search?q={query}&hl=en"
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        if response.status_code != 200:
            print(f"Error scraping {query}: Status {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Strategy 1: Look for "Live" or "Busy" text in specific areas
        # This is highly experimental as Google changes classes frequently.
        # We look for the "Popular times" aria-label or text.
        
        # Often the live busyness is in a div with "Live" text and a percentage height or width
        # Searching for text "Live" or "Busy" might be too broad, but let's try to find the specific container
        
        # Checking for "Live" label usually associated with the pink bar
        live_labels = soup.find_all(string=lambda text: text and "Live" in text)
        for label in live_labels:
            # Usually the parent or grandparent contains the percentage info in aria-label or style
            parent = label.find_parent()
            if parent:
                # Try to find something that looks like "50% busy"
                # Sometimes it is in the 'aria-label' of a sibling or parent
                container = parent.find_parent()
                if container:
                    text_content = container.get_text()
                    if "%" in text_content:
                        # Extract number
                        import re
                        match = re.search(r'(\d+)%', text_content)
                        if match:
                            return int(match.group(1))

        # Strategy 2: Look for the specific class that often holds this data (obfuscated, but sometimes stable-ish)
        # Not reliable to hardcode classes like 'Ob2kfd'.
        
        # Strategy 3: Just return a random value for TESTING if enabled, otherwise return None to show real failure
        if IS_TEST_MODE:
            print(f"Test mode: simulating data for {query}")
            return random.randint(20, 90)

        return None
        
    except Exception as e:
        print(f"Exception scraping {query}: {e}")
        return None

def send_telegram_message(message):
    if IS_TEST_MODE:
        print(f"TELEGRAM TEST: {message}")
        return True
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        return False

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Security Check
        from urllib.parse import urlparse, parse_qs
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        key = query_params.get('key', [None])[0]
        
        if not IS_TEST_MODE and key != CRON_SECRET:
            self.send_response(401)
            self.end_headers()
            self.wfile.write("Unauthorized".encode('utf-8'))
            return

        # Core Logic
        busyness_values = []
        
        for place in LOCATIONS:
            val = scrape_google_busyness(place['query'])
            if val is not None:
                busyness_values.append(val)
            else:
                print(f"No data for {place['name']}")
            # Be nice to Google
            time.sleep(1) 

        message = ""
        index_val = 0
        
        if not busyness_values:
            message = "Pentagon pizza index: No Data :("
        else:
            index_val = int(sum(busyness_values) / len(busyness_values))
            
            status_visual = "🟢"
            status_text = "Index is normal"
            
            if index_val > 50:
                status_visual = "🟡"
                status_text = "Elevated activity"
            if index_val > 75:
                status_visual = "🔴"
                status_text = "The index exceeds the norm"
                
            message = f"Pentagon pizza index now: {index_val} — {status_visual} {status_text}"

        send_telegram_message(message)

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(f"Scraped. Result: {message}".encode('utf-8'))

# For local testing
if __name__ == "__main__":
    # Mock request object not needed, just run the logic
    print("Running local test...")
    # Manually invoke logic (this is just for quick python api/index.py run)
    # But the handler structure is for Vercel. 
    # To test locally, we can reuse the functions.
    
    vals = []
    for place in LOCATIONS:
        v = scrape_google_busyness(place['query'])
        if v: vals.append(v)
    
    print(f"Values: {vals}")
