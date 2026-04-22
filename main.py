import os
import asyncio
import requests
from bs4 import BeautifulSoup
from flask import Flask
from telethon import TelegramClient

# ====== ENV VARIABLES ======
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
channel = os.getenv("CHANNEL")

# ⚠️ IMPORTANT: no phone here
client = TelegramClient("user_session", api_id, api_hash)

# ====== FLASK (KEEP ALIVE) ======
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot running"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# ====== AMAZON SCRAPER ======
def get_deals():
    headers = {"User-Agent": "Mozilla/5.0"}

    urls = [
        "https://www.amazon.in/gp/bestsellers/electronics/",
        "https://www.amazon.in/gp/bestsellers/kitchen/",
        "https://www.amazon.in/gp/bestsellers/fashion/",
    ]

    deals = []

    for url in urls:
        try:
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")

            items = soup.select("._cDEzb_p13n-sc-css-line-clamp-3_g3dy1")

            for item in items[:3]:
                try:
                    title = item.get_text(strip=True)

                    parent = item.find_parent("a")
                    link = "https://www.amazon.in" + parent["href"] if parent else ""

                    # visit product page
                    page = requests.get(link, headers=headers, timeout=10)
                    psoup = BeautifulSoup(page.text, "html.parser")

                    price = psoup.select_one(".a-price-whole")
                    rating = psoup.select_one(".a-icon-alt")
                    reviews = psoup.select_one("#acrCustomerReviewText")

                    price = price.get_text(strip=True) if price else "N/A"
                    rating = rating.get_text(strip=True) if rating else "N/A"
                    reviews = reviews.get_text(strip=True) if reviews else "N/A"

                    msg = f"""🔥 Bestseller
📦 {title}
💰 ₹{price}
⭐ {rating}
📝 {reviews}
👉 {link}
"""

                    deals.append(msg)

                except:
                    continue

        except:
            continue

    return deals

# ====== MAIN LOOP ======
async def main():
    await client.start()  # ✅ NO PHONE → NO OTP
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

# ====== RUN ======
if __name__ == "__main__":
    import threading
    threading.Thread(target=run_flask).start()
    asyncio.run(main())