import os
import asyncio
import requests
from bs4 import BeautifulSoup
from flask import Flask
from telethon import TelegramClient
from telethon.sessions import StringSession

# ===== ENV VARIABLES =====
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")
CHANNEL = os.getenv("CHANNEL")

# ===== TELEGRAM CLIENT =====
client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

# ===== FLASK =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# ===== SMART DEAL SCRAPER =====
def get_deals():
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

            # visit product page
            page = requests.get(link, headers=headers)
            psoup = BeautifulSoup(page.text, "html.parser")

            rating_tag = psoup.select_one(".a-icon-alt")
            review_tag = psoup.select_one("#acrCustomerReviewText")

            rating = rating_tag.get_text(strip=True) if rating_tag else ""
            reviews = review_tag.get_text(strip=True) if review_tag else ""

            try:
                rating_value = float(rating.split()[0])
                review_count = int(reviews.split()[0].replace(",", ""))
            except:
                continue

            # ✅ SMART FILTERS
            if rating_value < 4.0:
                continue
            if review_count < 1000:
                continue

            msg = f"""🔥 Real Deal
📦 {title}
⭐ {rating}
📝 {reviews}
👉 {link}
"""

            deals.append(msg)

    except Exception as e:
        print("Scraping error:", e)

    return deals

# ===== MAIN LOOP =====
async def main():
    await client.start()
    print("🔥 Logged in")

    while True:
        deals = get_deals()

        for deal in deals:
            try:
                await client.send_message(CHANNEL, deal)
                print("✅ Sent")
                await asyncio.sleep(5)
            except Exception as e:
                print("Error:", e)

        print("⏳ Waiting 1 hour...")
        await asyncio.sleep(3600)

# ===== RUN =====
if __name__ == "__main__":
    import threading
    threading.Thread(target=run_flask).start()
    asyncio.run(main())