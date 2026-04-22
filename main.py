import os
import asyncio
import requests
from bs4 import BeautifulSoup
from flask import Flask
from telethon import TelegramClient
from telethon.sessions import StringSession

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
    return "Bot running"

async def run_flask():
    from threading import Thread
    def start():
        app.run(host="0.0.0.0", port=10000)
    Thread(target=start).start()

# ===== SCRAPER (SMART FILTER) =====
def get_deals():
    print("🚀 Fetching deals...")

    headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://www.amazon.in/gp/bestsellers/electronics/"
    deals = []

    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        items = soup.select("._cDEzb_p13n-sc-css-line-clamp-3_g3dy1")

        print(f"Products found: {len(items)}")

        for item in items[:10]:
            title = item.get_text(strip=True)
            parent = item.find_parent("a")
            link = "https://www.amazon.in" + parent["href"] if parent else ""

            # open product page
            page = requests.get(link, headers=headers)
            psoup = BeautifulSoup(page.text, "html.parser")

            # ===== EXTRACT DATA =====
            rating_tag = psoup.select_one(".a-icon-alt")
            review_tag = psoup.select_one("#acrCustomerReviewText")
            price_tag = psoup.select_one(".a-price-whole")

            rating = rating_tag.get_text(strip=True) if rating_tag else ""
            reviews = review_tag.get_text(strip=True) if review_tag else ""
            price = price_tag.get_text(strip=True).replace(",", "") if price_tag else "0"

            try:
                rating_value = float(rating.split()[0])
                review_count = int(reviews.split()[0].replace(",", ""))
                price_value = int(price)
            except:
                continue

            # ===== SMART FILTER =====
            if rating_value < 4.0:
                continue

            if review_count < 500:
                continue

            if price_value == 0 or price_value > 50000:
                continue

            # ===== MESSAGE =====
            msg = f"""🔥 Verified Deal

📦 {title}
💰 ₹{price_value}
⭐ {rating}
📝 {reviews}

👉 {link}
"""

            deals.append(msg)

    except Exception as e:
        print("Scraping error:", e)

    print(f"Deals ready: {len(deals)}")
    return deals

# ===== MAIN =====
async def main():
    print("🚀 Starting bot...")

    await run_flask()

    await client.start()
    print("🔥 Logged in successfully")

    while True:
        deals = get_deals()

        if not deals:
            print("❌ No good deals found")

        for deal in deals:
            try:
                print("📤 Sending...")
                await client.send_message(CHANNEL, deal)
                print("✅ Sent")
                await asyncio.sleep(5)
            except Exception as e:
                print("Send error:", e)

        print("⏳ Waiting 10 minutes...")
        await asyncio.sleep(600)  # 10 min loop

# ===== RUN =====
if __name__ == "__main__":
    asyncio.run(main())