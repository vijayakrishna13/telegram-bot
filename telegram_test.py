import asyncio
from telethon import TelegramClient

# 🔑 Your credentials (already filled)
api_id = 34165554
api_hash = "6879f17a50febfb32f9264b7300a8066"
BOT_TOKEN = "AAE0xs3TcGr-Zz8eDYrAhOsnxqfn455jJM0"  # ← put your NEW token

# 📢 Channels
SOURCE_CHANNEL = "loot_deals"
TARGET_CHANNEL = "loot_deals_india_vj"

# 🚀 Create client
client = TelegramClient("bot_session", api_id, api_hash)

async def main():
    print("✅ Bot started...")

    await client.start(bot_token=BOT_TOKEN)

    while True:
        try:
            print("🔍 Checking source channel...")

            async for message in client.iter_messages(SOURCE_CHANNEL, limit=5):
                if message.text:
                    text = message.text

                    # Basic filter (only deals)
                    if "₹" in text or "Rs" in text:
                        print("📤 Posting message...")

                        await client.send_message(TARGET_CHANNEL, text)

                        print("✅ Posted successfully")

            print("😴 Sleeping...\n")
            await asyncio.sleep(60)

        except Exception as e:
            print("❌ Error:", e)
            await asyncio.sleep(10)

# ▶️ Run
with client:
    client.loop.run_until_complete(main())