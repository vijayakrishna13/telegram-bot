from telethon import TelegramClient
import re
import asyncio

# 🔑 TELEGRAM CONFIG
api_id = 34165554
api_hash = '6879f17a50febfb32f9264b7300a8066'

client = TelegramClient('session', api_id, api_hash)

# 🎯 SOURCE CHANNEL (change if needed)
SOURCE_CHANNEL = 'loot_deals'

# 🎯 YOUR CHANNEL
TARGET_CHANNEL = 'loot_deals_india_vj'

# 💰 AFFILIATE TAG
AFFILIATE_TAG = "lootdealsvj21-21"

seen_links = set()


# 🔗 Convert to affiliate link
def convert_to_affiliate(link):
    link = re.sub(r'([&?])tag=[^&]+', '', link)

    if "amazon.in" in link:
        if "?" in link:
            return link + f"&tag={AFFILIATE_TAG}"
        else:
            return link + f"?tag={AFFILIATE_TAG}"

    return link


# 🧾 Extract first link
def extract_link(text):
    match = re.search(r'https?://\S+', text)
    return match.group() if match else None


# 🚀 MAIN LOOP
async def main():
    source = await client.get_entity(SOURCE_CHANNEL)
    target = await client.get_entity(TARGET_CHANNEL)

    await client.send_message(target, "✅ Stable system started")
    print("✅ Bot started")

    while True:
        print("\n🔍 Checking source channel...")

        async for message in client.iter_messages(source, limit=20):
            if not message.text:
                continue

            link = extract_link(message.text)

            # ✅ AMAZON FILTER (VERY IMPORTANT)
            if not link or "amazon.in" not in link:
                continue

            # ✅ DUPLICATE CHECK
            if link in seen_links:
                continue

            seen_links.add(link)

            # 💰 ADD AFFILIATE
            link = convert_to_affiliate(link)

            msg = f"🔥 Hot Deal\n💰 Limited Offer\n👉 {link}"

            try:
                await client.send_message(target, msg)
                print("📤 Posted:", link)
            except Exception as e:
                print("❌ Error:", e)

            await asyncio.sleep(2)

        print("⏳ Sleeping 30 seconds...\n")
        await asyncio.sleep(30)


# ▶️ RUN
with client:
    client.loop.run_until_complete(main())