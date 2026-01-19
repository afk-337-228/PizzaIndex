from http.server import BaseHTTPRequestHandler
import os
import json
import requests
import time

# Configuration
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
CRON_SECRET = os.environ.get("CRON_SECRET")
IS_TEST_MODE = os.environ.get("IS_TEST_MODE", "False").lower() == "true"

PIZZINT_API_URL = "https://www.pizzint.watch/api/dashboard-data?nocache=1"

def fetch_pizzint_data():
    """
    Fetches Pentagon Pizza Index data from pizzint.watch API.
    Returns: dict with 'index' and 'doughcon' or None.
    """
    try:
        response = requests.get(PIZZINT_API_URL, timeout=10)
        if response.status_code != 200:
            print(f"Error fetching data from Pizzint: Status {response.status_code}")
            return None
        
        data = response.json()
        overall_index = data.get("overall_index", 0)
        defcon_level = data.get("defcon_level", 4) # Default to 4 if missing
        
        return {
            "index": overall_index,
            "doughcon": defcon_level
        }
    except Exception as e:
        print(f"Exception fetching data: {e}")
        return None

def send_telegram_message(message):
    if IS_TEST_MODE:
        print(f"TELEGRAM TEST: {message}")
        return True
        
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials missing!")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
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
        stats = fetch_pizzint_data()
        
        if not stats:
            message = "🍕 *Pentagon Pizza Index*: No Data :("
        else:
            idx = stats['index']
            defcon = stats['doughcon']
            
            # Official Pizzint level mapping
            mapping = {
                1: {"emoji": "🔴", "text": "Maximum Readiness"},
                2: {"emoji": "🟠", "text": "Next Step to Maximum Readiness"},
                3: {"emoji": "🟡", "text": "Increase in Force Readiness"},
                4: {"emoji": "🔵", "text": "Increased Intelligence Watch"},
                5: {"emoji": "🟢", "text": "Lowest State of Readiness"}
            }
            
            status = mapping.get(defcon, {"emoji": "⚪", "text": "Unknown Status"})
            
            message = f"🍕 *Pentagon Pizza Index*: {idx}\n"
            message += f"📊 *Status*: level {defcon} — {status['emoji']} {status['text']}"

        send_telegram_message(message)

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(f"Processed. Result: {message}".encode('utf-8'))

# For local testing
if __name__ == "__main__":
    print("Running local test for Pizzint API...")
    res = fetch_pizzint_data()
    if res:
        print(f"Index: {res['index']}, DOUGHCON: {res['doughcon']}")
        msg = f"🍕 *Pentagon Pizza Index*: {res['index']}\n📊 *Status*: level {res['doughcon']}"
        send_telegram_message(msg)
    else:
        print("Failed to fetch data.")
