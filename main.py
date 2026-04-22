import os
import asyncio
import requests
from bs4 import BeautifulSoup
from telethon import TelegramClient
from telethon.sessions import StringSession
from flask import Flask
import threading

# ===== ENV =====
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")
CHANNEL = os.getenv("CHANNEL")

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

# ===== FLASK =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

# ===== SCRAPER =====
def get_deals():
    print("🚀 Fetching deals...")

    headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://www.amazon.in/gp/bestsellers/electronics/"
    deals = []

    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        items = soup.select("._cDEzb_p13n-sc-css-line-clamp-3_g3dy1")

        for item in items[:5]:
            title = item.get_text(strip=True)
            parent = item.find_parent("a")
            link = "https://www.amazon.in" + parent["href"] if parent else ""

            deals.append(f"🔥 {title}\n👉 {link}")

    except Exception as e:
        print("Error:", e)

    print("Deals:", len(deals))
    return deals

# ===== TELEGRAM =====
async def send_deals():
    deals = get_deals()

    for deal in deals:
        await client.send_message(CHANNEL, deal)
        print("Sent")
        await asyncio.sleep(5)

# ===== BOT LOOP =====
async def bot_loop():
    print("🚀 Starting bot...")

    await client.start()

    while True:
        print("🔁 Cycle running...")
        await send_deals()
        print("⏳ Sleeping...\n")
        await asyncio.sleep(1800)

# ===== RUN BOT IN THREAD =====
def start_bot():
    asyncio.run(bot_loop())

# ===== START =====
if __name__ == "__main__":
    threading.Thread(target=start_bot).start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)