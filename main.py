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

# ===== PRICE LOGIC =====
def extract_price_data(text):
    prices = re.findall(r'₹\s?(\d+)', text)

    if len(prices) >= 2:
        try:
            deal = int(prices[0])
            mrp = int(prices[1])

            if mrp > deal:
                discount = int(((mrp - deal) / mrp) * 100)
                return deal, mrp, discount
        except:
            return None

    return None

# ===== PRICE VALIDATION =====
def is_real_discount(deal, mrp, discount):
    if discount < 40:
        return False

    # fake MRP detection
    if mrp > deal * 3:  # unrealistic inflated price
        return False

    return True

# ===== BESTSELLER =====
def is_bestseller(link):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(link, headers=headers, timeout=10)
        html = res.text.lower()

        keywords = ["best seller", "#1", "bestseller"]
        return any(k in html for k in keywords)

    except:
        return False

# ===== COPYWRITING =====
def format_message(deal, mrp, discount, link):
    return f"""🔥 MEGA DEAL

💰 Deal Price: ₹{deal}
🏷 MRP: ₹{mrp}
📉 OFF: {discount}%

⭐ Bestseller Product
⚡ Real Price Drop

👉 Buy Now:
{link}
"""

# ===== AMAZON SCRAPER =====
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

            # FAKE TEXT (we improve later)
            text = "₹1000 ₹2000"

            price_data = extract_price_data(text)
            if not price_data:
                continue

            deal, mrp, discount = price_data

            if not is_real_discount(deal, mrp, discount):
                continue

            if not is_bestseller(link):
                continue

            sent_products.add(product_id)
            with open(FILE_NAME, "a") as f:
                f.write(product_id + "\n")

            deals.append(format_message(deal, mrp, discount, link))

            if len(deals) >= 3:
                break

    except Exception as e:
        print("Amazon error:", e)

    return deals

# ===== TELEGRAM SCRAPER =====
async def get_telegram_deals():
    print("Fetching Telegram deals...")

    source_channels = ["offerzone3_0"]
    deals = []

    for channel in source_channels:
        try:
            async for message in client.iter_messages(channel, limit=30):

                if not message.text:
                    continue

                if "₹" not in message.text:
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

                price_data = extract_price_data(message.text)
                if not price_data:
                    continue

                deal, mrp, discount = price_data

                if not is_real_discount(deal, mrp, discount):
                    continue

                if not is_bestseller(link):
                    continue

                sent_products.add(product_id)
                with open(FILE_NAME, "a") as f:
                    f.write(product_id + "\n")

                deals.append(format_message(deal, mrp, discount, link))

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

        amazon = get_amazon_deals()
        telegram = await get_telegram_deals()

        all_deals = amazon + telegram

        if not all_deals:
            print("No good deals found")

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

    threading.Thread(target=run_bot).start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)