import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters

from menu import MenuManager
from config import MENU_FILE

menu_manager = MenuManager(MENU_FILE)

# Состояния для ConversationHandler
NAVIGATE_MENU = range(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['current_path'] = []
    return await show_menu(update, context)

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    current_path = context.user_data['current_path']
    menu_items = menu_manager.get_menu(current_path)

    choices = list(menu_items.keys())

    # Разбиваем на строки по 2 пункта в строке
    max_buttons_per_row = 2
    reply_keyboard = list(chunk_list(choices, max_buttons_per_row))

    if current_path:
        reply_keyboard.append(['Назад'])

    await update.message.reply_text(
        "Выберите пункт меню:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)
    )
    return NAVIGATE_MENU

async def navigate_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    current_path = context.user_data.get('current_path', [])
    menu_items = menu_manager.get_menu(current_path)

    # Если пользователь выбрал "Назад", возвращаемся на уровень выше
    if choice == 'Назад':
        if current_path:
            context.user_data['current_path'].pop()
        return await show_menu(update, context)

    # Проверяем, существует ли выбор в текущем меню
    if choice in menu_items:
        item = menu_items[choice]

        # Если у пункта есть подменю, обновляем текущий путь и показываем его
        if 'sub_menu' in item:
            context.user_data['current_path'].append(choice)
            return await show_menu(update, context)

        # Если у пункта есть текст, фото или документ, отправляем их
        if 'response' in item:
            await update.message.reply_text(item['response'])
        if 'photo' in item:
            await update.message.reply_photo(item['photo'])
        if 'document' in item:
            await update.message.reply_document(item['document'])

        # Возвращаем пользователя к текущему меню
        return await show_menu(update, context)

    # Если выбор не найден, выводим сообщение об ошибке и остаемся в текущем состоянии
    await update.message.reply_text("Пункт меню не найден. Попробуйте снова.")
    return NAVIGATE_MENU

def chunk_list(lst, n):
    """Разбивает список lst на подсписки длиной не более n."""
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def register_user_handlers(application):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAVIGATE_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, navigate_menu)
            ],
        },
        fallbacks=[],
    )
    application.add_handler(conv_handler)
