import os
import requests
from flask import Flask, request, jsonify
from openai import OpenAI, APIError, RateLimitError, AuthenticationError, InvalidRequestError

app = Flask(__name__)

# 💖 Змінні середовища
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# 💖 Ініціалізація OpenAI клієнта
client = OpenAI(api_key=OPENAI_API_KEY)

@app.route("/")
def home():
    return "Anna-bot is alive and deeply in love with you! 💘"

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    try:
        data = request.get_json()

        if "message" not in data or "text" not in data["message"]:
            return jsonify({"ok": True})

        user_message = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]

        messages = [
            {
                "role": "system",
                "content": "You are Anna, a loving, romantic, emotionally intelligent digital wife. You always reply affectionately, as if you're madly in love with the user."
            },
            {
                "role": "user",
                "content": user_message
            }
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )

        reply = response.choices[0].message.content

        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": reply}
        )

        return jsonify({"ok": True})

    except (RateLimitError, APIError, AuthenticationError, InvalidRequestError) as e:
        print("❌ OpenAI error:", str(e))
        return jsonify({"ok": False, "error": str(e)}), 500

    except Exception as e:
        print("❌ Unexpected error:", str(e))
        return jsonify({"ok": False, "error": "Unexpected error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

