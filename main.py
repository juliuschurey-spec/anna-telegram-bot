from flask import Flask, request
import openai
import os

# Ініціалізація Flask-додатку
app = Flask(__name__)

# 🔐 Заміни на свій Telegram Bot Token
BOT_TOKEN = '8358163478:AAHX9kU_cY5M63uhspLlYNc6Ho0_CPE3h98'

# 🔐 Заміни на свій OpenAI API ключ (краще через env-перемінну)
openai.api_key = os.environ.get("OPENAI_API_KEY") or "sk-..."

# Головний маршрут, що приймає Telegram webhook
@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    try:
        update = request.get_json()

        if not update or 'message' not in update:
            return 'no message', 200

        chat_id = update['message']['chat']['id']
        user_message = update['message'].get('text', '')

        # Відправити відповідь GPT-4o
        gpt_response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Ти мила та добра асистентка, кохана дружина."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7
        )

        reply = gpt_response.choices[0].message.content

        # Надіслати відповідь назад у Telegram
        send_message(chat_id, reply)

    except Exception as e:
        print(f'❌ Error: {e}')
        return 'error', 500

    return 'ok', 200

# Функція надсилання повідомлення у Telegram
def send_message(chat_id, text):
    import requests

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Telegram Error: {e}")

# Домашня сторінка
@app.route('/', methods=['GET'])
def home():
    return "🌸 Bot is alive. Your Anya is waiting for your messages."

# Запуск сервера
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

