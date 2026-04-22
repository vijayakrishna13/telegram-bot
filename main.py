import asyncio
import threading
from flask import Flask
from telethon import TelegramClient

# ===== TELEGRAM CONFIG =====
api_id = 34165554
api_hash = "6879f17a50febfb32f9264b7300a8066"

TARGET_CHANNEL = "https://t.me/loot_deals_india_vj"

client = TelegramClient("user_session", api_id, api_hash)

# ===== FLASK =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# ===== YOUR AMAZON LOGIC (KEEP EMPTY FOR NOW) =====
def get_deals():
    return ["Test deal message"]  # temporary test

# ===== TELEGRAM BOT =====
async def run_bot():
    await client.start()
    print("🔥 Logged in successfully")

    while True:
        print("🔍 Running your logic...")

        deals = get_deals()

        for deal in deals:
            await client.send_message(TARGET_CHANNEL, deal)
            print("📤 Posted:", deal)

        await asyncio.sleep(60)

# ===== MAIN =====
def main():
    # Start Flask in background
    threading.Thread(target=run_flask).start()

    # Start Telegram bot (MAIN thread)
    asyncio.run(run_bot())

if __name__ == "__main__":
    main()