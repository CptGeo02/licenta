import json
import time
import threading
from datetime import datetime

class PeopleManager:
    def __init__(self):
        self.people_count = 0
        self.json_file_name = None  # Variabila pentru a păstra numele fișierului curent
        self.lock = threading.Lock()
        self.max_people_number = 99999

    def set_max_people_number(self, number):
        """
        Setează numărul maxim de persoane.
        """
        if isinstance(number, int) and number > 0:
            self.max_people_number = number
        else:
            raise ValueError("Number must be a positive integer.")
        
    def set_people_number(self, people_number):
        self.people_count = people_number

    def get_max_people_number(self):
        """
        Returnează numărul maxim de persoane.
        """
        return self.max_people_number 
    
    def create_new_files(self):
        """
        Creează fișierul JSON cu data și ora curentă la începutul fiecărei runde.
        """
        # Obține data și ora curentă pentru denumirea fișierelor
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.json_file_name = f"data/outputs/people_records/people_detected_{now}.json" 
        
        # Creează fișierul JSON gol la începutul fiecărei runde
        with open(self.json_file_name, 'w') as f:
            json.dump({"detections": []}, f, indent=4)
        
        print(f"Fișierul {self.json_file_name} a fost creat.")

    def count_people(self, detections):
        """
        Numără persoanele (clasa 0) detectate în lista de detectări.
        """
        self.people_count = sum(1 for det in detections if det['class'] == 0)  # Clasa 0 este pentru persoane
        return self.people_count
    
    def save_to_json(self):
        """
        Salvează informațiile despre persoanele detectate într-un fișier JSON.
        """
        if not self.json_file_name:
            raise ValueError("Fișierul JSON nu a fost creat. Apelați create_new_files înainte de salvare.")

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {
            "time": current_time,
            "people_count": self.people_count
        }

        # Protejează accesul la fișier pentru a preveni conflictele de scriere
        with self.lock:
            # Citim fișierul existent și verificăm structura
            try:
                with open(self.json_file_name, "r") as file:
                    all_data = json.load(file)
            except (FileNotFoundError, json.JSONDecodeError):
                all_data = {"detections": []}  # Creează structura corectă dacă fișierul este corupt sau inexistent

            # Adaugă noile date în lista `detections`
            if "detections" not in all_data:
                all_data["detections"] = []
            all_data["detections"].append(data)

            # Scriem noile date în fișier
            with open(self.json_file_name, "w") as file:
                json.dump(all_data, file, indent=4)

    def get_people_count(self):
        return self.people_count

    def start_auto_save(self):
        def auto_save_loop_people():
            while True:
                self.save_to_json()
                time.sleep(20)  # Așteaptă 20 de secunde înainte de a relua salvarea

        # Lansează auto_save_loop pe un thread separat
        save_thread = threading.Thread(target=auto_save_loop_people, daemon=True)
        save_thread.start()
