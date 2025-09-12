import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
from dotenv import load_dotenv

# Завантаження змінних середовища
load_dotenv()

# Налаштування
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Ініціалізація клієнта OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка команди /start"""
    await update.message.reply_text(
        'Привіт! Я бот з інтеграцією ChatGPT. Напиши мені щось, і я спробую відповісти!'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка повідомлень від користувача"""
    try:
        user_message = update.message.text
        
        # Виклик ChatGPT API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}],
            max_tokens=500
        )
        
        bot_response = response.choices[0].message.content
        await update.message.reply_text(bot_response)
        
    except Exception as e:
        logging.error(f"Помилка: {str(e)}")
        await update.message.reply_text("Виникла помилка при обробці запиту. Спробуйте ще раз.")

def main():
    """Запуск бота"""
    # Створення додатку
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Додавання обробників
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()

