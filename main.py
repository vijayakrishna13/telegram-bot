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

# ===== STORAGE =====
FILE_NAME = "sent.txt"
sent_products = set()

if os.path.exists(FILE_NAME):
    with open(FILE_NAME, "r") as f:
        for line in f:
            sent_products.add(line.strip())

# ===== FLASK =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

# ===== DISCOUNT CALC =====
def calculate_discount(text):
    prices = re.findall(r'₹\s?(\d+)', text)

    if len(prices) >= 2:
        try:
            mrp = int(prices[1])
            deal = int(prices[0])

            if mrp > deal:
                discount = int(((mrp - deal) / mrp) * 100)
                return discount, deal, mrp
        except:
            return None

    return None

# ===== FILTER =====
def is_good_deal(text):
    text = text.lower()

    if "amazon" not in text:
        return False

    if "₹" not in text:
        return False

    bad_words = ["earn", "crypto", "bet", "loan", "adult"]
    if any(word in text for word in bad_words):
        return False

    discount_data = calculate_discount(text)

    if discount_data:
        discount, deal, mrp = discount_data
        if discount < 30:
            return False

    return True

# ===== COPYWRITING =====
def format_message(text, link):
    discount_data = calculate_discount(text)

    if discount_data:
        discount, deal, mrp = discount_data

        msg = f"""🔥 MEGA DEAL

💰 Price: ₹{deal} (MRP ₹{mrp})
📉 Discount: {discount}% OFF

⚡ Limited Time Offer

👉 Buy Now:
{link}
"""
    else:
        msg = f"""🔥 HOT DEAL

👉 Buy Now:
{link}
"""
    return msg

# ===== AMAZON =====
def get_amazon_deals():
    print("Fetching Amazon deals...")

    headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://www.amazon.in/deals"
    deals = []

    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        links = soup.find_all("a", href=True)

        for a in links:
            href = a["href"]

            if "/dp/" not in href:
                continue

            link = "https://www.amazon.in" + href.split("?")[0]
            product_id = link.split("/dp/")[1].split("/")[0]

            if product_id in sent_products:
                continue

            sent_products.add(product_id)
            with open(FILE_NAME, "a") as f:
                f.write(product_id + "\n")

            formatted = format_message("amazon deal ₹1000 ₹2000", link)
            deals.append(formatted)

            if len(deals) >= 3:
                break

    except Exception as e:
        print("Amazon error:", e)

    return deals

# ===== TELEGRAM =====
async def get_telegram_deals():
    print("Fetching Telegram deals...")

    source_channels = ["offerzone3_0"]  # ensure you joined this
    deals = []

    for channel in source_channels:
        try:
            async for message in client.iter_messages(channel, limit=30):

                if not message.text:
                    continue

                if not is_good_deal(message.text):
                    continue

                links = re.findall(r'https?://\S+', message.text)
                if not links:
                    continue

                link = links[0]

                if "/dp/" not in link:
                    continue

                product_id = link.split("/dp/")[1].split("/")[0]

                if product_id in sent_products:
                    continue

                sent_products.add(product_id)
                with open(FILE_NAME, "a") as f:
                    f.write(product_id + "\n")

                formatted = format_message(message.text, link)
                deals.append(formatted)

                if len(deals) >= 5:
                    break

        except Exception as e:
            print("Telegram error:", e)

    return deals

# ===== LOOP =====
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