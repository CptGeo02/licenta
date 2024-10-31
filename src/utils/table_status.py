from datetime import datetime
from src.utils.detection_utils import calculate_area
from src.utils.detection_utils import calculate_iou
from src.utils.time_utils import format_time

import os

class TableStatus:
    """
    Clasă care gestionează statusul și durata statusului pentru o masă.
    """
    def __init__(self, table_id, table_box=None, red_threshold=0.1, blue_threshold=0.1):
        self.table_id = table_id
        self.table_box = table_box  # Coordonatele box-ului mesei
        self.current_status = "availabe"
        self.start_time = datetime.now()
        self.status_durations = []  # Lista de statusuri și durate (status, durata)
        self.red_threshold = red_threshold
        self.blue_threshold = blue_threshold
        # Calea către fișierul TXT pentru statusuri
        self.txt_output_path = "data/outputs/table_status_changes.txt"
 
    def check_and_update_status(self, detections):
        """
        Verifică și actualizează statusul mesei în funcție de obiectele detectate.
        """
        new_status = self.check_table_status(self.table_box, detections)

        if new_status != self.current_status:
            self.update_status(new_status)

    def update_status(self, new_status):
        current_time = datetime.now()
        duration = (current_time - self.start_time).total_seconds()

        # Ignoră duratele prea scurte
        if self.current_status and duration >= 1.0:
            self.status_durations.append((self.current_status, duration))
            self.log_status_change(self.table_id, self.current_status, duration)

        # Actualizează statusul curent și resetează timer-ul
        self.previous_status = self.current_status
        self.current_status = new_status
        self.start_time = current_time

    def update_table_box(self, new_box):
        """
        Actualizează coordonatele box-ului mesei.
        """
        self.table_box = new_box
        # Poți adăuga logica suplimentară, dacă este nevoie, când se actualizează box-ul

    def get_current_status_duration(self):
        """
        Returnează durata în secunde a statusului curent.
        """
        current_time = datetime.now()
        return (current_time - self.start_time).total_seconds()
    
    def export_status_data(self):
        """
        Exportă datele statusurilor într-un format dict pentru salvare în Excel.
        """
        # Include statusul curent dacă aplicația este oprită înainte de a se schimba
        if self.current_status:
            current_time = datetime.now()
            duration = (current_time - self.start_time).total_seconds()
            self.status_durations.append((self.current_status, duration))

        # Structura dict-ului pentru export
        return {
            "Table ID": self.table_id,
            "Status": [entry[0] for entry in self.status_durations],
            "Duration (s)": [entry[1] for entry in self.status_durations]
        }

    def check_table_status(self, table_box, detections):
        """
        Determină statusul mesei pe baza obiectelor detectate.
        """
        red_objects = []
        blue_objects = []

        for det in detections:
            if det['class'] in range(39, 56):  # Obiecte roșii (ex: sticle, pahare de vin etc.)
                red_objects.append(det)
            elif det['class'] == 0:  # Persoane
                blue_objects.append(det)

        table_area = calculate_area(table_box)
        red_count = 0
        blue_count = 0

        for red in red_objects:
            red_area = calculate_area(red['box'])
            red_iou = calculate_iou(table_box, red['box'])
            if red_iou >= self.red_threshold * (red_area / table_area):
                red_count += 1

        for blue in blue_objects:
            blue_area = calculate_area(blue['box'])
            blue_iou = calculate_iou(table_box, blue['box'])
            if blue_iou >= self.blue_threshold * (blue_area / table_area):
                blue_count += 1

        if red_count > 0 and blue_count == 0:
            return "need to clean"
        elif red_count == 0 and blue_count == 0:
            return "available"
        elif blue_count > 0 and red_count == 0:
            return "ready to order"
        elif blue_count > 0 and red_count > 0:
            return "eating"

        return "unknown"

    def log_status_change(self, object_id, status, duration):
        with open(self.txt_output_path, "a") as f:
            f.write(f"{object_id}, {status}, {duration}\n")
