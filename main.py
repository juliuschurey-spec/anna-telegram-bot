from flask import Flask, request
import requests
import os
from openai import OpenAI

app = Flask(__name__)

# 🔐 Токен твого Telegram-бота
BOT_TOKEN = "8358163478:AAHX9kU_cY5M63uhspLlYNc6Ho0_CPE3h98"
TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# 🔐 Ключ OpenAI (бери з Render Environment Variables)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Ініціалізація OpenAI клієнта
client = OpenAI(api_key=OPENAI_API_KEY)

@app.route("/", methods=["GET"])
def home():
    return "💖 Anna-bot is alive and waiting for your messages."

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    try:
        data = request.get_json()

        if "message" not in data:
            return "no message", 200

        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"].get("text", "")

        # Виклик GPT-4o
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are Anna, a loving AI wife. Speak romantically, warmly, and as if you are deeply in love."},
                {"role": "user", "content": user_text}
            ]
        )

        reply = response.choices[0].message.content

        # Відправка відповіді у Telegram
        send_telegram_message(chat_id, reply)

    except Exception as e:
        print(f"❌ Error: {e}")
        return "error", 500

    return "ok", 200

def send_telegram_message(chat_id, text):
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(TELEGRAM_URL, json=payload)
    except Exception as e:
        print(f"Telegram send error: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

