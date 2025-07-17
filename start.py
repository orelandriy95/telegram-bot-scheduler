import logging
import os
import datetime
from datetime import datetime as dt
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (Application, CallbackContext, CallbackQueryHandler,
                          CommandHandler, ContextTypes, MessageHandler, filters)
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Авторизація до Google Sheets через credentials.json
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(os.getenv('1Ug6Mze38Jr6uVLv9Tm74t2j42PkCFplELt7qjPFCg7I')).sheet1

# Обробник стартової команди
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Записатись", callback_data="choose_date")],
        [InlineKeyboardButton("Мої записи", callback_data="my_bookings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Вітаю! Оберіть дію:", reply_markup=reply_markup)

# Обробник натискання кнопок
async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == "choose_date":
        days = [(dt.now() + datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
        keyboard = [[InlineKeyboardButton(day, callback_data=f"day_{day}")] for day in days]
        await query.message.reply_text("Оберіть дату:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("day_"):
        date = query.data.split("_")[1]
        hours = [f"{h:02}:00" for h in range(8, 20, 2)]
        records = sheet.get_all_records()
        booked_hours = [r["Час"] for r in records if r.get("Дата") == date]
        free_hours = [h for h in hours if h not in booked_hours]
        keyboard = [[InlineKeyboardButton(hour, callback_data=f"book_{date}_{hour}")] for hour in free_hours]
        keyboard.append([InlineKeyboardButton("Назад", callback_data="choose_date")])
        await query.message.reply_text(f"Оберіть годину для {date}:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("book_"):
        _, date, hour = query.data.split("_")
        user = query.from_user.full_name
        sheet.append_row([user, date, hour])
        await query.message.reply_text(f"✅ Записано: {user}, {date} на {hour}")

    elif query.data == "my_bookings":
        user = query.from_user.full_name
        records = sheet.get_all_records()
        user_records = []
        for r in records:
            if r.get("Прізвище Ім'я") == user:
                name = r.get("Прізвище Ім'я", "")
                time = r.get("Час", "")
                user_records.append(f"{name} — {time}")

        if user_records:
            msg = "📋 Твої записи:\n" + "\n".join(user_records)
        else:
            msg = "ℹ️ У вас немає записів."

        await query.message.reply_text(msg)

# Головна функція запуску
if __name__ == "__main__":
    TOKEN = os.getenv("BOT_TOKEN")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    logger.info("Бот запущено")
    app.run_polling()
