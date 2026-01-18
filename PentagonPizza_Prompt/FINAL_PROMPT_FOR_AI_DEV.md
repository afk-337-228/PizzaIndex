# Project: Pentagon Pizza Index Bot (Vercel Serverless Edition)

## **1. Project Overview**
We want to build a Telegram Bot that tracks the "Pentagon Pizza Index" — an automated OSINT tool that monitors the "Live Busyness" of pizza places near The Pentagon (Arlington, VA). The theory is that a spike in pizza orders at strange hours indicates a crisis or major military operation.

The bot will run on **Vercel** (Free Tier) using **Vercel Cron Jobs** to trigger a check **every 2 hours**.

## **2. Technical Stack**
*   **Language:** Python 3.9+ (or Node.js, but Python is preferred for scraping ecosystems).
*   **Hosting:** Vercel (Serverless Functions).
*   **Scheduling:** Vercel Cron (`vercel.json` configuration).
*   **Database:** None required (Stateless).
*   **Notification:** Telegram Bot API.
*   **Data Source:** Google Maps "Popular Times" / "Live Busyness" data.

## **3. Core Requirements**

### **A. The Scraper (Crucial)**
We need to scrape the "Live Busyness" percentage (0-100%) from Google Maps for specific locations.
*   **Constraint:** You cannot use an official API for "Live Busyness". You must scrape it.
*   **Constraint:** Vercel Free Tier has limits (execution time < 10s for some functions, 50MB size). **Avoid heavy Headless Browsers (Selenium/Puppeteer) if possible.**
*   **Architecture Suggestion:**
    *   Try to use a lightweight scraping library that mimics `requests` with proper User-Agent headers to fetch the HTML/JSON payload from Google Search/Maps.
    *   Look for the specific script tags or JSON blobs in the Google Maps response that contain "busyness" or "popular_times".
    *   If a browser is absolutely necessary, use a lightweight wrapper compatible with AWS Lambda/Vercel (like `playwright-aws-lambda` or `chrome-aws-lambda`), but be warned: this is hard to fit in the free tier. **Prefer direct HTTP requests.**

### **B. Target Locations (The "Pentagon Basket")**
Scrape the following locations (or their specific Google Maps Place IDs):
1.  **Domino's Pizza** (15th St S, Arlington, VA) - *High volume delivery hub.*
2.  **Papa John's Pizza** (23rd St S / Army Navy Dr area, Arlington, VA).
3.  **Wiseguy Pizza** (710 12th St S, Arlington, VA) - *Popular lunch/dinner spot.*

### **C. The Logic & Math**
1.  **Fetch Data:** Get `current_busyness` (0-100) for all 3 locations.
2.  **Handle Missing Data:** If a place is closed or data is missing, ignore it. If all are missing, send a "No Data" message.
3.  **Calculate Index:** `PentagonIndex = Average(busyness_of_active_places)`.
4.  **Determine Status:**
    *   **0 - 50:** 🟢 Index is normal
    *   **51 - 75:** 🟡 Elevated activity
    *   **76 - 100+:** 🔴 The index exceeds the norm

### **D. The Telegram Bot**
*   **Format:**
    ```text
    Pentagon pizza index now: [INDEX] — [ICON] [STATUS_TEXT]
    ```
    *Example:*
    > Pentagon pizza index now: 45 — 🟢 Index is normal
    > Pentagon pizza index now: 90 — 🔴 The index exceeds the norm
*   **Functionality:** The function should compile this message and send it to a predefined `CHANNEL_ID` or `CHAT_ID`.

## **4. Implementation Steps**

### **Step 1: Project Structure**
Create a standard Vercel Python project structure:
```
/api
  index.py        # Main entry point for the Vercel Function
  requirements.txt # Dependencies
vercel.json       # Cron config
README.md         # Instructions
```

### **Step 2: `vercel.json` Configuration**
Configure the Cron Job to run every 2 hours.
```json
{
  "crons": [
    {
      "path": "/api/index",
      "schedule": "0 */2 * * *"
    }
  ],
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ]
}
```

### **Step 3: The Code (`api/index.py`)**
Write the Python code to:
1.  **Authenticat**: Read `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` from environment variables.
2.  **Scrape**: Run the scraping logic for the 3 targets.
    *   *Tip:* Use random User-Agents to avoid 429 Errors.
    *   *Tip:* If scraping generic Google Search ("Domino's Pentagon busyness"), the "Popular Times" graph often appears in the search result HTML itself, which is easier to scrape than Maps.
3.  **Calculate & Send**: Format the string and POST to `https://api.telegram.org/bot<TOKEN>/sendMessage`.

## **5. Special Instructions for the AI Developer**
*   **Proxy Strategy:** The user wants to avoid paid proxies. Implement a robust `User-Agent` rotation. If the request fails, try 1-2 retries with different headers. If it takes too long, fail gracefully (Vercel timeout).
*   **Testing:** Provide a variable `IS_TEST_MODE=True` that allows running the script locally (printing to console instead of sending to Telegram).
*   **Deployment:** Include a brief "How to Deploy" section in the README (install Vercel CLI, `vercel login`, `vercel deploy`).

## **6. Deliverables**
1.  Complete source code.
2.  `requirements.txt`.
3.  `vercel.json`.
4.  A short README explaining how to get the Telegram Token, Chat ID, and deploy to Vercel.
