import asyncio
import threading
from flask import Flask
from telethon import TelegramClient

# ===== TELEGRAM CONFIG =====
api_id = 34165554
api_hash = "6879f17a50febfb32f9264b7300a8066"

SOURCE_CHANNEL = "loot_deals"
TARGET_CHANNEL = "loot_deals_india_vj"

client = TelegramClient("user_session", api_id, api_hash)

# ===== FLASK (for Render) =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# ===== TELEGRAM BOT =====
async def telegram_bot():
    await client.start()
    print("🔥 Logged in successfully")

    while True:
        print("🔍 Checking source channel...")

        async for message in client.iter_messages(SOURCE_CHANNEL, limit=5):
            if message.text:
                await client.send_message(TARGET_CHANNEL, message.text)
                print("📤 Posted")

        await asyncio.sleep(60)

# ===== RUN BOTH =====
def main():
    threading.Thread(target=run_flask).start()
    asyncio.run(telegram_bot())

if __name__ == "__main__":
    main()