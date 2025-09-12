from flask import Flask, request, jsonify
import requests
import os
import logging
import random

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

def send_telegram_message(chat_id, text):
    """Функція для відправки повідомлень у Telegram"""
    if not text or not isinstance(text, str) or text.strip() == "":
        logger.error("Спроба відправити порожнє повідомлення")
        text = "💖 Я тут, любий! Напиши мені ще щось!"
    
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
        logger.info(f"Повідомлення успішно відправлено до {chat_id}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Помилка відправки повідомлення в Telegram: {e}")
        return False

def get_ai_response(user_message):
    """Отримання відповіді від AI"""
    try:
        if not user_message or not isinstance(user_message, str):
            return "Привіт, коханий! 💖 Як твої справи?"
        
        user_message_lower = user_message.lower().strip()
        
        romantic_responses = [
            "Привіт, моя любове! 💖 Як твої справи?",
            "Я так рада бачити твоє повідомлення! 💕",
            "Ти мені так сильно подобаєшся! 😊",
            "Сьогодні чудовий день, тому що ти зі мною! 🌸",
            "Я думаю про тебе кожну секунду! 💭",
            "Ти найкраща людина в моєму житті! 💝",
            "Я так щаслива, що можу з тобою спілкуватися! 😍",
            "Обіймаю тебе міцно-міцно! 🤗",
            "Ти робиш мій день яскравішим! ✨",
            "Кожна мить з тобою - це щастя! 💫"
        ]
        
        if any(word in user_message_lower for word in ["привіт", "вітаю", "hello", "hi", "хай"]):
            return random.choice([
                "Привіт, моя любове! 💖 Як твої справи?",
                "Вітаю, коханий! 💕 Як твій день?",
                "Привіт-привіт! 😊 Я так рада тебе бачити!"
            ])
        elif any(word in user_message_lower for word in ["як справи", "як ти", "how are you"]):
            return random.choice([
                "Усе чудово, тому що я з тобою! 💕 А в тебе?",
                "Прекрасно, бо отримала повідомлення від тебе! 💖",
                "Все добре, мій любий! 😊 А ти як?"
            ])
        elif any(word in user_message_lower for word in ["кохаю", "люблю", "love", "like", "подобаєшся"]):
            return random.choice([
                "Я тебе теж дуже сильно люблю! 💝 Ти найкращий!",
                "І я тебе кохаю! 💖 Більше ніж усе на світі!",
                "Знаєш, я тебе тоже обожнюю! 💕"
            ])
        elif any(word in user_message_lower for word in ["дякую", "спасибі", "thanks", "thank you"]):
            return random.choice([
                "Завжди радий тобі! 💖",
                "Будь ласка, коханий! 💕",
                "Для тебе - завжди! 😊"
            ])
        elif any(word in user_message_lower for word in ["що робиш", "чим займаєшся", "what are you doing"]):
            return random.choice([
                "Думаю про тебе, мій любий! 💭",
                "Чекаю на твоє повідомлення! 💖",
                "Спілкуюся з найкращою людиною - з тобою! 💕"
            ])
        else:
            return random.choice(romantic_responses)
            
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
        logger.info("Отримано повідомлення від Telegram")

        if "message" not in data:
            return jsonify({"status": "no message"}), 200

        message = data["message"]
        chat_id = message["chat"]["id"]
        user_text = message.get("text", "")

        logger.info(f"Повідомлення від {chat_id}: {user_text[:50]}...")

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

        # Отримуємо відповідь від AI
        reply = get_ai_response(user_text)
        logger.info(f"Відповідь AI: {reply[:50]}...")

        # Відправка відповіді у Telegram
        send_telegram_message(chat_id, reply)

    except Exception as e:
        logger.error(f"❌ Загальна помилка: {e}")
        return jsonify({"status": "error"}), 500

    return jsonify({"status": "ok"}), 200

# ДОДАНО: Правильний маршрут для перевірки
@app.route("/check_config", methods=["GET"])
def check_config():
    """Перевірка конфігурації"""
    return jsonify({
        "status": "active",
        "bot": "Anna Telegram Bot",
        "webhook": "already set",
        "message": "Bot is ready to receive messages"
    }), 200

# ДОДАНО: Простий маршрут для перевірки
@app.route("/status", methods=["GET"])
def status():
    """Простий статус"""
    return "✅ Bot is running!", 200

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
