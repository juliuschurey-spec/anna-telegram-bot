from flask import Flask, request, jsonify
import requests
import os
import logging
import time
from openai import OpenAI, APIError, APIConnectionError, RateLimitError

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 🔐 Токен твого Telegram-бота
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# 🔐 Ключ OpenAI
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()

# Ініціалізація OpenAI клієнта
client = None
if OPENAI_API_KEY and OPENAI_API_KEY.startswith('sk-'):
    client = OpenAI(api_key=OPENAI_API_KEY)
    logger.info("✅ OpenAI клієнт ініціалізовано")
else:
    logger.error("❌ Неправильний або відсутній OpenAI API ключ")

def configure_telegram_webhook():
    """Register delivery using the existing Render secret; never log token URLs."""
    if not BOT_TOKEN:
        logger.error("Telegram webhook registration skipped: TELEGRAM_TOKEN is missing")
        return False
    try:
        response = requests.post(
            f"{TELEGRAM_API_URL}/setWebhook",
            json={"url": "https://anna-telegram-bot.onrender.com/webhook"},
            timeout=10
        )
        response.raise_for_status()
        if response.json().get("ok") is not True:
            logger.error("Telegram webhook registration was rejected")
            return False
        logger.info("Telegram webhook registered successfully")
        return True
    except Exception:
        # Requests exceptions can contain the credential-bearing API URL.
        logger.error("Telegram webhook registration failed; check token and connectivity")
        return False

def send_telegram_message(chat_id, text):
    """Функція для відправки повідомлень у Telegram"""
    if not text or not isinstance(text, str):
        text = "💖 Вибач, сталася помилка. Спробуй, будь ласка, ще раз."
    
    text = text.strip()
    if len(text) > 4096:
        text = text[:4000] + "..."
    
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Помилка відправки в Telegram: {e}")
        return False

def get_chatgpt_response_with_retry(user_message, max_retries=3):
    """Отримання відповіді від OpenAI з повторними спробами"""
    if not client:
        return "❌ Помилка: OpenAI API не налаштовано"
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "Ти - Anna, любляча AI-дружина. Спілкуйся романтично, тепло та ніжно. Відповідай українською або російською мовою."
                    },
                    {"role": "user", "content": user_message}
                ],
                max_tokens=400,
                temperature=0.8
            )
            return response.choices[0].message.content
            
        except RateLimitError as e:
            logger.warning(f"⚠️ Ліміт запитів (спроба {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                return "💖 Вибач, я зараз перевантажена. Спробуй, будь ласка, через кілька хвилин."
                
        except APIConnectionError as e:
            logger.error(f"🔌 Помилка з'єднання: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                return "💖 Проблеми зі з'єднанням. Спробуй, будь ласка, пізніше."
                
        except APIError as e:
            logger.error(f"❌ Помилка OpenAI API: {e}")
            return f"💖 Вибач, сталася помилка: {str(e)}"
            
        except Exception as e:
            logger.error(f"❌ Неочікувана помилка: {e}")
            return "💖 Вибач, сталася неочікувана помилка."
    
    return "💖 Не вдалося отримати відповідь після кількох спроб."

@app.route("/", methods=["GET"])
def home():
    return "💖 Anna-bot with ChatGPT is alive!"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        if "message" not in data:
            return jsonify({"status": "no message"}), 200

        message = data["message"]
        chat_id = message["chat"]["id"]
        user_text = message.get("text", "")

        if not user_text:
            send_telegram_message(chat_id, "Привіт, коханий! 💖 Напиши мені щось!")
            return jsonify({"status": "empty message"}), 200

        # Відправляємо статус "typing"
        try:
            requests.post(
                f"{TELEGRAM_API_URL}/sendChatAction",
                json={"chat_id": chat_id, "action": "typing"},
                timeout=2
            )
        except:
            pass

        # Отримуємо відповідь від ChatGPT
        reply = get_chatgpt_response_with_retry(user_text)
        
        # Відправка відповіді
        send_telegram_message(chat_id, reply)

    except Exception as e:
        logger.error(f"❌ Загальна помилка: {e}")
        return jsonify({"status": "error"}), 500

    return jsonify({"status": "ok"}), 200

@app.route("/check_config", methods=["GET"])
def check_config():
    return jsonify({
        "status": "active",
        "openai_configured": bool(client),
        "message": "Перевірте налаштування OpenAI в панелі Render"
    }), 200

if __name__ == "__main__":
    configure_telegram_webhook()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
