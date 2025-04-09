from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Хранилище заметок
notes = []

# Команда /start с Reply Keyboard
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["/list", "/list_buttons"],  # Первая строка кнопок
        ["/delete", "/clear"],       # Вторая строка кнопок
        ["/search", "/help"]         # Третья строка кнопок
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! Я твой бот для заметок. Вот список доступных команд. Выберите одну из кнопок ниже:",
        reply_markup=reply_markup
    )

# Команда /help - показывает список всех команд
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📚 Доступные команды:

/start - Начать работу с ботом  
/list - Показать все заметки  
/list_buttons - Показать заметки с кнопками удаления  
/delete [номер] - Удалить конкретную заметку (пример: /delete 1)  
/clear - Удалить все заметки  
/search [текст] - Поиск заметок (пример: /search покупки)  
/help - Показать это сообщение  

💡 Как использовать:  
Просто отправляйте мне текст, и я сохраню его как заметку!
    """
    await update.message.reply_text(help_text)

# Команда /menu с Inline Keyboard
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Список заметок", callback_data="list_notes")],
        [InlineKeyboardButton("Очистить заметки", callback_data="clear_notes")],
        [InlineKeyboardButton("Помощь", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

# Обработка нажатий на Inline Keyboard
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "list_notes":
        if not notes:
            await query.edit_message_text("Заметок пока нет.")
        else:
            response = "\n\n".join([f"{i+1}. {n}" for i, n in enumerate(notes)])
            await query.edit_message_text(f"Список заметок:\n\n{response}")
    elif query.data == "clear_notes":
        notes.clear()
        await query.edit_message_text("Все заметки очищены!")
    elif query.data == "help":
        help_text = """
📚 Доступные команды:

/start - Начать работу с ботом  
/list - Показать все заметки  
/list_buttons - Показать заметки с кнопками удаления  
/delete [номер] - Удалить конкретную заметку (пример: /delete 1)  
/clear - Удалить все заметки  
/search [текст] - Поиск заметок (пример: /search покупки)  
/help - Показать это сообщение  

💡 Как использовать:  
Просто отправляйте мне текст, и я сохраню его как заметку!
        """
        await query.edit_message_text(help_text)

# Сохранение заметки
async def save_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    notes.append(text)
    await update.message.reply_text(f"Заметка сохранена! Сейчас у тебя {len(notes)} заметок.")

# Просмотр всех заметок
async def list_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not notes:
        await update.message.reply_text("Заметок пока нет.")
    else:
        response = "\n\n".join([f"{i+1}. {n}" for i, n in enumerate(notes)])
        await update.message.reply_text(response)

# Удаление конкретной заметки
async def delete_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        note_index = int(context.args[0]) - 1
        if 0 <= note_index < len(notes):
            deleted_note = notes.pop(note_index)
            await update.message.reply_text(f"Заметка удалена: {deleted_note}")
        else:
            await update.message.reply_text("Неверный номер заметки.")
    except (IndexError, ValueError):
        await update.message.reply_text("Пожалуйста, укажите номер заметки для удаления. Например: /delete 1")

# Очистка всех заметок
async def clear_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    notes.clear()
    await update.message.reply_text("Все заметки удалены!")

# Поиск по ключевым словам
async def search_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Пожалуйста, укажите текст для поиска. Например: /search ключевое_слово")
        return
    
    matching_notes = [f"{i+1}. {note}" for i, note in enumerate(notes) if query.lower() in note.lower()]
    if matching_notes:
        response = "\n\n".join(matching_notes)
        await update.message.reply_text(f"Найдено:\n\n{response}")
    else:
        await update.message.reply_text("Нет совпадений.")

# Создание приложения и регистрация обработчиков
app = ApplicationBuilder().token("7022082873:AAF5F-IjhfnYwDZ14uT7IaYXDWxLV3xFDt0").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("menu", menu))
app.add_handler(CommandHandler("list", list_notes))
app.add_handler(CommandHandler("delete", delete_note))
app.add_handler(CommandHandler("clear", clear_notes))
app.add_handler(CommandHandler("search", search_notes))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_note))
app.add_handler(CallbackQueryHandler(handle_callback))

# Запуск бота
if __name__ == "__main__":
    app.run_polling()

