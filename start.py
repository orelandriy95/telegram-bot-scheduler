import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Ініціалізація Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(os.environ["GOOGLE_SHEET_ID"]).sheet1

# Telegram токен
TOKEN = os.environ["BOT_TOKEN"]

# Логування
logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Записатись", callback_data="register")],
        [InlineKeyboardButton("Мої записи", callback_data="my_bookings")]
    ]
    await update.message.reply_text("Привіт! Обери дію:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "register":
        await query.edit_message_text("⏰ Обери час (лише парні години з 8:00 до 18:00):")
        hours = [str(h) + ":00" for h in range(8, 20, 2)]
        buttons = [[InlineKeyboardButton(hour, callback_data=f"book:{hour}")] for hour in hours]
        await query.message.reply_text("Доступні години:", reply_markup=InlineKeyboardMarkup(buttons))

    elif query.data.startswith("book:"):
        hour = query.data.split(":")[1]
        user = query.from_user
        sheet.append_row([user.full_name, hour])
        await query.message.reply_text(f"✅ Записано: {user.full_name} на {hour}")

    elif query.data == "my_bookings":
        user = query.from_user.full_name
        records = sheet.get_all_records()
        user_records = []
            for r in records:
                if r["Прізвище Ім'я"] == user:
                    user_records.append(f"{r['Прізвище Ім\'я']} — {r['Час']}")    
        msg = "\n".join(user_records) if user_records else "Немає записів"
        await query.message.reply_text(f"📋 Твої записи:\n{msg}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
