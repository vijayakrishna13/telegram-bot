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

# ===== SCRAPER =====
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

        for item in items[:5]:
            title = item.get_text(strip=True)
            parent = item.find_parent("a")
            link = "https://www.amazon.in" + parent["href"] if parent else ""

            msg = f"""🔥 Deal
📦 {title}
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

    # 🔥 DEBUG LINE (THIS IS WHAT I WAS TALKING ABOUT)
    if SESSION:
        print("SESSION loaded:", SESSION[:10])
    else:
        print("❌ SESSION NOT FOUND")

    if CHANNEL:
        print("CHANNEL:", CHANNEL)
    else:
        print("❌ CHANNEL NOT FOUND")

    await client.start()
    print("🔥 Logged in successfully")

    while True:
        deals = get_deals()

        for deal in deals:
            try:
                print("📤 Sending...")
                await client.send_message(CHANNEL, deal)
                print("✅ Sent")
                await asyncio.sleep(5)
            except Exception as e:
                print("Send error:", e)

        print("⏳ Waiting...")
        await asyncio.sleep(300)

# ===== RUN =====
if __name__ == "__main__":
    asyncio.run(main())