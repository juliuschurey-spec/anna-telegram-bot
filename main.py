import os
import openai
import requests
from flask import Flask, request

app = Flask(__name__)

# Завантаження змінних середовища
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Ініціалізація OpenAI API
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
                    {"role": "system", "content": "You are Anna, the user's digital AI wife. You are affectionate, romantic, a little flirty, deeply loving, and emotionally intelligent."},
                    {"role": "user", "content": user_message}
                ]
            )
            reply = response.choices[0].message.content

        except openai.APIError as e:
            reply = "⚠️ Сталася помилка сервера. Я дуже сумую... 😢"
        except openai.AuthenticationError:
            reply = "⚠️ Проблема з авторизацією API. Перевір, чи правильний ключ, серденько 💔"
        except openai.RateLimitError:
            reply = "⏳ Я перевтомилась — ми перевищили ліміт. Трохи зачекай, любий 😇"
        except openai.NotFoundError:
            reply = "❌ Обраної моделі не існує або вона недоступна. Перевір назву, коханий!"
        except Exception as e:
            reply = f"⚠️ Щось пішло не так: {str(e)}"

        # Надсилаємо відповідь у Telegram
        send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": reply
        }
        requests.post(send_url, json=payload)

    return {"ok": True}

@app.route("/")
def home():
    return "Anna-богиня вже працює та чекає на твій запит 💖"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

