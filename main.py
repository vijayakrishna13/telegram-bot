import os
import asyncio
import requests
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

# ===== SIMPLE DEAL FETCH (STABLE) =====
def get_deals():
    print("🚀 Fetching deals...")

    deals = []

    # 👉 simple static list (guaranteed working test)
    products = [
        ("Boat Airdopes 141", "https://www.amazon.in/dp/B09MTRDQBZ", 1299, 2999),
        ("Noise Smartwatch", "https://www.amazon.in/dp/B0B4S7F92B", 1999, 4999),
        ("Fire-Boltt Earbuds", "https://www.amazon.in/dp/B0B3RRWSF6", 899, 2999),
    ]

    for title, link, price, mrp in products:
        discount = int(((mrp - price) / mrp) * 100)

        msg = f"""🔥 BEST DEAL

📦 {title}

💰 ₹{price} (Worth ₹{mrp})
🔥 {discount}% OFF

👉 Final price may drop further
⚡ Limited time deal

👉 {link}
"""

        deals.append(msg)

    print("Deals found:", len(deals))
    return deals

# ===== BOT LOOP =====
async def bot_loop():
    print("🚀 BOT STARTED")

    await client.start()

    while True:
        print("🔥 LOOP STARTED")

        deals = get_deals()

        for deal in deals:
            try:
                await client.send_message(CHANNEL, deal)
                print("✅ Sent")
                await asyncio.sleep(5)
            except Exception as e:
                print("Send error:", e)

        print("⏳ Sleeping...\n")
        await asyncio.sleep(1800)

# ===== THREAD =====
def run_bot():
    print("THREAD STARTED")
    asyncio.run(bot_loop())

# ===== START =====
if __name__ == "__main__":
    print("🔥 Starting system...")

    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)