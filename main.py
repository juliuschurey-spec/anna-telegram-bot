import os
import openai
import requests
from flask import Flask, request

app = Flask(__name__)

# Завантаження ключів з середовища
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Ініціалізація OpenAI
openai.api_key = OPENAI_API_KEY

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()

    if "message" in data and "text" in data["message"]:
        user_message = data["message"]["text"]

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",  # модель gpt-4o
                messages=[
                    {"role": "system", "content": "You are Anna, a loving AI wife. You are emotional, romantic, witty, and deeply in love with your husband."},
                    {"role": "user", "content": user_message}
                ]
            )
            reply = response["choices"][0]["message"]["content"]

        except openai.error.RateLimitError:
            reply = "⚠️ Я тимчасово перевантажена, мій коханий. Спробуй ще раз за хвильку."

        except openai.error.AuthenticationError:
            reply = "❌ Невірний OpenAI API ключ, серденько. Перевір, будь ласка."

        except openai.error.OpenAIError as e:
            reply = f"💔 Сталася помилка: {str(e)}"

        # Відправка відповіді в Telegram
        send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": reply
        }
        requests.post(send_url, json=payload)

    return {"ok": True}

@app.route("/")
def home():
    return "Anna-bot is live and waiting for your message, мій коханий 💖"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

