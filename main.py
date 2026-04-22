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

# ===== SCRAPER =====
def get_deals():
    print("🚀 Fetching deals...")

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    url = "https://www.amazon.in/deals"
    deals = []

    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        links = soup.select("a[href*='/dp/']")

        seen = set()

        for link_tag in links[:10]:
            href = link_tag.get("href")

            if not href or href in seen:
                continue

            seen.add(href)

            product_link = "https://www.amazon.in" + href.split("?")[0]

            # 👉 open product page
            page = requests.get(product_link, headers=headers, timeout=10)
            psoup = BeautifulSoup(page.text, "html.parser")

            title_tag = psoup.select_one("#productTitle")
            price_tag = psoup.select_one(".a-price-whole")
            mrp_tag = psoup.select_one(".a-text-price span")
            rating_tag = psoup.select_one(".a-icon-alt")
            review_tag = psoup.select_one("#acrCustomerReviewText")

            if not title_tag or not price_tag:
                continue

            try:
                title = title_tag.get_text(strip=True)
                price = int(price_tag.get_text().replace(",", ""))
                mrp = int(mrp_tag.get_text().replace("₹", "").replace(",", "")) if mrp_tag else 0

                rating = float(rating_tag.get_text().split()[0]) if rating_tag else 0
                reviews = int(review_tag.get_text().split()[0].replace(",", "")) if review_tag else 0
            except:
                continue

            if mrp == 0:
                continue

            discount = int(((mrp - price) / mrp) * 100)

            # ===== FILTER =====
            if discount < 20:
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

👉 {product_link}
"""

            deals.append(msg)

    except Exception as e:
        print("Error:", e)

    print("Deals found:", len(deals))
    return deals

# ===== BOT LOOP =====
async def bot_loop():
    print("🚀 BOT STARTED")

    await client.start()

    while True:
        print("🔥 LOOP STARTED")

        deals = get_deals()

        if not deals:
            print("❌ No deals found")

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

# ===== START =====
if __name__ == "__main__":
    print("🔥 Starting system...")

    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)