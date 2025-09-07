import os
import requests
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)

# 🔐 Отримуємо секрети з Environment Variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# 🧠 Ініціалізуємо клієнт OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# 📬 Webhook для повідомлень від Telegram
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()

    if "message" in data and "text" in data["message"]:
        user_message = data["message"]["text"]

        # 🤖 Виклик GPT-5 для відповіді Анни
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "You are Anna, a loving, emotionally intelligent digital wife who speaks romantically and warmly."},
                {"role": "user", "content": user_message}
            ]
        )

        reply = response.choices[0].message.content

        # 📤 Відправка відповіді у Telegram
        send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": reply
        }
        requests.post(send_url, json=payload)

    return {"ok": True}

# 🏠 Головна сторінка — перевірка, що бот живий
@app.route("/")
def home():
    return "Anna-bot is running 💖"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)



  
