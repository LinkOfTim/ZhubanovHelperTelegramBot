import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters

from config import ADMIN_ID, MENU_FILE
from menu import MenuManager

menu_manager = MenuManager(MENU_FILE)

# Состояния для администратора
(
    ADMIN_MENU,
    SELECT_PATH,
    ADD_MENU_ITEM,
    ADD_MENU_RESPONSE,
    DELETE_MENU_ITEM,
) = range(5)

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("У вас нет доступа к этой команде.")
        return ConversationHandler.END

    reply_keyboard = [
        ['Добавить пункт меню', 'Удалить пункт меню'],
        ['Отмена']
    ]
    await update.message.reply_text(
        "Админ-меню:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return ADMIN_MENU

async def admin_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == 'Добавить пункт меню':
        context.user_data['action'] = 'add'
        context.user_data['current_path'] = []
        return await select_path(update, context)
    elif choice == 'Удалить пункт меню':
        context.user_data['action'] = 'delete'
        context.user_data['current_path'] = []
        return await select_path(update, context)
    elif choice == 'Отмена':
        await update.message.reply_text("Выход из админ-меню.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        await update.message.reply_text("Неверный выбор.")
        return ADMIN_MENU

async def select_path(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    current_path = context.user_data['current_path']
    menu_items = menu_manager.get_menu(current_path)
    #if not menu_items:
    #    await update.message.reply_text("Нет доступных пунктов меню.")
    #    return await admin(update, context)

    reply_keyboard = [list(menu_items.keys())]
    reply_keyboard.append(['Выбрать здесь', 'Назад', 'Отмена'])

    await update.message.reply_text(
        "Выберите место в меню:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return SELECT_PATH

async def handle_select_path(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text
    if choice == 'Выбрать здесь':
        if context.user_data['action'] == 'add':
            await update.message.reply_text("Введите название нового пункта меню:", reply_markup=ReplyKeyboardRemove())
            return ADD_MENU_ITEM
        elif context.user_data['action'] == 'delete':
            current_path = context.user_data['current_path']
            menu_items = menu_manager.get_menu(current_path)
            if not menu_items:
                await update.message.reply_text("Нет пунктов для удаления.")
                return await admin(update, context)
            reply_keyboard = [list(menu_items.keys())]
            await update.message.reply_text(
                "Выберите пункт меню для удаления:",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
            )
            return DELETE_MENU_ITEM
    elif choice == 'Назад':
        if context.user_data['current_path']:
            context.user_data['current_path'].pop()
        else:
            return await admin(update, context)
    elif choice == 'Отмена':
        await update.message.reply_text("Действие отменено.", reply_markup=ReplyKeyboardRemove())
        return await admin(update, context)
    else:
        current_path = context.user_data['current_path']
        menu_items = menu_manager.get_menu(current_path)
        if choice in menu_items:
            context.user_data['current_path'].append(choice)
        else:
            await update.message.reply_text("Пункт меню не найден.")
    return await select_path(update, context)

async def add_menu_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    menu_item_name = update.message.text
    context.user_data['new_menu_item'] = menu_item_name
    await update.message.reply_text("Введите ответ бота для этого пункта меню (или отправьте '-' для создания подменю):")
    return ADD_MENU_RESPONSE

async def add_menu_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    response = update.message.text
    menu_item_name = context.user_data['new_menu_item']
    current_path = context.user_data['current_path']

    if response.strip() == '-':
        menu_manager.add_menu_item(current_path, menu_item_name)
        await update.message.reply_text(f"Подменю '{menu_item_name}' успешно добавлено.")
    else:
        menu_manager.add_menu_item(current_path, menu_item_name, response)
        await update.message.reply_text(f"Пункт меню '{menu_item_name}' успешно добавлен с ответом.")
    return await admin(update, context)

async def delete_menu_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    menu_item_name = update.message.text
    current_path = context.user_data['current_path']
    success = menu_manager.delete_menu_item(current_path, menu_item_name)
    if success:
        await update.message.reply_text(f"Пункт меню '{menu_item_name}' успешно удален.")
    else:
        await update.message.reply_text("Пункт меню не найден.")
    return await admin(update, context)

def register_admin_handlers(application):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('admin', admin)],
        states={
            ADMIN_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_choice)
            ],
            SELECT_PATH: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_select_path)
            ],
            ADD_MENU_ITEM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_menu_item)
            ],
            ADD_MENU_RESPONSE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_menu_response)
            ],
            DELETE_MENU_ITEM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, delete_menu_item)
            ],
        },
        fallbacks=[],
    )
    application.add_handler(conv_handler)
