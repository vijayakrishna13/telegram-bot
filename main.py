import os
import asyncio
import requests
from bs4 import BeautifulSoup
from flask import Flask
from telethon import TelegramClient

# ====== YOUR CREDENTIALS ======
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
phone = os.getenv("PHONE")
channel = os.getenv("CHANNEL")  # your Telegram channel username

# ====== TELEGRAM CLIENT ======
client = TelegramClient("session", api_id, api_hash)

# ====== FLASK (RENDER KEEP ALIVE) ======
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# ====== SCRAPER ======
def get_deals():
    headers = {"User-Agent": "Mozilla/5.0"}

    categories = [
        "https://www.amazon.in/gp/bestsellers/electronics/",
        "https://www.amazon.in/gp/bestsellers/kitchen/",
        "https://www.amazon.in/gp/bestsellers/fashion/",
    ]

    deals = []

    for url in categories:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            items = soup.select("._cDEzb_p13n-sc-css-line-clamp-3_g3dy1")

            for item in items[:3]:  # keep low to avoid block
                try:
                    title = item.get_text(strip=True)

                    parent = item.find_parent("a")
                    link = "https://www.amazon.in" + parent["href"] if parent else ""

                    # 👉 Visit product page
                    product_page = requests.get(link, headers=headers, timeout=10)
                    product_soup = BeautifulSoup(product_page.text, "html.parser")

                    # Price
                    price_tag = product_soup.select_one(".a-price-whole")
                    price = price_tag.get_text(strip=True) if price_tag else "N/A"

                    # Rating
                    rating_tag = product_soup.select_one(".a-icon-alt")
                    rating = rating_tag.get_text(strip=True) if rating_tag else "N/A"

                    # Reviews
                    review_tag = product_soup.select_one("#acrCustomerReviewText")
                    reviews = review_tag.get_text(strip=True) if review_tag else "N/A"

                    message = f"""🔥 Bestseller
📦 {title}
💰 ₹{price}
⭐ {rating}
📝 {reviews}
👉 {link}
"""

                    deals.append(message)

                except Exception as e:
                    continue

        except Exception as e:
            continue

    return deals

# ====== MAIN BOT LOOP ======
async def main():
    await client.start()
    print("🔥 Logged in")

    while True:
        print("🔍 Fetching deals...")
        deals = get_deals()

        for deal in deals:
            try:
                await client.send_message(channel, deal)
                print("✅ Sent")
                await asyncio.sleep(5)
            except Exception as e:
                print("Error:", e)

        print("⏳ Waiting 1 hour...\n")
        await asyncio.sleep(3600)

# ====== RUN BOTH ======
if __name__ == "__main__":
    import threading
    threading.Thread(target=run_flask).start()
    asyncio.run(main())