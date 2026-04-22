from telethon import TelegramClient
import re
import asyncio
from flask import Flask
import threading

# ================== KEEP ALIVE ==================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot running"

def run_web():
    app.run(host="0.0.0.0", port=10000)

# ================== CONFIG ==================
api_id = 34165554
api_hash = '6879f17a50febfb32f9264b7300a8066'
bot_token = 'AAE0xs3TcGr-Zz8eDYrAhOsnxqfn455jJM0'

SOURCE_CHANNEL = 'loot_deals'
TARGET_CHANNEL = 'loot_deals_india_vj'

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# ================== HELPERS ==================
def convert_to_affiliate(link):
    if "amazon.in" in link:
        if "tag=" in link:
            return link
        return link + "?tag=lootdealsvj21-21"
    return link

def extract_data(text):
    link_match = re.search(r'https?://\S+', text)
    link = link_match.group() if link_match else ""

    price_match = re.search(r'₹\s?\d+[,\d]*', text)
    price = price_match.group() if price_match else ""

    product = text.split('\n')[0]
    return product, price, link

# ================== MAIN ==================
async def main():
    print("✅ Bot started")

    entity = await client.get_entity(TARGET_CHANNEL)

    while True:
        print("🔍 Checking source channel...")

        async for message in client.iter_messages(SOURCE_CHANNEL, limit=50):
            try:
                if not message.text:
                    continue

                product, price, link = extract_data(message.text)

                if not link or "amazon.in" not in link:
                    continue

                link = convert_to_affiliate(link)

                msg = f"🔥 {product}\n💰 {price}\n👉 {link}"

                await client.send_message(entity, msg)
                print("📤 Posted:", product)

                await asyncio.sleep(2)

            except Exception as e:
                print("Error:", e)

        print("⏳ Sleeping 2 minutes...\n")
        await asyncio.sleep(120)

# ================== RUN ==================
threading.Thread(target=run_web).start()

with client:
    client.loop.run_until_complete(main())