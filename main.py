import os
import asyncio
import requests
from bs4 import BeautifulSoup
from telethon import TelegramClient
from telethon.sessions import StringSession
from flask import Flask
import threading

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
sent_links = set()

# ===== SCRAPER =====
def get_deals():
    print("🚀 Fetching smart deals...")

    headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://www.amazon.in/gp/bestsellers/electronics/"
    deals = []

    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        items = soup.select("._cDEzb_p13n-sc-css-line-clamp-3_g3dy1")

        for item in items[:10]:
            title = item.get_text(strip=True)
            parent = item.find_parent("a")
            link = "https://www.amazon.in" + parent["href"] if parent else ""

            if link in sent_links:
                continue

            # open product page
            page = requests.get(link, headers=headers)
            psoup = BeautifulSoup(page.text, "html.parser")

            price_tag = psoup.select_one(".a-price-whole")
            mrp_tag = psoup.select_one(".a-text-price span")

            if not price_tag or not mrp_tag:
                continue

            try:
                price = int(price_tag.get_text().replace(",", ""))
                mrp = int(mrp_tag.get_text().replace("₹", "").replace(",", ""))
            except:
                continue

            if mrp == 0:
                continue

            discount = int(((mrp - price) / mrp) * 100)

            # ===== FILTER =====
            if discount < 30:
                continue

            # ===== COUPON =====
            coupon_text = ""
            coupon = psoup.find(string=lambda x: x and "coupon" in x.lower())
            if coupon:
                coupon_text = coupon.strip()

            # ===== BANK =====
            bank_text = ""
            bank = psoup.find(string=lambda x: x and "bank" in x.lower())
            if bank:
                bank_text = bank.strip()

            # ===== MESSAGE =====
            msg = f"""🔥 BEST DEAL

📦 {title[:60]}...

💰 ₹{price} (Worth ₹{mrp})
🔥 {discount}% OFF
"""

            if coupon_text:
                msg += f"\n🎟 {coupon_text}"

            if bank_text:
                msg += f"\n🏦 {bank_text}"

            msg += f"""

👉 Final price may drop further
⚡ Limited time deal

👉 {link}
"""

            deals.append(msg)
            sent_links.add(link)

            if len(deals) >= 5:
                break

    except Exception as e:
        print("Error:", e)

    print("Deals found:", len(deals))
    return deals

# ===== BOT LOOP =====
async def bot_loop():
    print("🚀 BOT STARTED")

    await client.start()

    while True:
        print("🔁 Running cycle...")

        deals = get_deals()

        if not deals:
            print("❌ No good deals found")

        for deal in deals:
            try:
                await client.send_message(CHANNEL, deal)
                print("✅ Sent")
                await asyncio.sleep(5)
            except Exception as e:
                print("Send error:", e)

        print("⏳ Sleeping...\n")
        await asyncio.sleep(1800)

# ===== THREAD =====
def run_bot():
    print("THREAD STARTED")
    asyncio.run(bot_loop())

# ===== MAIN =====
if __name__ == "__main__":
    print("🔥 Starting system...")

    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)