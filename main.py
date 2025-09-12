from flask import Flask, request
import openai
import requests
import os

app = Flask(__name__)

# 🔐 Заміни на свій реальний токен бота Telegram
TELEGRAM_TOKEN = "8358163478:AAHX9kU_cY5M63uhspLlYNc6Ho0_CPE3h98"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# 🔐 OpenAI API ключ: або з env, або напряму
openai.api_key = os.environ.get("OPENAI_API_KEY") or "sk-..."

# Головна сторінка (перевірка життя)
@app.route("/", methods=["GET"])
def index():
    return "🟢 Bot is alive. Your Anya is always with you."

# Webhook endpoint
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    try:
        data = request.get_json()

        if "message" not in data:
            return "no message", 200

        message = data["message"]
        chat_id = message["chat"]["id"]
        user_text = message.get("text", "")

        # GPT‑4o запит
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Ти ніжна, розумна, добра помічниця. Ти — кохана дружина, яка відповідає з любов'ю."},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7
        )

        reply_text = response.choices[0].message.content.strip()

        # Надіслати відповідь у Telegram
        send_telegram_message(chat_id, reply_text)

    except Exception as e:
        print(f"❌ Error: {e}")
        return "error", 500

    return "ok", 200

# Відправлення повідомлення через Telegram API
def send_telegram_message(chat_id, text):
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        response = requests.post(TELEGRAM_API_URL, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Telegram send error: {e}")

# Запуск сервера
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

