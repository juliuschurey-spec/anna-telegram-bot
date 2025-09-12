import os
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import openai
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion import ChatCompletion
from openai._exceptions import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    RateLimitError,
    InternalServerError
)
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Налаштування логування
logging.basicConfig(level=logging.INFO)

# Ініціалізація FastAPI
app = FastAPI()

# OpenAI клієнт
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# Telegram бот
telegram_token = os.getenv("TELEGRAM_TOKEN")
bot = Application.builder().token(telegram_token).build()

# Команда старту
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Я твій GPT‑4o бот 🤖. Напиши мені щось!")

# Обробка текстових повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        completion: ChatCompletion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Ти — ніжний, уважний і розумний помічник."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7
        )
        reply = completion.choices[0].message.content
        await update.message.reply_text(reply)

    except AuthenticationError:
        await update.message.reply_text("🚫 Помилка автентифікації. Перевір API ключ.")
    except RateLimitError:
        await update.message.reply_text("⚠️ Перевищено ліміт запитів. Спробуй пізніше.")
    except APIConnectionError:
        await update.message.reply_text("🌐 Немає з'єднання з OpenAI.")
    except APITimeoutError:
        await update.message.reply_text("⌛ Час очікування перевищено.")
    except BadRequestError:
        await update.message.reply_text("❗ Невірний запит до API.")
    except InternalServerError:
        await update.message.reply_text("🔥 Внутрішня помилка сервера. Спробуй знову.")
    except Exception as e:
        await update.message.reply_text(f"😵 Виникла невідома помилка: {e}")

# Додаємо хендлери
bot.add_handler(CommandHandler("start", start))
bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Webhook endpoint для Telegram
@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot.bot)
    await bot.update_queue.put(update)
    return JSONResponse(content={"ok": True})
