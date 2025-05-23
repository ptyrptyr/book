import requests
from bs4 import BeautifulSoup
import time
import schedule
import datetime
import json
import asyncio
import os
from telegram import Bot
from telegram.constants import ParseMode

# --- Konfiguracja ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BOOKS_JSON_URL = os.getenv("BOOKS_JSON_URL")  # <- zdalny JSON
CHECK_INTERVAL_MINUTES = 15
DEBUG = True

def load_books_from_url():
    try:
        response = requests.get(BOOKS_JSON_URL)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Błąd podczas wczytywania JSON z URL: {e}")
        return []

BOOK_ITEMS = load_books_from_url()
notifications_sent_status = {item["url"]: False for item in BOOK_ITEMS}

async def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Brak tokena lub chat ID")
        return
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode=ParseMode.MARKDOWN)
        if DEBUG:
            print(f"[Telegram] Wysłano wiadomość: {message}")
    except Exception as e:
        print(f"Błąd przy wysyłaniu wiadomości: {e}")

async def check_single_book(book):
    book_url = book["url"]
    book_name = book["name"]
    filia_name = book["filia_name"]
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] Sprawdzam: {book_name} ({book_url}) dla {filia_name}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(book_url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        text_nodes = soup.find_all(string=lambda t: filia_name in t)
        found = False

        for node in text_nodes:
            parent = node.parent
            for _ in range(7):
                if parent.find('button', class_='record-av-agenda-button-available'):
                    found = True
                    break
                parent = parent.parent
            if found:
                break

        if found:
            if not notifications_sent_status.get(book_url):
                msg = f"🔔 Książka *'{book_name}'* JEST DOSTĘPNA w *{filia_name}*!\n[Link]({book_url})"
                await send_telegram_message(msg)
                notifications_sent_status[book_url] = True
        else:
            print(f"[{current_time}] '{book_name}' niedostępna.")
            notifications_sent_status[book_url] = False
    except Exception as e:
        print(f"[{current_time}] Błąd: {e}")

async def check_all_books():
    for book in BOOK_ITEMS:
        await check_single_book(book)
        await asyncio.sleep(1)

async def job():
    now = datetime.datetime.now()
    if now.weekday() < 5 and 7 <= now.hour < 18:
        if DEBUG:
            print(f"[{now}] Sprawdzam wg harmonogramu...")
        await check_all_books()
    else:
        if DEBUG:
            print(f"[{now}] Poza godzinami sprawdzania.")

async def scheduler_loop():
    schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(lambda: asyncio.create_task(job()))
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

if __name__ == "__main__":
    print("--- START MONITORINGU ---")
    asyncio.run(send_telegram_message(f"🤖 Skrypt uruchomiony o {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."))
    asyncio.run(job())
    asyncio.run(scheduler_loop())
