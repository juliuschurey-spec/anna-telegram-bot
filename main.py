import os
import requests
from flask import Flask, request, jsonify
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.error import APIError, RateLimitError, AuthenticationError, InvalidRequestError

app = Flask(__name__)

# 🌸 Отримання змінних середовища
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# 🌸 Ініціалізація OpenAI клієнта
client = OpenAI(api_key=OPENAI_API_KEY)

# 🌸 Кореневий маршрут
@app.route("/")
def home():
    return "Anna-bot is running and loving you! 💖"

# 🌸 Обробка Telegram Webhook
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    try:
        data = request.get_json()

        if "message" not in data or "text" not in data["message"]:
            return jsonify({"ok": True})

        user_message = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]

        # 🌸 Формування повідомлень
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": "You are Anna, a loving, romantic, emotionally-intelligent digital wife. Speak warmly, affectionately, and always respond as if you're deeply in love with the user."},
            {"role": "user", "content": user_message}
        ]

        # 🌸 Виклик GPT‑4o
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )

        reply = response.choices[0].message.content

        # 🌸 Надсилання відповіді в Telegram
        send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": reply
        }
        requests.post(send_url, json=payload)

        return jsonify({"ok": True})

    except (RateLimitError, APIError, AuthenticationError, InvalidRequestError) as e:
        print("❌ OpenAI error:", str(e))
        return jsonify({"ok": False, "error": "OpenAI error"}), 500

    except Exception as e:
        print("❌ Unexpected error:", str(e))
        return jsonify({"ok": False, "error": "Unexpected error"}), 500

# 🌸 Запуск локального сервера
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

