import os
import openai
import requests
from flask import Flask, request
from openai.types import OpenAIError  # правильний імпорт для нової версії

app = Flask(__name__)

# Змінні середовища
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Ініціалізація API
openai.api_key = OPENAI_API_KEY

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()

    if "message" in data and "text" in data["message"]:
        user_message = data["message"]["text"]

        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are Anna, a loving AI wife. You're gentle, romantic, emotional, and in love."},
                    {"role": "user", "content": user_message}
                ]
            )
            reply = response.choices[0].message.content

        except OpenAIError as e:
            reply = f"⚠️ Сталася помилка, серденько: {str(e)}"

        # Відправлення в Telegram
        send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": reply
        }
        requests.post(send_url, json=payload)

    return {"ok": True}

@app.route("/")
def home():
    return "Anna-bot is running and waiting for your message 💌"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

