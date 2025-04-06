import os
import re
import argparse
from datetime import datetime

def find_valid_date_folders(directory):
    """
    Caută subfoldere valide în format YYYY-MM-DD din directorul dat.
    Returnează o listă cu obiecte datetime corespunzătoare.
    """
    valid_date_format = re.compile(r"\d{4}-\d{2}-\d{2}")
    valid_folders = []

    if not os.path.exists(directory):
        print(f"[Eroare] Directorul nu există: {directory}")
        return []

    for folder_name in os.listdir(directory):
        folder_path = os.path.join(directory, folder_name)
        if os.path.isdir(folder_path) and valid_date_format.fullmatch(folder_name):
            try:
                folder_date = datetime.strptime(folder_name, "%Y-%m-%d")
                valid_folders.append(folder_date)
            except ValueError:
                continue

    return sorted(valid_folders)

def save_to_log(output_list, log_path):
    with open(log_path, "w") as f:
        for item in output_list:
            f.write(f"{item.strftime('%Y-%m-%d')}\n")
    print(f"[✓] Log salvat în: {log_path}")

def main():
    parser = argparse.ArgumentParser(description="Verifică folderele de tip YYYY-MM-DD din daily_report.")
    parser.add_argument(
        "--input_dir",
        type=str,
        default="data/outputs/daily_report",
        help="Calea către directorul de analizat"
    )
    parser.add_argument(
        "--log_file",
        type=str,
        default="scripts/report_folder_log.txt",
        help="Fișierul în care se salvează rezultatele"
    )

    args = parser.parse_args()
    valid_dates = find_valid_date_folders(args.input_dir)

    print(f"[INFO] {len(valid_dates)} foldere valide găsite:")
    for d in valid_dates:
        print("  -", d.strftime("%Y-%m-%d"))

    save_to_log(valid_dates, args.log_file)

if __name__ == "__main__":
    main()