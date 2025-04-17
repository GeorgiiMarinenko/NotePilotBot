import os
import aiosqlite
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

DB_PATH = "notes.db"

# Инициализация базы данных
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                text TEXT NOT NULL
            )
        """)
        await db.commit()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["/list", "/list_buttons"],
        ["/delete", "/clear"],
        ["/search", "/help"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! Я твой бот для заметок. Вот список доступных команд. Выберите одну из кнопок:",
        reply_markup=reply_markup
    )

# Команда /help
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

# Сохранение заметки
async def save_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO notes (user_id, text) VALUES (?, ?)", (user_id, text))
        await db.commit()
        cursor = await db.execute("SELECT COUNT(*) FROM notes WHERE user_id = ?", (user_id,))
        count = (await cursor.fetchone())[0]
    await update.message.reply_text(f"Заметка сохранена! Сейчас у тебя {count} заметок.")

# Просмотр всех заметок
async def list_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT id, text FROM notes WHERE user_id = ?", (user_id,))
        notes = await cursor.fetchall()
    if not notes:
        await update.message.reply_text("Заметок пока нет.")
    else:
        response = "\n\n".join([f"{i+1}. {n[1]}" for i, n in enumerate(notes)])
        await update.message.reply_text(response)

# Удаление конкретной заметки
async def delete_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    try:
        note_index = int(context.args[0]) - 1
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("SELECT id FROM notes WHERE user_id = ?", (user_id,))
            notes = await cursor.fetchall()
            if 0 <= note_index < len(notes):
                note_id = notes[note_index][0]
                await db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
                await db.commit()
                await update.message.reply_text("Заметка удалена.")
            else:
                await update.message.reply_text("Неверный номер заметки.")
    except (IndexError, ValueError):
        await update.message.reply_text("Пожалуйста, укажите номер заметки для удаления. Например: /delete 1")

# Очистка всех заметок
async def clear_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM notes WHERE user_id = ?", (user_id,))
        await db.commit()
    await update.message.reply_text("Все заметки удалены!")

# Поиск по ключевым словам
async def search_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Пожалуйста, укажите текст для поиска. Например: /search ключевое_слово")
        return
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT text FROM notes WHERE user_id = ? AND LOWER(text) LIKE ?", (user_id, f"%{query.lower()}%"))
        notes = await cursor.fetchall()
    if notes:
        response = "\n\n".join([f"{i+1}. {n[0]}" for i, n in enumerate(notes)])
        await update.message.reply_text(f"Найдено:\n\n{response}")
    else:
        await update.message.reply_text("Нет совпадений.")

# Inline Keyboard и CallbackQueryHandler можно реализовать аналогично, передавая user_id

# Создание приложения и регистрация обработчиков
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("list", list_notes))
app.add_handler(CommandHandler("delete", delete_note))
app.add_handler(CommandHandler("clear", clear_notes))
app.add_handler(CommandHandler("search", search_notes))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_note))
# Добавьте CallbackQueryHandler при необходимости

# Запуск бота
if __name__ == "__main__":
    import asyncio
    asyncio.run(init_db())
    app.run_polling()
