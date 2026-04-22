import os
import asyncio
import requests
from bs4 import BeautifulSoup
from telethon import TelegramClient
from telethon.sessions import StringSession
from flask import Flask
import threading
import re
import datetime

# ===== ENV =====
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")
CHANNEL = os.getenv("CHANNEL")

AFFILIATE_TAG = "lootdealsvj21-21"

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

# ===== FILES =====
SENT_FILE = "sent.txt"
LOG_FILE = "analytics.txt"

sent_products = set()

if os.path.exists(SENT_FILE):
    with open(SENT_FILE, "r") as f:
        for line in f:
            sent_products.add(line.strip())

# ===== FLASK =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot running"

# ===== ANALYTICS =====
def log_deal(product_id, category):
    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    with open(LOG_FILE, "a") as f:
        f.write(f"{time_now} | {category} | {product_id}\n")

# ===== PRICE =====
def extract_price_data(text):
    prices = re.findall(r'₹\s?(\d+)', text)

    if len(prices) >= 2:
        deal = int(prices[0])
        mrp = int(prices[1])

        if mrp > deal:
            discount = int(((mrp - deal) / mrp) * 100)
            return deal, mrp, discount

    return None

def is_real_discount(deal, mrp, discount):
    return discount >= 40 and mrp < deal * 3

# ===== AFFILIATE =====
def make_affiliate(link):
    if "tag=" in link:
        return link
    if "?" in link:
        return link + f"&tag={AFFILIATE_TAG}"
    return link + f"?tag={AFFILIATE_TAG}"

# ===== BESTSELLER =====
def is_bestseller(link):
    try:
        html = requests.get(link, headers={"User-Agent": "Mozilla"}, timeout=10).text.lower()
        return any(k in html for k in ["best seller", "#1", "bestseller"])
    except:
        return False

# ===== COPYWRITING =====
def format_message(deal, mrp, discount, link, category):
    link = make_affiliate(link)

    return f"""🔥 {discount}% OFF – {category.upper()} DEAL

💰 ₹{deal} (MRP ₹{mrp})
📉 Save ₹{mrp - deal}

⭐ Bestseller Product
⚡ Limited Time Deal

👉 Buy Now:
{link}
"""

# ===== AMAZON =====
CATEGORIES = {
    "electronics": "https://www.amazon.in/gp/bestsellers/electronics/",
    "mobiles": "https://www.amazon.in/gp/bestsellers/wireless/",
    "home": "https://www.amazon.in/gp/bestsellers/kitchen/",
}

def scrape_category(url, category):
    deals = []

    try:
        soup = BeautifulSoup(
            requests.get(url, headers={"User-Agent": "Mozilla"}, timeout=10).text,
            "html.parser"
        )

        for a in soup.find_all("a", href=True):
            href = a["href"]

            if "/dp/" not in href:
                continue

            link = "https://www.amazon.in" + href.split("?")[0]
            product_id = link.split("/dp/")[1].split("/")[0]

            if product_id in sent_products:
                continue

            # TEMP price (later improve)
            text = "₹1000 ₹2000"

            data = extract_price_data(text)
            if not data:
                continue

            deal, mrp, discount = data

            if not is_real_discount(deal, mrp, discount):
                continue

            if not is_bestseller(link):
                continue

            sent_products.add(product_id)
            with open(SENT_FILE, "a") as f:
                f.write(product_id + "\n")

            # 🔥 ANALYTICS HERE
            log_deal(product_id, category)

            deals.append(format_message(deal, mrp, discount, link, category))

            if len(deals) >= 2:
                break

    except Exception as e:
        print("Amazon error:", e)

    return deals

# ===== TELEGRAM =====
async def get_telegram_deals():
    deals = []

    try:
        async for msg in client.iter_messages("offerzone3_0", limit=20):

            if not msg.text:
                continue

            links = re.findall(r'https?://\S+', msg.text)
            if not links:
                continue

            link = links[0]

            if "/dp/" not in link:
                continue

            product_id = link.split("/dp/")[1].split("/")[0]

            if product_id in sent_products:
                continue

            data = extract_price_data(msg.text)
            if not data:
                continue

            deal, mrp, discount = data

            if not is_real_discount(deal, mrp, discount):
                continue

            if not is_bestseller(link):
                continue

            sent_products.add(product_id)
            with open(SENT_FILE, "a") as f:
                f.write(product_id + "\n")

            # 🔥 ANALYTICS HERE
            log_deal(product_id, "telegram")

            deals.append(format_message(deal, mrp, discount, link, "TRENDING"))

            if len(deals) >= 3:
                break

    except Exception as e:
        print("Telegram error:", e)

    return deals

# ===== LOOP =====
async def bot_loop():
    print("BOT STARTED")

    await client.start() 
    log_deal("TEST123", "test")

    while True:
        print("Running cycle...")

        all_deals = []

        for name, url in CATEGORIES.items():
            all_deals.extend(scrape_category(url, name))

        all_deals.extend(await get_telegram_deals())

        for deal in all_deals:
            try:
                await client.send_message(CHANNEL, deal)
                print("Sent")
                await asyncio.sleep(5)
            except Exception as e:
                print("Send error:", e)

        print("Sleeping...\n")
        await asyncio.sleep(1800)

# ===== MAIN =====
def run_bot():
    asyncio.run(bot_loop())

if __name__ == "__main__":
    print("Starting system...")

    threading.Thread(target=run_bot).start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)