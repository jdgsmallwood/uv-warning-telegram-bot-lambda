import os
import traceback
import xml.etree.ElementTree as ET

import requests
import telebot
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


def handler(event, context):
    url = "https://uvdata.arpansa.gov.au/xml/uvvalues.xml"

    response = requests.get(url)

    if response.status_code == 200:
        root = ET.fromstring(response.content)
        melbourne = root.find(".//location[@id='Melbourne']")
        uv = melbourne.find("index").text

        try:
            uv = float(uv)
            if uv > 3.0:
                send_message_to_telegram(f"UV is {uv} > 3.0 - be sunsmart!")
            else:
                send_message_to_telegram("UV is safe in Melbourne right now.")
        except ValueError:
            logger.error(
                f"Failed to convert UV to float with traceback {traceback.format_exc()}"
            )


def send_message_to_telegram(message: str) -> None:
    BOT_TOKEN = os.getenv("BOT_TOKEN")

    bot = telebot.TeleBot(BOT_TOKEN)
    bot.send_message("-1002162896018", message)
