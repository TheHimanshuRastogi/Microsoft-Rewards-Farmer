"""
This is a module docstring
"""


import requests

from src.os import Os


MAX_LENGTHS = {
    "telegram": 4096,
    "discord": 2000,
}


class Notifier:
    def __init__(self):
        self.os = Os()
        self.tg_chat_id = self.os.env("TG_CHAT_ID")
        self.tg_bot_token = self.os.env("TG_BOT_TOKEN")
        self.discord_webhook_url = self.os.env("DISCORD_WEBHOOK_URL")

    def telegram(self, message):
        data = {"chat_id": self.tg_chat_id, "text": message}
        requests.post(url=f"https://api.telegram.org/bot{self.tg_bot_token}/sendMessage", data=data)

    def discord(self, message):
        data = {"email": "Microsoft Rewards Farmer", "content": message}
        requests.post(url=self.discord_webhook_url, data=data)
