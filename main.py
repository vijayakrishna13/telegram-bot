import asyncio
from flask import Flask
from telethon import TelegramClient

# ===== CONFIG =====
api_id = 34165554
api_hash = "6879f17a50febfb32f9264b7300a8066"

SOURCE_CHANNEL = "loot_deals"
TARGET_CHANNEL = "loot_deals_india_vj"

client = TelegramClient("user_session", api_id, api_hash)

# ===== FLASK =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

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
async def main():
    asyncio.create_task(telegram_bot())
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    asyncio.run(main())