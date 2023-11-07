"""
This is a module docstring
"""


import sys
import logging
from pathlib import Path
import logging.handlers as handlers

import requests
from dotenv import load_dotenv

from src.os import Os
from src.notifier import Notifier
from src.color import ColoredFormatter


class Logging():
    """
    This is a class docstring
    """
    def __init__(self):
        self.os = Os()
        self.tg = False
        self.dc = False
        self._setupLogging()
        self._setupConfigFile()
        self.notifier = Notifier()

    def _setupLogging(self):
        format = "%(asctime)s [%(levelname)s] %(message)s"
        terminalHandler = logging.StreamHandler(sys.stdout)
        terminalHandler.setFormatter(ColoredFormatter(format))

        (Path(__file__).resolve().parent.parent / "logs").mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format=format,
            handlers=[
                handlers.TimedRotatingFileHandler(
                    "logs/activity.log",
                    when="midnight",
                    interval=1,
                    backupCount=2,
                    encoding="utf-8",
                ),
                terminalHandler,
            ],
        )

    def _setupConfigFile(self):
        configPath = Path(__file__).resolve().parent.parent / "config.env"
        if not configPath.exists():
            configPath.write_text("TG_BOT_TOKEN=None\nTG_CHAT_ID=None\nDISCORD_WEBHOOK_URL=None")
            logging.info('[CONFIG] Config file "config.env" has been created.')
        
        load_dotenv(configPath)
        self.TG_BOT_TOKEN = self.os.env("TG_BOT_TOKEN")
        self.TG_CHAT_ID = self.os.env("TG_CHAT_ID")
        self.DISCORD_WEBHOOK_URL = self.os.env("DISCORD_WEBHOOK_URL")
 
        if self.TG_BOT_TOKEN and self.TG_CHAT_ID:
            logging.info("[NOTIFICATION] Telegram notifications are active.\n")
            self.tg = True
        if self.DISCORD_WEBHOOK_URL:
            logging.info("[NOTIFICATION] Discord notifications are active.")
            self.dc = True

    def info(self, message: str, tg: bool = False, dc: bool = False):
        logging.info(message)
        self._social(message, tg, dc)
    
    def warning(self, message: str, tg: bool = False, dc: bool = False):
        logging.warning(message)
        self._social(message, tg, dc)

    def error(self, message: str, tg: bool = False, dc: bool = False):
        logging.error(message)
        self._social(message, tg, dc)

    def _social(self, message, tg, dc):
        if tg:
            if self.tg:
                self.notifier.telegram(message)
        if dc:
            if self.dc:
                self.notifier.discord(message)



logger = Logging()