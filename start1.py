import base64
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 🔐 Вшитий base64-ключ
CREDENTIALS_BASE64 = "ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAidGctYm90LXNjaGVkdWxlci0xOTk1IiwKICAicHJpdmF0ZV9rZXlfaWQiOiAiZmZlNDljZmQxMGNhYzNhZmI2MzZhMzJhM2E3NWViY2Q2MjU0NTgzYiIsCiAgInByaXZhdGVfa2V5IjogIi0tLS0tQkVHSU4gUFJJVkFURSBLRVktLS0tLVxuTUlJRXZRSUJBREFOQmdrcWhraUc5dzBCQVFFRkFBU0NCS2N3Z2dTakFnRUFBb0lCQVFDdFFVZEt0RnE3ZUtlMFxuWUhpZFNGKy91ODZxK1k4Snh1R2ZLM3RTcTQ1aXpMYUFQRmhrYk5MWHkxalQrc2U1ZWl5R1huUVo3YkdjQUlwMVxud1BTbDFZeTlHUFdyS1gvRHREVjdQUGdyMTlpNzhvWlZ4cjhhZzdiWE9MdDAxMmdXaDJzd1grSGlvcDRzZjZKWVxudEM3czU2R1pDa0JGN1l1STlnRUUrQzhQQXU2M2o4T2JBNVRTWmpUZEhTYk4wYW8yblFjcDdOT3RSVWRpSFdjRVxuZWVwaEc3Q0h2cUVGamprOWVGWERsdmNONFAzWDMrWXRKeVJkdGNNenp5SEQrMDBieGhjOEdLK3l5dmNUN0dVYlxuUEl5dlRvcnhyaWJmak5zZ0xIa1FYOFdvSVp6Z2tKcmJ5ZlBQbXFzYzNpdldLeWp3QWZ2REp6cm1JRk5CSDhycVxudnh1Q1J0TjlBZ01CQUFFQ2dnRUFVRnBWTVMyQ1l5NHJRWG40bHFHcFhxaEF5b1VodE53YmFoSGxpVXJ0cDU3Z1xuQ1l0elIyZzlSVDRYUFlFeXZqQU9sR2NjRzZaazJFQmI5dzc5cUNmcHRRM3RhbXU5eU1zOGZxS2hTdHc1dGJsZVxuV2t2cDkrY2NscWJHTWdOeFQvbVFXZ2d1SUVsaGFLdnRaSXgwc3dVZXFuYlpwbFRzZ1NIdkNSbjk0VTF2MzR1MVxuSFNCRnN3TEJ5VDFlWHpkdXFETFlMdlVFV3ZmOTNRSGhDZTJHY0VycnpLWWw3YVhhVnRZWVJySlpUOFh5aTZ1aFxuZDVweXJvL0VtekJrQ3ovU2xadDduUDVSc2k5d3VQcXVVa0xxdlVvTjR4a0N6NVFoSTd0L3k3MnVjdUNaZkVrdlxuMFJYS2gzbU40NGI1V3M0ZkNBVFRFT3JRSEd6dEcvNkQ2TXRZc3JzSmRRS0JnUUQwWkkvTGRxWHFRNUlRMzE2bFxuZnA2VXhIRm9pVTRFZy9McDFodFhqTU1mVGVxVnJUcERUUFNlbmR3UE4yZDhoNFRNUFRLTVVYeU5OQ2tsVTFodVxudG1rMHhCa0k5VmQ1ZG16MStGcEhiVDJUa3hBTndvcHNPcndnbllWRmM4VTVrZ2VWUGdRMWt2QngraDZpNWJUVFxuaEdjM0kvQUxmNmZpN2pCa2J4TTMxN0NxR3dLQmdRQzFlOHA5RlJtU0trNk9qNk81K1FMTVRKZVVuTm1tT2pNN1xuS01XdGppOGNmSEVaNEIzSnBnWFhWTTVuU3lQYXpBNENkQjc5ZGxXQUgvY2VFdVZGeTJxODJhSFJ6dUpxTzA0OFxuYzFVK3g0djdvVXlDdmhqNVdHNzFzN1BJQUVqWVJTZkl0aHV3WE93VFBoU0VzQlhsN0VSV0ZvbUtIY2pWdU96MVxuYU1UelNoRlNSd0tCZ0NzUVBUWkE1ZU50bktOVWVMejRuc0RnREl1N0JnQk5yOVA4WWp6L0ZMTERhLzZMMDZSZ1xuUHdwa0RvNnYySkJjNE0yTVN3Zm1vK2ZOdFNKYW1VNkkzZWpxVk83N0xEcSszMXhJTXNBN1E0cHBjMzY1Tk9MMVxuUm9rSXVKOFFVMFJkc3ZCZFNTaVhoNzdOci9CTVFaeXp5K3d2YlBEWndaOS9FUS9oY3FWNFlDelpBb0dCQUtUTlxuVWphK0IyZUZCYXRONHZjSm1qSGR4N1NMcnRYVmVocFp6eERvMGYxRFFBMm9TRVNLZ0RsbmFMdkNMMEFNRnhqQlxuVERjTTAxMnpLVnZrK3RDamhUMFRRSEJmTjVvU1d0eG9PMXYwSnprTTQ0YkNpN2s2UmlEVzNBWmR3OGlwSEJTV1xuMHBRWC9jVUhsZWhjWXJaVkZFVTgyQTlWTnNCbDJzQ01NSFZocUZNWEFvR0FLUGR2RVU0WTVNMWxoZk9ZZjg3OVxuY09aMHR1MXRHZDJDS3RXdkNUUVBpRVk3Vm80SS85NWE4NFZQd2lvNnlrek1VWmttUVRIMXhwY1JFQ0NpOXhSdFxudU03UmdHTi82VVU2RUFYeUMxWmtiVjdyWFBsNWtCOGtmTWZsYS9KOGtmcWdvdWw4blhRNlZwWkpQMFVYeWVzalxuWHJjWFBlYUgyeE9obVVvdjhnZjFJZTg9XG4tLS0tLUVORCBQUklWQVRFIEtFWS0tLS0tXG4iLAogICJjbGllbnRfZW1haWwiOiAidGVsZWdyYW0tYm90LWdzaGVldHNAdGctYm90LXNjaGVkdWxlci0xOTk1LmlhbS5nc2VydmljZWFjY291bnQuY29tIiwKICAiY2xpZW50X2lkIjogIjEwNTg3OTY3Njg3ODAyODg0Mzg1MCIsCiAgImF1dGhfdXJpIjogImh0dHBzOi8vYWNjb3VudHMuZ29vZ2xlLmNvbS9vL29hdXRoMi9hdXRoIiwKICAidG9rZW5fdXJpIjogImh0dHBzOi8vb2F1dGgyLmdvb2dsZWFwaXMuY29tL3Rva2VuIiwKICAiYXV0aF9wcm92aWRlcl94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL29hdXRoMi92MS9jZXJ0cyIsCiAgImNsaWVudF94NTA5X2NlcnRfdXJsIjogImh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL3JvYm90L3YxL21ldGFkYXRhL3g1MDkvdGVsZWdyYW0tYm90LWdzaGVldHMlNDB0Zy1ib3Qtc2NoZWR1bGVyLTE5OTUuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJ1bml2ZXJzZV9kb21haW4iOiAiZ29vZ2xlYXBpcy5jb20iCn0K"

# 📥 Декодуємо та завантажуємо
creds_json = base64.b64decode(CREDENTIALS_BASE64).decode("utf-8")
creds_dict = json.loads(creds_json)

# 🔑 Авторизація до Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# 📄 Таблиця
sheet = client.open_by_key("ТУТ_ID_ТАБЛИЦІ").sheet1

#sheet = client.open_by_key(os.getenv('1Ug6Mze38Jr6uVLv9Tm74t2j42PkCFplELt7qjPFCg7I')).sheet1
sheet = client.open_by_key("1Ug6Mze38Jr6uVLv9Tm74t2j42PkCFplELt7qjPFCg7I").sheet1

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
