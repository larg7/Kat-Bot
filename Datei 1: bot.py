import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import re

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

def send_to_notion(modell, ankauf, markt):
    url = "https://api.notion.com/v1/pages"

    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Modell": {
                "title": [{"text": {"content": modell}}]
            },
            "Ankauf (€)": {"number": ankauf},
            "Marktwert (€)": {"number": markt}
        }
    }

    requests.post(url, json=data, headers=headers)

def parse(text):
    ankauf = int(re.findall(r'\d+', text)[0])
    modell = re.sub(r'\d+', '', text).strip()

    if "GM26" in text:
        markt = 150
    elif "Prius" in text:
        markt = 500
    else:
        markt = ankauf * 2

    return modell, ankauf, markt

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    modell, ankauf, markt = parse(text)
    profit = markt - ankauf

    send_to_notion(modell, ankauf, markt)

    await update.message.reply_text(
        f"✅ Gespeichert\n\n"
        f"Modell: {modell}\n"
        f"Ankauf: {ankauf}€\n"
        f"Markt: {markt}€\n"
        f"Gewinn: {profit}€"
    )

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, handle))

print("Bot läuft...")
app.run_polling()
