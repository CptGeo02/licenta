import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import os
import json
from datetime import datetime
from src.libs import *
from src.utils.json_to_excel import JsonToExcel

class ScheduleFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.schedule_data = {}
        self.create_widgets()
        self.stop_event = threading.Event()  # Eveniment pentru a opri threadul
        self.thread = None

    def create_widgets(self):
        # Header Row

        tk.Label(self, text="Day of Week", width=15, anchor="w").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(self, text="Workday Length", width=15, anchor="w").grid(row=0, column=1, padx=5, pady=5)
        tk.Label(self, text="Start Time", width=10, anchor="w").grid(row=0, column=2, padx=5, pady=5)
        tk.Label(self, text="End Time", width=10, anchor="w").grid(row=0, column=3, padx=5, pady=5)

        self.entries = []

        # Rows for each day
        for i, day in enumerate(self.days):
            var_open = tk.BooleanVar(value=True)
            self.schedule_data[day] = {
                "is_open": var_open,
                "work_length": tk.StringVar(value="8 h"),
                "start_time": tk.StringVar(value="09:00"),
                "end_time": tk.StringVar(value="17:00"),
            }

            # Checkbox for Open/Closed
            checkbox = tk.Checkbutton(self, text=day, variable=var_open, command=lambda d=day: self.toggle_day(d))
            checkbox.grid(row=i + 1, column=0, sticky="w", padx=5, pady=5)

            # Workday Length Entry
            work_length = ttk.Entry(self, textvariable=self.schedule_data[day]["work_length"], width=10)
            work_length.grid(row=i + 1, column=1, padx=5, pady=5)
            work_length.bind("<Return>", lambda e, d=day: self.update_end_time(d))  # Update End Time

            # Start Time Entry
            start_time = ttk.Entry(self, textvariable=self.schedule_data[day]["start_time"], width=10)
            start_time.grid(row=i + 1, column=2, padx=5, pady=5)

            # End Time Entry
            end_time = ttk.Entry(self, textvariable=self.schedule_data[day]["end_time"], width=10)
            end_time.grid(row=i + 1, column=3, padx=5, pady=5)
            end_time.bind("<Return>", lambda e, d=day: self.update_work_length(d))  # Update Workday Length

            # Add to entries list for toggling
            self.entries.append((work_length, start_time, end_time))

        # Submit Button
        set_schedule_button = ttk.Button(self, text="Set Schedule", command=self.submit_schedule)
        set_schedule_button.grid(row=len(self.days) + 1, column=0, columnspan=4, pady=10)

    def toggle_day(self, day):
        """Enable or disable widgets based on the 'is_open' checkbox."""
        data = self.schedule_data[day]
        index = self.days.index(day)
        state = "normal" if data["is_open"].get() else "disabled"
        for widget in self.entries[index]:
            widget.config(state=state)

    def update_end_time(self, day):
        """Update End Time based on Workday Length and Start Time."""
        try:
            start_time = self.schedule_data[day]["start_time"].get()
            work_length = self.schedule_data[day]["work_length"].get()

            # Parse Start Time
            start_time_obj = datetime.strptime(start_time, "%H:%M")

            # Extract hours from Work Length
            work_hours = int(work_length.replace("h", "").strip())

            # Calculate End Time
            end_time_obj = start_time_obj + timedelta(hours=work_hours)
            self.schedule_data[day]["end_time"].set(end_time_obj.strftime("%H:%M"))

        except Exception as e:
            print(f"Error updating end time for {day}: {e}")

    def update_work_length(self, day):
        """Update Workday Length based on Start Time and End Time."""
        try:
            start_time = self.schedule_data[day]["start_time"].get()
            end_time = self.schedule_data[day]["end_time"].get()

            # Parse Start and End Times
            start_time_obj = datetime.strptime(start_time, "%H:%M")
            end_time_obj = datetime.strptime(end_time, "%H:%M")

            # Calculate Work Length
            duration = end_time_obj - start_time_obj
            hours = duration.total_seconds() // 3600
            self.schedule_data[day]["work_length"].set(f"{int(hours)} h")

        except Exception as e:
            print(f"Error updating work length for {day}: {e}")

    def submit_schedule(self):
        """Print the schedule to the console."""
        for day, data in self.schedule_data.items():
            if data["is_open"].get():
                print(f"{day}: Open, Workday Length: {data['work_length'].get()}, "
                      f"Start Time: {data['start_time'].get()}, End Time: {data['end_time'].get()}")
            else:
                print(f"{day}: Closed")
        self.start_checking_schedule()

    def check_time(self):
        """
        Verifică dacă timpul curent a depășit end_time pentru ziua curentă și generează rapoartele JSON.
        
        Args:
            schedule_frame (ScheduleFrame): Instanță din care se iau datele end_time și is_open pentru ziua curentă.
        """
        # Obține ziua curentă
        current_day = datetime.now().strftime("%A")
        current_time = datetime.now().strftime("%H:%M")
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Verifică dacă ziua curentă este deschisă în program
        if not self.schedule_data[current_day]["is_open"].get():
            print(f"{current_day} este închisă.")
            return
        
        # Obține end_time pentru ziua curentă
        start_time = self.schedule_data[current_day]["start_time"].get()
        end_time = self.schedule_data[current_day]["end_time"].get()
        
        # Compară timpul curent cu end_time
        if current_time < end_time:
            print(f"Timpul curent ({current_time}) nu a depășit end_time ({end_time}) pentru {current_day}.")
            return
        self.generate_reports(start_time, end_time, current_day, current_date)

    def generate_reports(self, start_time, end_time, current_day, current_date):
        print(f"Timpul curent a depășit end_time ({end_time}) pentru {current_day}. Generăm rapoarte...")
        
        # Calea de ieșire pentru rapoartele zilnice
        daily_report_path = os.path.join("data", "outputs", "daily_report", current_date)
        os.makedirs(daily_report_path, exist_ok=True)

        # Concatenare fișiere table_records    
        table_records_path = os.path.join("data", "outputs", "table_records")
        self.generate_concatenated_json(
            source_folder=table_records_path,
            target_file=os.path.join(daily_report_path, "table_status_report.json"),
            start_time = start_time,
            end_time = end_time,
        )
        
        # Concatenare fișiere people_records
        people_records_path = os.path.join("data", "outputs", "people_records")
        self.generate_concatenated_json(
            source_folder=people_records_path,
            target_file=os.path.join(daily_report_path, "people_detected.json"),
            start_time = start_time,
            end_time = end_time,
        )


        table_records_path = os.path.join("data", "outputs", "daily_report", current_date, "table_status_report.json")
        people_records_path = os.path.join("data", "outputs", "daily_report", current_date, "people_detected.json")
        excel_file = os.path.join("data", "outputs", "daily_report", current_date, "table_status_analysis.xlsx")
        try:
            analyzer = JsonToExcel(table_records_path, people_records_path, excel_file)
            analyzer.save_to_excel()
            print(f"Fișierul Excel a fost generat cu succes: {excel_file}")
            analyzer.save_average_statistics()
        except Exception as e:
            print(f"Eroare la generarea fișierului table_status_analysis.xlsx: {e}")
        self.stop_checking_schedule()
        
    def generate_concatenated_json(self, source_folder, target_file, start_time, end_time):
        """
        Concatenează toate fișierele JSON dintr-un folder care conțin data curentă în numele fișierului
        și le filtrează în funcție de un interval orar specificat.

        Args:
            source_folder (str): Calea către folderul sursă.
            target_file (str): Calea către fișierul JSON rezultat.
            start_time (str): Ora de început a intervalului (format: HH:MM).
            end_time (str): Ora de sfârșit a intervalului (format: HH:MM).
        """
        all_data = {}
        start_time_dt = datetime.strptime(start_time, "%H:%M").time()
        end_time_dt = datetime.strptime(end_time, "%H:%M").time()

        # Obține data curentă în formatul YYYY-MM-DD
        today = datetime.today().strftime('%Y-%m-%d')

        for filename in os.listdir(source_folder):
            if filename.endswith(".json") and today in filename:
                filepath = os.path.join(source_folder, filename)
                try:
                    with open(filepath, "r") as file:
                        data = json.load(file)

                        if "people_detected" in filename:
                            # Filtrare pe baza câmpului "time" (format complet: YYYY-MM-DD HH:MM:SS)
                            for key, value in data.items():
                                if isinstance(value, list):
                                    filtered_list = [
                                        item for item in value
                                        if "time" in item
                                        # Convertim "time" din formatul complet la un obiect de tip datetime
                                        and start_time_dt <= datetime.strptime(item["time"], "%Y-%m-%d %H:%M:%S").time() <= end_time_dt
                                    ]
                                    if filtered_list:
                                        if key in all_data:
                                            all_data[key].extend(filtered_list)
                                        else:
                                            all_data[key] = filtered_list

                        elif "table_status_report" in filename:
                            # Filtrare pe baza câmpului "start_time" (format complet: YYYY-MM-DD HH:MM:SS)
                            for key, value in data.items():
                                if isinstance(value, list):
                                    filtered_list = [
                                        item for item in value
                                        if "start_time" in item
                                        # Convertim "start_time" din formatul complet la un obiect de tip datetime
                                        and start_time_dt <= datetime.strptime(item["start_time"], "%Y-%m-%d %H:%M:%S").time() <= end_time_dt
                                    ]
                                    if filtered_list:
                                        if key in all_data:
                                            all_data[key].extend(filtered_list)
                                        else:
                                            all_data[key] = filtered_list

                        else:
                            # Pentru alte fișiere, adaugă datele așa cum sunt
                            for key, value in data.items():
                                if key in all_data:
                                    if isinstance(value, list) and isinstance(all_data[key], list):
                                        all_data[key].extend(value)
                                    else:
                                        print(f"Avertisment: Structura pentru cheia '{key}' nu este o listă. Se omite.")
                                else:
                                    all_data[key] = value

                except Exception as e:
                    print(f"Eroare la citirea fișierului {filepath}: {e}")

        # Scrie datele filtrate într-un singur fișier JSON
        try:
            with open(target_file, "w") as outfile:
                json.dump(all_data, outfile, indent=4)
            print(f"Fișierul rezultat a fost salvat: {target_file}")
        except Exception as e:
            print(f"Eroare la scrierea fișierului {target_file}: {e}")

    def start_checking_schedule(self):
        """Pornește thread-ul care verifică programul."""
        if self.thread and self.thread.is_alive():
            print("Thread-ul este deja pornit.")
            return

        self.stop_event.clear()  # Asigură-te că thread-ul poate rula
        self.thread = threading.Thread(target=self.check_schedule)
        self.thread.daemon = True
        self.thread.start()

    def check_schedule(self):
        """Funcția rulată de thread pentru verificarea programului."""
        while not self.stop_event.is_set():
            self.check_time()
            time.sleep(60)  # Așteaptă o secundă înainte de a relua verificarea

    def stop_checking_schedule(self):
        """Opresc thread-ul de verificare."""
        if self.thread and self.thread.is_alive():
            print("Oprirea thread-ului...")
            self.stop_event.set()  # Semnalează thread-ului să se oprească
            print("Thread-ul a fost oprit.")
        else:
            print("Thread-ul nu este activ.")

# Main Application
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Main GUI")
    root.mainloop()
