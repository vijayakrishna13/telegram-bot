from telethon import TelegramClient

api_id = 34165554
api_hash = "6879f17a50febfb32f9264b7300a8066"

client = TelegramClient("user_session", api_id, api_hash)

client.start()
print("✅ Login successful")