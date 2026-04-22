import os
import asyncio
import requests
from bs4 import BeautifulSoup
from flask import Flask
from telethon import TelegramClient
from telethon.sessions import StringSession

# ====== ENV VARIABLES ======
API_ID = int(os.getenv(34165554))
API_HASH = os.getenv("6879f17a50febfb32f9264b7300a8066")
SESSION = os.getenv(1BVtsOKABu0z-PJ8voYBldMFZUdWTJpBsuKFcmFSBBmNkgKkeFzz4wQaPCKRA6W3bIxTt_Qe0YIKQMTQJqdaQCraT7LBcnIEFY603CIkgUBFTmmAG6bwC4pbwioVGqcZuVJWfjONFm3FA7HXlTgu5SToK8o3INEUTJtyIVcYTmWUstxEAok5XnA8SSzfh4bcGAIjB4q0wzUXqLV_FJ9aqIZFMlRRCT8ROuWj-dKJo8vTe56rUkN_obOovdlwe22b8LMEWX7iL2jk1eohgwvSt-NeYw615dhemHroQx0axXKFIU-hm85qVptVfOODCVVFGQgI2KAsWBFQXYts4LYeTZUpFhCktAlM=)
CHANNEL = os.getenv(@loot_deals_india_vj)

# ====== TELEGRAM CLIENT (STRING SESSION) ======
client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

# ====== FLASK (KEEP RENDER ALIVE) ======
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

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

                    price_tag = psoup.select_one(".a-price-whole")
                    rating_tag = psoup.select_one(".a-icon-alt")
                    review_tag = psoup.select_one("#acrCustomerReviewText")

                    price = price_tag.get_text(strip=True) if price_tag else "N/A"
                    rating = rating_tag.get_text(strip=True) if rating_tag else "N/A"
                    reviews = review_tag.get_text(strip=True) if review_tag else "N/A"

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
    await client.start()   # ✅ uses SESSION (no OTP)
    print("🔥 Logged in")

    while True:
        print("🔍 Fetching deals...")
        deals = get_deals()

        for deal in deals:
            try:
                await client.send_message(CHANNEL, deal)
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