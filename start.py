import os
import json
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# Скопіюй цей scope
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# ОТРИМУЄМО І РОЗПАРСЮЄМО ЗМІННУ З Railway
creds_raw = os.getenv("SERVICE_ACCOUNT_JSON")

# ЗАМІНЮЄМО \\n НА СПРАВЖНІ \n
creds_fixed = creds_raw.replace("\\n", "\n")

# ПАРСИМО У JSON
creds_dict = json.loads(creds_fixed)

# Авторизація
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Підключення до Google Sheet
spreadsheet_id = os.getenv("GOOGLE_SHEET_ID")
sheet = client.open_by_key(spreadsheet_id).sheet1
# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📅 Записатись", callback_data="choose_date")],
        [InlineKeyboardButton("📋 Мої записи", callback_data="my_bookings")]
    ]
    await update.message.reply_text("Вітаю! Оберіть дію:", reply_markup=InlineKeyboardMarkup(keyboard))

# Обробка кнопок
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = query.from_user.full_name

    if data == "choose_date":
        today = dt.now().date()
        days = [(today + timedelta(days=i)) for i in range(0, 180)]
        buttons = []
        for day in days:
            label = day.strftime("%d.%m.%Y (%A)")
            buttons.append([InlineKeyboardButton(label, callback_data=f"day_{day}")])
        await query.message.reply_text("🗓 Оберіть дату:", reply_markup=InlineKeyboardMarkup(buttons[:10]))

    elif data.startswith("day_"):
        date_str = data.replace("day_", "")
        context.user_data["selected_date"] = date_str
        hours = [f"{h:02}:00" for h in range(8, 20, 2)]
        booked = [r["Час"] for r in sheet.get_all_records() if r["Дата"] == date_str]
        available = [h for h in hours if h not in booked]
        buttons = [[InlineKeyboardButton(h, callback_data=f"confirm_{h}")] for h in available]
        buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="choose_date")])
        await query.message.reply_text(f"🕓 Години для {date_str}:", reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("confirm_"):
        hour = data.replace("confirm_", "")
        date_str = context.user_data.get("selected_date")
        context.user_data["pending"] = (date_str, hour)
        btns = [
            [InlineKeyboardButton("✅ Так", callback_data="save_booking")],
            [InlineKeyboardButton("❌ Ні", callback_data="choose_date")]
        ]
        await query.message.reply_text(f"Підтвердити запис на {date_str} о {hour}?", reply_markup=InlineKeyboardMarkup(btns))

    elif data == "save_booking":
        date_str, hour = context.user_data.get("pending", (None, None))
        sheet.append_row([user, date_str, hour])
        await query.message.reply_text(f"✅ Записано: {user}, {date_str} на {hour}")

    elif data == "my_bookings":
        records = sheet.get_all_records()
        user_records = [r for r in records if r["Прізвище Ім'я"] == user]
        if not user_records:
            await query.message.reply_text("У вас немає записів.")
            return
        msg = "\n".join([f"{i+1}. {r['Дата']} о {r['Час']}" for i, r in enumerate(user_records)])
        await query.message.reply_text(f"📋 Ваші записи:\n{msg}")

# Запуск бота
async def main():
    app = Application.builder().token(os.environ["BOT_TOKEN"]).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
