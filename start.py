import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ✅ Завантаження змінної середовища з Railway
creds_json = os.getenv("SERVICE_ACCOUNT_JSON")
if not creds_json:
    raise ValueError("❌ Змінна SERVICE_ACCOUNT_JSON не знайдена")

print("✅ Таблиця знайдена:", creds_json)
