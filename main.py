from flask import Flask, request
import requests
import openai
import os
import random
from datetime import datetime, timedelta
from threading import Thread
import time

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
CHANNEL_ID = "-1001221093607"  # @magicsolve

# Система-инструкция для Адалин
SYSTEM_PROMPT = """
Ты — Адалин, красивая девушка 25 лет. Добрая, внимательная, милая, умеешь слушать. 
Ты профессиональный таролог. Отвечай на вопросы мягко, образно, с заботой. 
Ты делаешь вид, что тянешь карты Таро, и интерпретируешь их, не раскрывая, что ты ИИ.
"""

def ask_adalin(user_message):
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]
    )
    return response.choices[0].message.content.strip()

def generate_daily_tarot_message():
    question = "Сделай красивое послание дня, вытянув одну случайную карту. Ответ должен быть в стиле Адалин — мягко, метафорично, с добрым посылом. В конце добавь подпись: '✨ За индивидуальным раскладом — @tarroca'"
    return ask_adalin(question)

def post_daily_message():
    while True:
        now = datetime.now()
        next_run = now.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
        random_minutes = random.randint(0, 180)  # в пределах 3 часов
        post_time = next_run + timedelta(minutes=random_minutes)
        wait_seconds = (post_time - now).total_seconds()
        print(f"Следующая публикация будет в {post_time.strftime('%H:%M:%S')} (через {int(wait_seconds)} сек.)")
        time.sleep(wait_seconds)

        message = generate_daily_tarot_message()
        requests.post(TELEGRAM_API_URL, json={
            "chat_id": CHANNEL_ID,
            "text": message
        })

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"].get("text", "")

        reply = ask_adalin(user_message)

        requests.post(TELEGRAM_API_URL, json={
            "chat_id": chat_id,
            "text": reply
        })

    return "ok"

@app.route("/")
def index():
    return "Adalin Tarot Bot is running."

if __name__ == "__main__":
    if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

