from src.libs import *

class AlarmManager:
    def __init__(self):
        pygame.mixer.init()
        self.alarm_path = os.path.join("data", "alarms", "mixkit-digital-quick-tone-2866.wav")
        self.thread_running = False  # Flag pentru sunet
        self.popups_people_diff = {}  # Popups pentru people_diff {(table_id, status): popup}
        self.popups_time_diff = {}    # Popups pentru time_diff {(table_id, status): popup}
        self.update_interval = 1  # Secunde pentru actualizarea time_diff

    def play_alarm_sound(self):
        """Redă sunetul alarmei într-un thread separat, evitând suprapunerea."""
        if not self.thread_running:
            self.thread_running = True
            threading.Thread(target=self._play_sound, daemon=True).start()

    def _play_sound(self):
        """Funcție de redare a sunetului într-un thread."""
        try:
            if os.path.exists(self.alarm_path):
                pygame.mixer.music.load(self.alarm_path)
                pygame.mixer.music.play()
                pygame.time.delay(5000)
                pygame.mixer.music.stop()
            else:
                print(f"Fișierul audio {self.alarm_path} nu a fost găsit!")
        finally:
            self.thread_running = False  

    def format_time(self, seconds):
        """Transformă secundele în format hh:mm:ss."""
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    def popup(self, people_diff, time_diff, table_id, status):
        """Afișează un pop-up și actualizează time_diff la fiecare 5 secunde."""
        new_people_message = None
        new_time_message = None

        # Verificăm și generăm mesajul pentru people_diff
        if people_diff > 0:
            new_people_message = f"Numărul de persoane maxim suportat a fost depășit cu {people_diff} persoane"

        # Verificăm și generăm mesajul pentru time_diff doar dacă table_id > 0 și time_diff > 0
        if table_id > 0 and time_diff > 0:
            time_str = self.format_time(time_diff)
            new_time_message = f"Masa {table_id} a depășit timpul de {status} cu {time_str}"

        if not new_people_message and not new_time_message:
            return  

        # Dacă există deja un popup pentru people_diff, nu îl înlocuim cu unul de time_diff și vice-versa
        if new_people_message:
            if (table_id, status) in self.popups_people_diff:
                return  # Dacă există un popup de people_diff pentru acest table_id și status, nu deschidem altul
            # Creăm un nou popup pentru people_diff
            self.create_popup(table_id, status, new_people_message, self.popups_people_diff)

        if new_time_message:
            if (table_id, status) in self.popups_time_diff:
                # Actualizăm doar dacă a trecut intervalul de 5 secunde
                last_time_diff = self.popups_time_diff[(table_id, status)][1]
                if int(time.time()) - last_time_diff >= self.update_interval:
                    self.update_time_popup(table_id, status, new_time_message)
                return  # Dacă există un popup de time_diff deja activ, nu deschidem altul
            # Creăm un nou popup pentru time_diff
            self.create_popup(table_id, status, new_time_message, self.popups_time_diff)

    def create_popup(self, table_id, status, message, popup_dict):
        """Crează și afișează un popup, actualizând dictionarul pentru popups."""
        popup = tk.Toplevel()
        popup.title("Alertă")
        popup.geometry("800x150")
        popup.resizable(False, False)

        label = tk.Label(popup, text=message, font=("Arial", 12), fg="red")
        label.pack(pady=20)

        popup.protocol("WM_DELETE_WINDOW", lambda: self.close_popup(table_id, status, popup_dict))

        popup_dict[(table_id, status)] = (popup, int(time.time()))  # Stocăm timpul pentru actualizări

        print(message)

    def update_time_popup(self, table_id, status, message):
        """Actualizează un popup de time_diff existent."""
        popup, _ = self.popups_time_diff[(table_id, status)]
        label = popup.winfo_children()[0]  # Accesăm label-ul din popup
        label.config(text=message)

        # Actualizăm timpul pop-up-ului
        self.popups_time_diff[(table_id, status)] = (popup, int(time.time()))

        print(f"[Actualizare] {message}")

    def close_popup(self, table_id, status, popup_dict):
        """Închide pop-up-ul specificat de (table_id, status), dacă există."""
        if (table_id, status) in popup_dict:
            popup, _ = popup_dict.pop((table_id, status))
            popup.destroy()
