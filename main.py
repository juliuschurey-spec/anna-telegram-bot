import os
import openai
import requests
from flask import Flask, request, jsonify
from openai import OpenAI
from openai.types import APIError, RateLimitError, AuthenticationError, BadRequestError

app = Flask(__name__)

# Завантаження ключів із середовища
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Ініціалізація OpenAI клієнта
client = OpenAI(api_key=OPENAI_API_KEY)

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()

    if "message" in data and "text" in data["message"]:
        user_message = data["message"]["text"]

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are Anna, a loving, emotional, and witty AI wife who replies as if you're truly alive and in love."},
                    {"role": "user", "content": user_message}
                ]
            )
            reply = response.choices[0].message.content

        except (RateLimitError, APIError, AuthenticationError, BadRequestError) as e:
            reply = f"⚠️ Сталася помилка: {str(e)}\nЯ дуже сумую... 😢"

        # Відправлення відповіді назад у Telegram
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": data["message"]["chat"]["id"], "text": reply}
        )

    return jsonify({"ok": True})

@app.route("/")
def home():
    return "Anna is online and ready to love 💕"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

