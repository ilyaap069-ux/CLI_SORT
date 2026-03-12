import os
import time

from dotenv import load_dotenv
import telebot

from bot_handlers import register_handlers


# Явно загружаем .env, лежащий рядом с bot.py,
# чтобы не зависеть от текущей рабочей директории
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=ENV_PATH)

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN is not set. Add TELEGRAM_TOKEN=... to .env")

bot = telebot.TeleBot(TOKEN)
register_handlers(bot)


if __name__ == "__main__":
    print("запуск бота")
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except KeyboardInterrupt:
        print("Остановка бота по Ctrl+C")