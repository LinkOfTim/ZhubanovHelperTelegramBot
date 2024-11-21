import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram.ext import ApplicationBuilder

from config import BOT_TOKEN
from handlers import register_user_handlers
from admin_handlers import register_admin_handlers

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Регистрация обработчиков
    register_user_handlers(application)
    register_admin_handlers(application)

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
