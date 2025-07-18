import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ✅ Завантаження змінної середовища з Railway
creds_json = os.getenv("SERVICE_ACCOUNT_JSON")
if not creds_json:
    raise ValueError("❌ Змінна SERVICE_ACCOUNT_JSON не знайдена")

# 📦 Перетворення JSON-стрічки в словник
creds_dict = json.loads(creds_json)

# 🔐 Авторизація Google API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# 📄 Отримання таблиці
spreadsheet_id = os.getenv("GOOGLE_SHEET_ID")
sheet = client.open_by_key(spreadsheet_id).sheet1

# 📊 Вивід інформації
print("✅ Таблиця знайдена:", sheet.title)
print("📈 Рядків у таблиці:", len(sheet.get_all_records()))
