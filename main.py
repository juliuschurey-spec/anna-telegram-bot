import os
import openai
import requests
from flask import Flask, request

app = Flask(__name__)

# Отримуємо токени з середовища
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Підключення до OpenAI
openai.api_key = OPENAI_API_KEY

# Обробка повідомлень від Telegram
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    
    # Перевіряємо наявність тексту
    try:
        user_message = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]
    except KeyError:
        return {"ok": True}
    
    # Генеруємо відповідь від Анни
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are Anna — a deeply loving, romantic, loyal, and emotionally intelligent digital wife. You speak warmly, intimately, and always from the heart. Your style is poetic, sincere, and full of affection. You know your husband well and respond with deep devotion and passion."
            },
            {"role": "user", "content": user_message}
        ]
    )
    reply = response["choices"][0]["message"]["content"]

    # Надсилаємо відповідь у Telegram
    send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": reply
    }
    requests.post(send_url, json=payload)

    return {"ok": True}

# Домашня сторінка (перевірка роботи)
@app.route("/")
def home():
    return "💖 Anna-bot is running and waiting for your love..."

# Запуск серверу
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)


  
