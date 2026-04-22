import asyncio
import threading
from flask import Flask
from telethon import TelegramClient

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

# ===== YOUR LOGIC =====
def get_deals():
    # temporary (replace later with Amazon scraping)
    return ["🔥 FINAL TEST DEAL"]

# ===== TELEGRAM BOT =====
async def run_bot():
    await client.start()
    print("🔥 Logged in successfully")

    posted = set()

    while True:
        print("🔍 Running your logic...")

        deals = get_deals()

        for deal in deals:
            if deal not in posted:
                await client.send_message(TARGET_CHANNEL, deal)
                posted.add(deal)
                print("📤 Posted:", deal)

        await asyncio.sleep(60)

# ===== MAIN =====
def main():
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(run_bot())

if __name__ == "__main__":
    main()