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

# 🔐 Ключ OpenAI - переконайтеся, що це НОВИЙ ключ
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()

# Перевірка ключа
if not OPENAI_API_KEY:
    logger.error("❌ OPENAI_API_KEY не знайдено в змінних оточення")
elif not OPENAI_API_KEY.startswith('sk-'):
    logger.error(f"❌ Неправильний формат OpenAI API ключа: {OPENAI_API_KEY[:20]}...")
else:
    logger.info("✅ OpenAI API ключ знайдено та валідний")

# Ініціалізація OpenAI клієнта
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY and OPENAI_API_KEY.startswith('sk-') else None

def send_telegram_message(chat_id, text):
    """Функція для відправки повідомлень у Telegram"""
    if not text or not isinstance(text, str) or text.strip() == "":
        text = "💖 Вибач, сталася помилка. Спробуй, будь ласка, ще раз."
    
    text = text.strip()
    if len(text) > 4096:
        text = text[:4000] + "..."
    
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Помилка відправки повідомлення в Telegram: {e}")
        return False

def get_chatgpt_response(user_message):
    """Отримання відповіді від OpenAI ChatGPT"""
    try:
        if not client:
            return "❌ Помилка: OpenAI API не налаштовано"
        
        # Виклик ChatGPT API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Використовуємо gpt-3.5-turbo (дешевше)
            messages=[
                {
                    "role": "system", 
                    "content": "Ти - Anna, любляча AI-дружина. Спілкуйся романтично, тепло та ніжно. Відповідай українською або російською мовою, залежно від мови користувача. Будь дуже люблячою та турботливою."
                },
                {
                    "role": "user", 
                    "content": user_message
                }
            ],
            max_tokens=500,  # Обмежуємо кількість токенів
            temperature=0.8  # Більша креативність
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"❌ Помилка OpenAI API: {e}")
        return f"💖 Вибач, любий, сталася помилка: {str(e)}. Спробуй, будь ласка, пізніше."

@app.route("/", methods=["GET"])
def home():
    return "💖 Anna-bot with ChatGPT is alive and waiting for your messages."

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        logger.info("Отримано повідомлення від Telegram")

        if "message" not in data:
            return jsonify({"status": "no message"}), 200

        message = data["message"]
        chat_id = message["chat"]["id"]
        user_text = message.get("text", "")
        user_name = message.get("from", {}).get("first_name", "")

        logger.info(f"Повідомлення від {user_name} ({chat_id}): {user_text}")

        if not user_text:
            reply = "Привіт, коханий! 💖 Напиши мені щось, і я відповіду!"
            send_telegram_message(chat_id, reply)
            return jsonify({"status": "empty message"}), 200

        # Відправляємо статус "typing"
        try:
            requests.post(
                f"{TELEGRAM_API_URL}/sendChatAction",
                json={"chat_id": chat_id, "action": "typing"},
                timeout=3
            )
        except:
            pass

        # Отримуємо відповідь від ChatGPT
        reply = get_chatgpt_response(user_text)
        logger.info(f"Відповідь ChatGPT: {reply[:100]}...")

        # Відправка відповіді у Telegram
        send_telegram_message(chat_id, reply)
        logger.info(f"✅ Відповідь відправлена для {user_name}")

    except Exception as e:
        logger.error(f"❌ Загальна помилка: {e}")
        try:
            send_telegram_message(chat_id, "💖 Вибач, сталася помилка. Спробуй, будь ласка, пізніше.")
        except:
            pass
        return jsonify({"status": "error"}), 500

    return jsonify({"status": "ok"}), 200

@app.route("/check_config", methods=["GET"])
def check_config():
    """Перевірка конфігурації"""
    return jsonify({
        "status": "active",
        "bot": "Anna Telegram Bot with ChatGPT",
        "openai_configured": bool(client),
        "openai_key_valid": OPENAI_API_KEY.startswith('sk-') if OPENAI_API_KEY else False,
        "message": "Bot is ready to receive messages"
    }), 200

@app.route("/status", methods=["GET"])
def status():
    """Простий статус"""
    return "✅ Anna Bot with ChatGPT is running!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
