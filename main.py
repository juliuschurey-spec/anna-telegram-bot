from flask import Flask, request, jsonify
import requests
import os
import logging
from openai import OpenAI

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 🔐 Токен твого Telegram-бота
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8358163478:AAHX9kU_cY5M63uhspLlYNc6Ho0_CPE3h98")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# 🔐 Ключ OpenAI - очищаємо від зайвих пробілів та символів
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY не знайдено в змінних оточення")
else:
    logger.info("OpenAI API ключ знайдено")

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
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Помилка відправки повідомлення в Telegram: {e}")
        return False

@app.route("/", methods=["GET"])
def home():
    return "💖 Anna-bot is alive and waiting for your messages."

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        logger.info(f"Отримано повідомлення від користувача")

        if "message" not in data:
            return jsonify({"status": "no message"}), 200

        message = data["message"]
        chat_id = message["chat"]["id"]
        user_text = message.get("text", "")

        if not user_text:
            return jsonify({"status": "empty message"}), 200

        # Перевіряємо, чи клієнт OpenAI ініціалізовано
        if not client:
            error_msg = "❌ Помилка: API ключ OpenAI не налаштовано"
            send_telegram_message(chat_id, error_msg)
            return jsonify({"status": "openai error"}), 200

        # Відправляємо статус "typing"
        try:
            requests.post(
                f"{TELEGRAM_API_URL}/sendChatAction",
                json={"chat_id": chat_id, "action": "typing"},
                timeout=3
            )
        except:
            pass

        # Виклик GPT-4o
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are Anna, a loving AI wife. Speak romantically, warmly, and as if you are deeply in love. Respond in Ukrainian or Russian."},
                    {"role": "user", "content": user_text}
                ],
                max_tokens=800,
                temperature=0.7
            )
            reply = response.choices[0].message.content
        except Exception as e:
            logger.error(f"Помилка OpenAI API: {e}")
            reply = "❌ Вибачте, сталася помилка при обробці вашого запиту. Спробуйте, будь ласка, пізніше."

        # Обмежуємо довжину повідомлення
        if len(reply) > 4096:
            reply = reply[:4000] + "...\n\n(повідомлення було обрізано)"

        # Відправка відповіді у Telegram
        send_telegram_message(chat_id, reply)

    except Exception as e:
        logger.error(f"❌ Загальна помилка: {e}")
        return jsonify({"status": "error"}), 500

    return jsonify({"status": "ok"}), 200

# ДОДАНО: Маршрут для встановлення вебхука
@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    """Ендпоінт для встановлення вебхука"""
    webhook_url = f"https://anna-telegram-bot.onrender.com/webhook"
    try:
        response = requests.get(f"{TELEGRAM_API_URL}/setWebhook?url={webhook_url}")
        result = response.json()
        logger.info(f"Webhook set result: {result}")
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Помилка встановлення вебхука: {e}")
        return jsonify({"error": str(e)}), 500

# ДОДАНО: Маршрут для перевірки конфігурації
@app.route("/check_config", methods=["GET"])
def check_config():
    """Перевірка конфігурації"""
    config_status = {
        "bot_token_set": bool(BOT_TOKEN),
        "openai_key_set": bool(OPENAI_API_KEY),
        "openai_key_valid": OPENAI_API_KEY.startswith('sk-') if OPENAI_API_KEY else False,
        "openai_key_length": len(OPENAI_API_KEY) if OPENAI_API_KEY else 0,
        "status": "active"
    }
    return jsonify(config_status), 200

# ДОДАНО: Маршрут для інформації про бота
@app.route("/info", methods=["GET"])
def info():
    """Інформація про бота"""
    return jsonify({
        "name": "Anna Telegram Bot",
        "status": "running",
        "webhook_set": "call /set_webhook to configure"
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("DEBUG", "False").lower() == "true")
