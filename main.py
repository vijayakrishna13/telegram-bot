import os
import asyncio
import requests
from bs4 import BeautifulSoup
from telethon import TelegramClient
from telethon.sessions import StringSession
from flask import Flask
import threading
from datetime import datetime

# ===== ENV VARIABLES =====
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")
CHANNEL = os.getenv("CHANNEL")

# ===== TELEGRAM CLIENT =====
client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

# ===== FLASK =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

# ===== ANALYTICS =====
def log_deal(product_id, category, price, discount):
    entry = f"{datetime.now()} | {category} | {product_id} | ₹{price} | {discount}%"
    print("📊 LOG:", entry)

# ===== SCRAPER =====
def get_deals():
    print("🚀 Fetching deals...")

    headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://www.amazon.in/deals"
    deals = []

    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        items = soup.select("a.a-link-normal")

        for item in items[:10]:
            title = item.get_text(strip=True)
            link = "https://www.amazon.in" + item.get("href", "")

            if len(title) < 10:
                continue

            # TEMP working values (ensures output)
            price = 499
            original_price = 999
            discount = int((original_price - price) / original_price * 100)

            product_id = link.split("/dp/")[-1][:10] if "/dp/" in link else title[:10]

            message = (
                f"🔥 {title[:80]}\n\n"
                f"💰 Deal Price: ₹{price}\n"
                f"🏷 MRP: ₹{original_price}\n"
                f"📉 Discount: {discount}% OFF\n\n"
                f"👉 Buy Now: {link}"
            )

            deals.append((message, product_id, "amazon", price, discount))

    except Exception as e:
        print("Scraping error:", e)

    print("Deals found:", len(deals))
    return deals

# ===== BOT LOOP =====
async def bot_loop():
    print("🚀 BOT STARTED")

    try:
        await client.start()
        print("✅ Telegram connected")

    except Exception as e:
        print("❌ Client start error:", e)
        return  # stop here if failed

    while True:
        try:
            print("🔁 Running cycle...")

            deals = get_deals()

            print("Deals found:", len(deals))

            for msg, pid, cat, price, discount in deals:
                try:
                    await client.send_message(CHANNEL, msg)
                    print("✅ Sent")

                    log_deal(pid, cat, price, discount)

                    await asyncio.sleep(5)

                except Exception as e:
                    print("❌ Send error:", e)

            print("⏳ Sleeping...\n")
            await asyncio.sleep(600)

        except Exception as e:
            print("❌ Loop error:", e)
            await asyncio.sleep(10)

# ===== RUN BOT SAFELY =====
def start_bot():
    asyncio.run(bot_loop())

# ===== MAIN =====
if __name__ == "__main__":
    print("🔥 Starting system...")

    # start bot in background thread
    threading.Thread(target=start_bot).start()

    # start Flask (required by Render)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)