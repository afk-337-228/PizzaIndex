# Pentagon Pizza Index Bot 🍕

This Telegram bot monitors the "Live Busyness" of pizza places near **The Pentagon** to potentially detect high-priority military activity.

## Architecture

*   **Logic**: Python script hosted on **Vercel** (Serverless Function).
*   **Scheduling**: **GitHub Actions** triggers the script every 2 hours (bypassing Vercel Free Tier limits).
*   **Scraping**: `requests` + `BeautifulSoup` parsing Google Search results.

## Prerequisites

1.  **Telegram Bot**:
    *   Create a bot via [@BotFather](https://t.me/BotFather) and get the `TELEGRAM_BOT_TOKEN`.
    *   Get your `TELEGRAM_CHAT_ID` (you can use [@userinfobot](https://t.me/userinfobot)).
2.  **Vercel Account**: For hosting the Python code.
3.  **GitHub Account**: For hosting the repo and the scheduler.

## Deployment Guide

### 1. Deploy to Vercel

1.  Install Vercel CLI (optional) or just push this code to a GitHub repository.
2.  Import the project into Vercel.
3.  **Environment Variables**: Go to Project Settings -> Environment Variables and add:
    *   `TELEGRAM_BOT_TOKEN`: Your bot token.
    *   `TELEGRAM_CHAT_ID`: Your target chat ID.
    *   `CRON_SECRET`: A random string (e.g., `pizza-secret-123`). This protects your endpoint.

### 2. Configure GitHub Actions (The Scheduler)

To run this every 2 hours, we use GitHub Actions.

1.  Go to your GitHub Repository -> **Settings** -> **Secrets and variables** -> **Actions**.
2.  Add the following **Repository secrets**:
    *   `VERCEL_URL`: The URL of your Vercel deployment (e.g., `https://my-pizza-bot.vercel.app`). **Do not include trailing slash.**
    *   `CRON_SECRET`: The same secret string you set in Vercel.

### 3. Testing

*   **Local Test**: Set `IS_TEST_MODE=True` environment variable and run:
    ```bash
    python api/index.py
    ```
    This will print scraped data (or simulated data) to the console.
*   **Manual Trigger**: You can manually trigger the GitHub Action in the "Actions" tab to test the connection.

## Troubleshooting

*   **"No Data"**: Google aggressively blocks bots. The script tries to look for specific "Live" indicators in the HTML, but this often fails without a real browser. The script will simply report "No Data" or the calculated average of whatever it could find.
*   **Vercel Timeout**: The free tier has a 10s timeout. If scraping takes too long, it might fail.
