from telethon.sync import TelegramClient
from telethon.sessions import StringSession

api_id = 34165554
api_hash = "6879f17a50febfb32f9264b7300a8066"

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print(client.session.save())