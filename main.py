import os
import asyncio
import requests
from bs4 import BeautifulSoup
from telethon import TelegramClient
from telethon.sessions import StringSession
from flask import Flask
import threading
import re

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

# ===== MEMORY =====
sent_products = set()

# ===== AMAZON SCRAPER =====
def get_amazon_deals():
    print("Fetching Amazon deals...")

    headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://www.amazon.in/gp/bestsellers/electronics/"
    deals = []

    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        items = soup.select("._cDEzb_p13n-sc-css-line-clamp-3_g3dy1")

        for item in items[:10]:
            title = item.get_text(strip=True)
            parent = item.find_parent("a")
            link = "https://www.amazon.in" + parent["href"] if parent else ""

            # extract product id
            product_id = link.split("/dp/")[1].split("/")[0] if "/dp/" in link else link

            if product_id in sent_products:
                continue

            deals.append(f"Amazon Deal:\n{title}\n{link}")
            sent_products.add(product_id)

            if len(deals) >= 3:
                break

    except Exception as e:
        print("Amazon error:", e)

    return deals

# ===== TELEGRAM SCRAPER =====
async def get_telegram_deals():
    print("Fetching Telegram deals...")

    source_channels = [
        "loot_deals_india",
        "amazon_deals_india"
    ]

    deals = []

    for channel in source_channels:
        try:
            async for message in client.iter_messages(channel, limit=20):

                if not message.text:
                    continue

                text = message.text.lower()

                if "amazon" not in text:
                    continue

                links = re.findall(r'https?://\S+', message.text)
                if not links:
                    continue

                link = links[0]

                # extract product id
                if "/dp/" in link:
                    product_id = link.split("/dp/")[1].split("/")[0]
                else:
                    product_id = link

                if product_id in sent_products:
                    continue

                sent_products.add(product_id)

                clean_msg = message.text[:400]

                deals.append(clean_msg)

                if len(deals) >= 3:
                    break

        except Exception as e:
            print("Telegram error:", e)

    return deals

# ===== BOT LOOP =====
async def bot_loop():
    print("BOT STARTED")

    await client.start()

    while True:
        print("Running cycle...")

        amazon_deals = get_amazon_deals()
        telegram_deals = await get_telegram_deals()

        all_deals = amazon_deals + telegram_deals

        if not all_deals:
            print("No deals found")

        for deal in all_deals:
            try:
                await client.send_message(CHANNEL, deal)
                print("Sent")
                await asyncio.sleep(5)
            except Exception as e:
                print("Send error:", e)

        print("Sleeping...\n")
        await asyncio.sleep(1800)

# ===== THREAD =====
def run_bot():
    asyncio.run(bot_loop())

# ===== MAIN =====
if __name__ == "__main__":
    print("Starting system...")

    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)