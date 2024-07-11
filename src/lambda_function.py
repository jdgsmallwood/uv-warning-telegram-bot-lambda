import os
import traceback
import xml.etree.ElementTree as ET
from datetime import datetime

import boto3
import requests
import telebot
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv
from loguru import logger
from pytz import timezone

load_dotenv()





def handler(event, context):
    logger.info("Running...")
    url = "https://uvdata.arpansa.gov.au/xml/uvvalues.xml"

    response = requests.get(url)

    if response.status_code == 200:
        root = ET.fromstring(response.content)
        melbourne = root.find(".//location[@id='Melbourne']")
        uv = melbourne.find("index").text

        try:
            uv = float(uv)
            previous_uv = get_previous_uv(uv)

            write_message_to_telegram(uv, previous_uv)
        except ValueError:
            logger.error(f"Failed to run with traceback {traceback.format_exc()}")


def write_message_to_telegram(uv: float, previous_uv: float) -> None:
    if previous_uv <= 3.0 and uv > 3.0:
        send_message_to_telegram(
            f"UV is {uv} > 3.0 - be sunsmart! UV observations courtesy of ARPANSA."
        )
    elif previous_uv > 3.0 and uv < 3.0:
        send_message_to_telegram(
            "UV is safe in Melbourne right now. UV observations courtesy of ARPANSA."
        )
    else:
        logger.info("Nothing to do - no state change!")


def get_previous_uv(uv: float) -> float:
    """Get previous UV value from DynamoDB.

    If no previous value was logged for today - defaults to returning zero.
    """
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("UVIndexTable")

    date_today = datetime.now(tz=timezone("Australia/Sydney")).strftime("%Y-%m-%d")
    response = table.query(KeyConditionExpression=Key("date").eq(date_today))

    if response["Count"] == 0:
        logger.info("Adding key for today")
        table.put_item(Item={"date": date_today, "uv_index": str(uv)})
        return 0.0

    logger.info("Key already exists for today...")
    previous_uv = float(response["Items"][0]["uv_index"])
    table.update_item(
        Key={"date": date_today},
        UpdateExpression="SET uv_index = :val1",
        ExpressionAttributeValues={":val1": str(uv)},
    )

    return previous_uv


def send_message_to_telegram(message: str) -> None:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")
    bot = telebot.TeleBot(BOT_TOKEN)
    bot.send_message(CHAT_ID, message)
