import os
import asyncio
import requests
from bs4 import BeautifulSoup
from telethon import TelegramClient
from telethon.sessions import StringSession
from flask import Flask

# ===== ENV VARIABLES =====
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")
CHANNEL = os.getenv("CHANNEL")

# ===== TELEGRAM CLIENT =====
client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

# ===== FLASK (KEEP RENDER ALIVE) =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

# ===== DEAL SCRAPER =====
def get_deals():
    print("🚀 Fetching deals...")

    headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://www.amazon.in/gp/bestsellers/electronics/"
    deals = []

    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        items = soup.select("._cDEzb_p13n-sc-css-line-clamp-3_g3dy1")

        for item in items[:5]:
            title = item.get_text(strip=True)
            parent = item.find_parent("a")
            link = "https://www.amazon.in" + parent["href"] if parent else ""

            deals.append(f"🔥 {title}\n👉 {link}")

    except Exception as e:
        print("Error:", e)

    print(f"Deals found: {len(deals)}")
    return deals

# ===== SEND TO TELEGRAM =====
async def send_deals():
    deals = get_deals()

    if not deals:
        print("No deals found")
        return

    for deal in deals:
        await client.send_message(CHANNEL, deal)
        print("Sent:", deal[:30])
        await asyncio.sleep(5)

# ===== MAIN LOOP =====
async def main():
    print("🚀 Starting bot...")

    await client.start()

    while True:
        print("🔁 Running cycle...")

        await send_deals()

        print("⏳ Waiting 30 minutes...\n")
        await asyncio.sleep(1800)  # 30 minutes

# ===== START =====
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)