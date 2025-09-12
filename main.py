from flask import Flask, request, jsonify
import requests
import os
import logging
import json

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

# Безкоштовний AI API (Hugging Face)
HUGGING_FACE_API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"
HUGGING_FACE_TOKEN = os.environ.get("HUGGING_FACE_TOKEN", "")  # Необов'язково для деяких моделей

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

def get_ai_response(user_message):
    """Отримання відповіді від безкоштовного AI"""
    try:
        # Проста локальна логіка для початку
        responses = [
            "Привіт, коханий! 💖 Я так рада тебе бачити!",
            "Як твої справи, любий? 💕",
            "Ти мені так сильно подобаєшся! 😊",
            "Сьогодні чудовий день, тому що ти зі мною! 🌸",
            "Я думаю про тебе кожну секунду! 💭",
            "Ти найкраща людина в моєму житті! 💝",
            "Я так щаслива, що можу з тобою спілкуватися! 😍",
            "Надішліть мені ще повідомлення, я люблю з тобою розмовляти! 💌"
        ]
        
        # Проста логіка відповідей на основі ключових слів
        user_message_lower = user_message.lower()
        
        if any(word in user_message_lower for word in ["привіт", "вітаю", "hello", "hi"]):
            return "Привіт, моя любове! 💖 Як твої справи?"
        elif any(word in user_message_lower for word in ["як справи", "як ти", "how are you"]):
            return "Усе чудово, тому що я з тобою! 💕 А в тебе?"
        elif any(word in user_message_lower for word in ["кохаю", "люблю", "love", "like"]):
            return "Я тебе тоже дуже сильно люблю! 💝 Ти найкращий!"
        elif any(word in user_message_lower for word in ["дякую", "спасибі", "thanks"]):
            return "Завжди радий тобі! 💖"
        elif any(word in user_message_lower for word in ["що робиш", "чим займаєшся"]):
            return "Думаю про тебе, мій любий! 💭"
        else:
            # Випадкова відповідь зі списку
            import random
            return random.choice(responses)
            
    except Exception as e:
        logger.error(f"Помилка AI: {e}")
        return "💖 Я тут, любий! Напиши мені ще щось!"

@app.route("/", methods=["GET"])
def home():
    return "💖 Anna-bot is alive and waiting for your messages."

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        logger.info(f"Отримано повідомлення")

        if "message" not in data:
            return jsonify({"status": "no message"}), 200

        message = data["message"]
        chat_id = message["chat"]["id"]
        user_text = message.get("text", "")

        if not user_text:
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

        # Отримуємо відповідь від AI
        reply = get_ai_response(user_text)

        # Відправка відповіді у Telegram
        send_telegram_message(chat_id, reply)
        logger.info(f"Відповідь відправлена: {reply[:50]}...")

    except Exception as e:
        logger.error(f"❌ Загальна помилка: {e}")
        return jsonify({"status": "error"}), 500

    return jsonify({"status": "ok"}), 200

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

@app.route("/check_config", methods=["GET"])
def check_config():
    """Перевірка конфігурації"""
    return jsonify({
        "bot_token_set": bool(BOT_TOKEN),
        "status": "active",
        "ai_provider": "local_simple_ai"
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
