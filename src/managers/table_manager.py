import json
from datetime import datetime
import threading
import time
from src.utils.table_status import TableStatus
from src.utils.detection_utils import *
from src.libs import *
import numpy as np

class TableManager:
    def __init__(self):
        self.table_ids = {}  # Aici stocăm ID-urile meselor
        self.table_counter = 0  # Contor pentru ID-urile meselor
        self.tables = {}  # Aici stocăm obiectele TableStatus
        # Lista statusurilor ciclice
        self.status_cycle = ['available', 'ready to order', 'eating', 'need to clean']
        self.max_time_available = "99:99:99"
        self.max_time_ready_to_order = "99:99:99"
        self.max_time_eating = "99:99:99"
        self.max_time_need_to_clean = "99:99:99"

    def set_max_time(self, status_type, time_value):
        """
        Setează timpul maxim pentru un anumit status.
        """
        if status_type == "available":
            self.max_time_available = time_value
        elif status_type == "ready to order":
            self.max_time_ready_to_order = time_value
        elif status_type == "eating":
            self.max_time_eating = time_value
        elif status_type == "need to clean":
            self.max_time_clean = time_value

    def get_max_time(self, status_type):
        """
        Returnează timpul maxim pentru un anumit status.
        """
        if status_type == "available":
            return self.max_time_available
        elif status_type == "ready to order":
            return self.max_time_ready_to_order
        elif status_type == "eating":
            return self.max_time_eating
        elif status_type == "need to clean":
            return self.max_time_clean
        return None
    
    def create_new_files(self):
        """
        Creează fișierul JSON cu data și ora curentă la începutul fiecărei runde.
        """
        # Obține data și ora curentă pentru denumirea fișierelor
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.json_file_name = f"data/outputs/table_records/table_status_report_{now}.json"
        
        # Creează fișierul JSON gol la începutul fiecărei runde
        with open(self.json_file_name, 'w') as f:
            json.dump({"table_statuses": []}, f)

    def save_status_to_json(self):
        """
        Salvează statusurile meselor într-un fișier JSON, conform regulilor specificate:
        1. Dacă table_id nu există în fișierul JSON, se adaugă o nouă intrare.
        2. Dacă table_id există:
            2.1. Dacă statusul este identic:
                2.1.1. Dacă noul Duration este mai mare cu cel puțin o secundă decât cel precedent, actualizează durata.
            2.2. Dacă statusul este diferit, adaugă o nouă linie cu datele actuale, dar doar dacă durata este mai mare cu cel puțin o secundă.
        """
        try:
            # Încarcă datele existente din fișier
            with open(self.json_file_name, 'r') as f:
                data = json.load(f)

            # Procesare statusuri mese
            for table_id, table_status in self.tables.items():
                # Verificăm dacă statusul este 'unknown' și, dacă da, îl ignorăm
                if table_status.current_status == "unknown":
                    continue

                start_time_str = table_status.start_time.strftime("%Y-%m-%d %H:%M:%S")
                duration = table_status.get_current_status_duration()
                duration_str = f"{int(duration // 3600):02}:{int((duration % 3600) // 60):02}:{int(duration % 60):02}"
                
                # Găsim intrările curente pentru acest table_id în fișier
                current_entries = [entry for entry in data["table_statuses"] if entry["table_id"] == table_id]

                if not current_entries:
                    # 1) Nu există o intrare pentru table_id => Adăugăm noua intrare
                    data["table_statuses"].append({
                        "table_id": table_id,
                        "status": table_status.current_status,
                        "start_time": start_time_str,
                        "duration": duration_str
                    })
                else:
                    # 2) Există deja o intrare pentru table_id
                    latest_entry = current_entries[-1]

                    if latest_entry["status"] == table_status.current_status:
                        # 2.1) Statusul este identic
                        latest_duration = latest_entry["duration"]
                        latest_duration_seconds = int(latest_duration[:2]) * 3600 + int(latest_duration[3:5]) * 60 + int(latest_duration[6:])

                        if duration > latest_duration_seconds + 1:
                            # 2.1.1) Dacă noul Duration este mai mare cu cel puțin o secundă decât cel precedent, actualizează durata
                            latest_entry["duration"] = duration_str
                    else:
                        # 2.2) Statusul este diferit => Adăugăm o nouă linie
                        data["table_statuses"].append({
                            "table_id": table_id,
                            "status": table_status.current_status,
                            "start_time": start_time_str,
                            "duration": duration_str
                        })

            # Salvăm datele actualizate în fișierul JSON
            with open(self.json_file_name, 'w') as f:
                json.dump(data, f, indent=4)

        except FileNotFoundError:
            # Dacă fișierul nu există, creează un fișier nou cu structura dorită
            with open(self.json_file_name, 'w') as f:
                json.dump({"table_statuses": []}, f)

                
    def reset_tables(self):
        self.table_ids = {}
        self.table_counter = 0
        self.tables = {}

    def set_red_threshold_for_all_tables(self, red_threshold):
        for table_status in self.tables.values():
            table_status.set_red_threshold(red_threshold)

    def set_blue_threshold_for_all_tables(self, blue_threshold):
        for table_status in self.tables.values():
            table_status.set_blue_threshold(blue_threshold)

    def assign_table_id(self, table_id, box):
        if table_id is None:
            self.table_counter += 1
            new_table = TableStatus(self.table_counter, table_box=box)
            self.tables[self.table_counter] = new_table
        else:
            # Dacă masa a fost detectată, actualizează doar box-ul
            self.update_table_box(table_id, box)

    def get_all_tables_status(self):
        """
        Returnează un string cu statusul pentru fiecare masă în formatul:
        'Table <table_id> Status: <current_status> Start Time: <start_time> Duration: <status_duration>'
        """
        status_strings = []
        
        for table_id, table_status in self.tables.items():
            start_time_str = table_status.start_time.strftime("%Y-%m-%d %H:%M:%S")
            duration = table_status.get_current_status_duration()
            duration_str = f"{int(duration // 3600):02}:{int((duration % 3600) // 60):02}:{int(duration % 60):02}"

            status_strings.append(
                f"Table {table_id} Status: {table_status.current_status} "
                f"Start Time: {start_time_str} Duration: {duration_str}"
            )
        
        return "\n".join(status_strings)

    def get_table_id_by_box(self, box):
        center = self._get_box_center(box)
        for table_id, table_status in self.tables.items():
            table_center = self._get_box_center(table_status.table_box)
            if np.linalg.norm(np.array(center) - np.array(table_center)) < 100:  # Pragul de proximitate
                return table_id
        return None

    def get_table_id_by_similarity(self, box, threshold=0.9):
        for table_id, table_status in self.tables.items():
            if self._are_tables_identical(box, table_status.table_box, threshold):
                return table_id
        return None

    def get_table_id_by_overlap(self, box):
        for table_id, table_status in self.tables.items():
            if self._is_overlap(box, table_status.table_box):
                return table_id
        return None

    def update_table_box(self, table_id, box):
        self.tables[table_id].update_table_box(box)

    def check_and_update_status(self, detections):
        for _, table_status in self.tables.items():
            table_status.check_and_update_status(detections)
        
    def get_table_info(self, object_id):
        table_status = self.tables.get(object_id)
        if table_status:
            return table_status.current_status, table_status.get_current_status_duration()
        return None, None

    def _get_box_center(self, box):
        x1, y1, x2, y2 = box
        return (0.5 * (x1 + x2), 0.5 * (y1 + y2))

    def _is_overlap(self, box1, box2):
        # Extrage coordonatele box-urilor
        x1, y1, x2, y2 = box1
        x3, y3, x4, y4 = box2

        # Calculează ariile box-urilor
        area_box1 = (x2 - x1) * (y2 - y1)
        area_box2 = (x4 - x3) * (y4 - y3)

        # Determină coordonatele intersecției
        intersect_x1 = max(x1, x3)
        intersect_y1 = max(y1, y3)
        intersect_x2 = min(x2, x4)
        intersect_y2 = min(y2, y4)

        # Calculează aria intersecției
        intersect_width = max(0, intersect_x2 - intersect_x1)
        intersect_height = max(0, intersect_y2 - intersect_y1)
        intersection_area = intersect_width * intersect_height

        # Verifică dacă există o suprapunere semnificativă
        overlap_ratio = intersection_area / min(area_box1, area_box2)
        return (overlap_ratio >= 0.9) and (area_box1 >= 0.95 * area_box2 or area_box2 >= 0.95 * area_box1)

    def _compute_iou(self, rect1, rect2):
        # Descompunem box-urile în coordonate
        x1, y1, x2, y2 = rect1
        x3, y3, x4, y4 = rect2

        # Calculăm coordonatele intersecției
        inter_x1 = max(x1, x3)
        inter_y1 = max(y1, y3)
        inter_x2 = min(x2, x4)
        inter_y2 = min(y2, y4)

        # Calculăm aria intersecției
        inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)

        # Calculăm aria fiecărui box
        rect1_area = (x2 - x1) * (y2 - y1)
        rect2_area = (x4 - x3) * (y4 - y3)

        # Calculăm aria de unire
        total_area = rect1_area + rect2_area - inter_area

        # Calculăm IoU
        iou = inter_area / total_area if total_area > 0 else 0

        return iou

    def _are_tables_identical(self, rect1, rect2, threshold=0.9):
        iou = self._compute_iou(rect1, rect2)

        # Verificăm dacă IoU depășește pragul stabilit
        return iou >= threshold
    
    def start_auto_save(self):
        def auto_save_loop():
            while True:
                self.save_status_to_json()
                time.sleep(1)  # Așteaptă o secundă înainte de a relua salvarea

        # Lansează auto_save_loop pe un thread separat
        save_thread = threading.Thread(target=auto_save_loop, daemon=True)
        save_thread.start()
