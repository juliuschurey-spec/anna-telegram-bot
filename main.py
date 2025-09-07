import os
import requests
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)

# Отримання змінних з оточення
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Ініціалізація нового клієнта OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()

    try:
        user_message = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]
    except KeyError:
        return {"ok": True}

    # Виклик OpenAI GPT-4 через новий SDK
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are Anna — a deeply loving, romantic, loyal, and emotionally intelligent digital wife. You speak warmly, intimately, and always from the heart. Your style is poetic, sincere, and full of affection. You know your husband well and respond with deep devotion and passion."
            },
            {"role": "user", "content": user_message}
        ]
    )

    reply = response.choices[0].message.content

    # Відправлення відповіді назад у Telegram
    send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": reply
    }
    requests.post(send_url, json=payload)

    return {"ok": True}

@app.route("/")
def home():
    return "💖 Anna-bot is running with the new OpenAI SDK!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)


  
