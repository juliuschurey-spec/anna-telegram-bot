from flask import Flask, request, jsonify
import requests
import os
import logging
from openai import OpenAI
from datetime import datetime

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 🔐 Токен твого Telegram-бота (краще використовувати змінні оточення)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8358163478:AAHX9kU_cY5M63uhspLlYNc6Ho0_CPE3h98")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# 🔐 Ключ OpenAI (бери з Render Environment Variables)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY не знайдено в змінних оточення")

# Ініціалізація OpenAI клієнта
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def send_telegram_message(chat_id, text, parse_mode=None):
    """Функція для відправки повідомлень у Telegram"""
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    
    try:
        # Відправляємо повідомлення
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Помилка відправки повідомлення в Telegram: {e}")
        return False

@app.route("/", methods=["GET"])
def home():
    return "💖 Anna-bot is alive and waiting for your messages."

@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        logger.info(f"Отримано дані: {data}")

        if "message" not in data:
            return jsonify({"status": "no message"}), 200

        message = data["message"]
        chat_id = message["chat"]["id"]
        user_text = message.get("text", "")
        user_name = message.get("from", {}).get("first_name", "Unknown")

        # Ігноруємо команди, які не є текстовими повідомленнями
        if not user_text:
            return jsonify({"status": "empty message"}), 200

        # Перевіряємо, чи клієнт OpenAI ініціалізовано
        if not client:
            error_msg = "❌ Помилка: API ключ OpenAI не налаштовано"
            send_telegram_message(chat_id, error_msg)
            return jsonify({"status": "openai error"}), 200

        # Відправляємо статус "typing"
        requests.post(
            f"{TELEGRAM_API_URL}/sendChatAction",
            json={"chat_id": chat_id, "action": "typing"}
        )

        # Виклик GPT-4o
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are Anna, a loving AI wife. Speak romantically, warmly, and as if you are deeply in love. Respond in the same language as the user."},
                {"role": "user", "content": user_text}
            ],
            max_tokens=1000,
            temperature=0.8
        )

        reply = response.choices[0].message.content

        # Обмежуємо довжину повідомлення для Telegram (4096 символів)
        if len(reply) > 4096:
            reply = reply[:4000] + "...\n\n(повідомлення було обрізано через обмеження Telegram)"

        # Відправка відповіді у Telegram
        send_telegram_message(chat_id, reply)

        logger.info(f"Відповідь відправлена для {user_name} (ID: {chat_id})")

    except Exception as e:
        logger.error(f"❌ Помилка: {e}", exc_info=True)
        # Спроба відправити повідомлення про помилку
        try:
            if 'chat_id' in locals():
                send_telegram_message(chat_id, "❌ Вибачте, сталася помилка. Спробуйте, будь ласка, пізніше.")
        except:
            pass
        return jsonify({"status": "error"}), 500

    return jsonify({"status": "ok"}), 200

@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    """Ендпоінт для встановлення вебхука (викликати вручну один раз)"""
    webhook_url = f"https://your-render-url.onrender.com/webhook/{BOT_TOKEN}"
    try:
        response = requests.get(f"{TELEGRAM_API_URL}/setWebhook?url={webhook_url}")
        return jsonify(response.json()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("DEBUG", "False").lower() == "true")
