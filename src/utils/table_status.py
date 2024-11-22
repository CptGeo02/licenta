import os
from datetime import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from src.utils.time_utils import format_time
from src.utils.detection_utils import calculate_area
from src.utils.detection_utils import calculate_iou

class TableStatus:
    """
    Clasă care gestionează statusul și durata statusului pentru o masă.
    """
    def __init__(self, table_id, table_box=None, red_threshold=0.1, blue_threshold=0.1):
        self.table_id = table_id
        self.table_box = table_box  # Coordonatele box-ului mesei
        self.current_status = "unknown"
        self.previous_status = None
        self.start_time = datetime.now()
        self.status_durations = []  # Lista de statusuri și durate (status, durata)
        self.set_red_threshold(red_threshold)
        self.set_blue_threshold(blue_threshold)
        
    def set_red_threshold(self, red_threshold):
        self.red_threshold = red_threshold

    def set_blue_threshold(self, blue_threshold):
        self.blue_threshold = blue_threshold

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
        if duration >= 1.0:
            self.status_durations.append((self.current_status, duration))
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

    def check_table_status(self, table_box, detections):
        """
        Determină statusul mesei pe baza obiectelor detectate.

        Parametri:
        - table_box: coordonatele mesei curente (x1, y1, x2, y2).
        - detections: lista detectărilor, fiecare fiind un dicționar cu cheile `class`, `box`, și `confidence`.

        Returnează:
        - Statusul mesei: "need to clean", "available", "ready to order", "eating" sau "unknown".
        """

        # Filtrăm obiectele detectate relevante (în apropierea mesei și din clasele corespunzătoare)
        red_objects, blue_objects = self.filter_relevant_objects(table_box, detections)

        # Determinăm aria mesei
        table_area = calculate_area(table_box)

        # Numărăm obiectele relevante
        red_count = sum(
            self.is_relevant_object(table_box, obj['box'], table_area, self.red_threshold)
            for obj in red_objects
        )
        blue_count = sum(
            self.is_relevant_object(table_box, obj['box'], table_area, self.blue_threshold)
            for obj in blue_objects
        )

        # Determinăm statusul mesei pe baza numărătorii
        if red_count > 0 and blue_count == 0:
            return "need to clean"
        elif red_count == 0 and blue_count == 0:
            return "available"
        elif blue_count > 0 and red_count == 0:
            return "ready to order"
        elif blue_count > 0 and red_count > 0:
            return "eating"
        return "unknown"

    def filter_relevant_objects(self, table_box, detections):
        """
        Filtrează obiectele detectate pentru a include doar cele relevante (roșii sau albastre)
        care sunt în proximitatea mesei curente.

        Returnează:
        - red_objects: obiecte roșii relevante.
        - blue_objects: obiecte albastre relevante.
        """
        red_objects = []
        blue_objects = []

        for det in detections:
            class_id = det['class']
            if class_id in range(39, 56):  # Obiecte roșii
                if calculate_iou(table_box, det['box']) > 0:  # În proximitatea mesei
                    red_objects.append(det)
            elif class_id == 0:  # Persoane
                if calculate_iou(table_box, det['box']) > 0:  # În proximitatea mesei
                    blue_objects.append(det)

        return red_objects, blue_objects

    def is_relevant_object(self, table_box, obj_box, table_area, threshold):
        """
        Verifică dacă un obiect este suficient de relevant pentru masa curentă,
        bazat pe suprapunere și raportul dimensiunilor.

        Returnează:
        - True dacă obiectul este relevant, altfel False.
        """
        obj_area = calculate_area(obj_box)
        iou = calculate_iou(table_box, obj_box)
        return iou >= threshold * (obj_area / table_area)
