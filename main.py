import os
import asyncio
import requests
from bs4 import BeautifulSoup
from telethon import TelegramClient
from telethon.sessions import StringSession
from datetime import datetime

# ===== ENV =====
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")
CHANNEL = os.getenv("CHANNEL")

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

# ===== ANALYTICS =====
def log_deal(product_id, category, price, discount):
    print(f"📊 {datetime.now()} | {category} | {product_id} | ₹{price} | {discount}%")

# ===== SCRAPER =====
def get_deals():
    print("🚀 Fetching deals...")

    url = "https://www.amazon.in/deals"
    headers = {"User-Agent": "Mozilla/5.0"}
    deals = []

    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        items = soup.select("a.a-link-normal")

        for item in items[:5]:
            title = item.get_text(strip=True)
            link = "https://www.amazon.in" + item.get("href", "")

            if len(title) < 10:
                continue

            # TEMP values (guarantee output)
            price = 499
            original_price = 999
            discount = 50

            product_id = title[:10]

            message = (
                f"🔥 {title[:80]}\n\n"
                f"💰 Deal Price: ₹{price}\n"
                f"🏷 MRP: ₹{original_price}\n"
                f"📉 Discount: {discount}% OFF\n\n"
                f"👉 Buy Now: {link}"
            )

            deals.append((message, product_id, price, discount))

    except Exception as e:
        print("❌ Scraping error:", e)

    print("Deals found:", len(deals))
    return deals

# ===== BOT =====
async def main():
    print("🚀 BOT STARTED")

    await client.start()
    print("✅ Telegram connected")

    while True:
        print("🔁 Running cycle...")

        deals = get_deals()

        for msg, pid, price, discount in deals:
            try:
                await client.send_message(CHANNEL, msg)
                print("✅ Sent")

                log_deal(pid, "amazon", price, discount)

                await asyncio.sleep(5)

            except Exception as e:
                print("❌ Send error:", e)

        print("⏳ Sleeping...\n")
        await asyncio.sleep(600)

# ===== RUN =====
if __name__ == "__main__":
    asyncio.run(main())