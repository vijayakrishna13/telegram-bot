import asyncio
import threading
from flask import Flask
from telethon import TelegramClient
import requests
from bs4 import BeautifulSoup

# ===== TELEGRAM CONFIG =====
api_id = 34165554
api_hash = "6879f17a50febfb32f9264b7300a8066"

TARGET_CHANNEL = "https://t.me/loot_deals_india_vj"

client = TelegramClient("user_session", api_id, api_hash)

# ===== FLASK (for Render free plan) =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# ===== BESTSELLER SCRAPER =====
def get_deals():
    headers = {"User-Agent": "Mozilla/5.0"}

    categories = [
        "https://www.amazon.in/gp/bestsellers/electronics/",
        "https://www.amazon.in/gp/bestsellers/kitchen/",
        "https://www.amazon.in/gp/bestsellers/fashion/",
    ]

    deals = []

    for url in categories:
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")

            items = soup.select("._cDEzb_p13n-sc-css-line-clamp-3_g3dy1")

            for item in items[:5]:  # top 5 per category
                title = item.get_text(strip=True)

                parent = item.find_parent("a")
                link = "https://www.amazon.in" + parent["href"] if parent else ""

                message = f"🔥 Bestseller\n📦 {title}\n👉 {link}"

                deals.append(message)

        except:
            continue

    return deals

# ===== TELEGRAM BOT =====
async def run_bot():
    await client.start()
    print("🔥 Logged in successfully")

    posted = set()

    while True:
        print("🔍 Fetching bestseller products...")

        deals = get_deals()

        for deal in deals:
            if deal not in posted:
                await client.send_message(TARGET_CHANNEL, deal)
                posted.add(deal)
                print("📤 Posted:", deal)

        await asyncio.sleep(120)  # every 2 minutes

# ===== MAIN =====
def main():
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(run_bot())

if __name__ == "__main__":
    main()