import asyncio
from telethon import TelegramClient

api_id = 34165554
api_hash = "6879f17a50febfb32f9264b7300a8066"

SOURCE_CHANNEL = "loot_deals"
TARGET_CHANNEL = "loot_deals_india_vj"

client = TelegramClient("user_session", api_id, api_hash)

async def main():
    print("✅ User bot started...")

    await client.start()  # uses saved session

    print("🔥 Logged in successfully")

    while True:
        print("🔍 Checking source channel...")

        async for message in client.iter_messages(SOURCE_CHANNEL, limit=5):
            if message.text:
                await client.send_message(TARGET_CHANNEL, message.text)
                print("📤 Posted")

        print("⏳ Sleeping...")
        await asyncio.sleep(60)

asyncio.run(main())