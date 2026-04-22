import asyncio
from telethon import TelegramClient

api_id = 34165554
api_hash = "6879f17a50febfb32f9264b7300a8066"
BOT_TOKEN = "YOUR_NEW_TOKEN"

SOURCE_CHANNEL = "loot_deals"
TARGET_CHANNEL = "loot_deals_india_vj"

client = TelegramClient(None, api_id, api_hash)

async def main():
    print("✅ Bot started...")

    await client.start(bot_token=BOT_TOKEN)

    while True:
        print("🔍 Checking source channel...")

        async for message in client.iter_messages(SOURCE_CHANNEL, limit=5):
            if message.text:
                await client.send_message(TARGET_CHANNEL, message.text)
                print("📤 Posted")

        await asyncio.sleep(60)

async def run():
    async with client:
        await main()

asyncio.run(run())