import os
import re
from datetime import datetime

# Verifică folderele din 'daily_report'
daily_report_dir = 'data/outputs/daily_report'
valid_date_format = re.compile(r"\d{4}-\d{2}-\d{2}")  # Expresie regulată pentru validarea datei

valid_folders = []

for folder_name in os.listdir(daily_report_dir):
    folder_path = os.path.join(daily_report_dir, folder_name)
    if os.path.isdir(folder_path) and valid_date_format.match(folder_name):
        try:
            folder_date = datetime.strptime(folder_name, "%Y-%m-%d")
            valid_folders.append(folder_date)
            print(folder_date)
        except ValueError:
            continue  # Dacă data nu este validă, o să o sărim