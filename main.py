import asyncio
from telethon import TelegramClient

# 🔑 Your credentials
api_id = 34165554
api_hash = "6879f17a50febfb32f9264b7300a8066"
BOT_TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"

# 📢 Channels
SOURCE_CHANNEL = "loot_deals"
TARGET_CHANNEL = "loot_deals_india_vj"

# ✅ Create client (session file)
client = TelegramClient("bot_session", api_id, api_hash)


async def main():
    print("✅ Bot started...")

    # ✅ IMPORTANT: Only bot login (no phone login)
    await client.start(bot_token=BOT_TOKEN)

    print("🔥 Logged in successfully")

    while True:
        print("🔍 Checking source channel...")

        async for message in client.iter_messages(SOURCE_CHANNEL, limit=5):
            if message.text:
                await client.send_message(TARGET_CHANNEL, message.text)
                print("📤 Posted")

        print("⏳ Sleeping...")
        await asyncio.sleep(60)


# 🚀 Run the bot
asyncio.run(main())