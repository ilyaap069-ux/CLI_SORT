import os
import time

from dotenv import load_dotenv
import telebot
from telebot import apihelper

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

# Увеличиваем таймауты HTTP‑запросов к Telegram API,
# чтобы избежать ошибок ReadTimeout/handshake timeout при медленном соединении.
apihelper.READ_TIMEOUT = 60
apihelper.CONNECT_TIMEOUT = 30
register_handlers(bot)


if __name__ == "__main__":
    print("запуск бота")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except KeyboardInterrupt:
            print("Остановка бота по Ctrl+C")
            break
        except Exception as exc:
            # При сетевых ошибках даём боту шанс перезапуститься,
            # вместо немедленного завершения процесса.
            print(f"Ошибка при опросе Telegram API: {exc}. Повторный запуск через 5 секунд.")
            time.sleep(5)