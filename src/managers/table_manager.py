# src/managers/table_manager.py

from src.utils.table_status import TableStatus
from src.utils.detection_utils import *
class TableManager:
    def __init__(self):
        self.table_ids = {}  # Aici stocăm ID-urile meselor
        self.table_counter = 0  # Contor pentru ID-urile meselor
        self.table_status_objects = {}  # Aici stocăm obiectele TableStatus

    def assign_table_id(self, detections):
        for det in detections:
            if det['class'] == 60:  # ID pentru mese
                box = det['box']
                # Verifică dacă masa a fost deja detectată prin suprapunere
                object_id = next((key for key, value in self.table_status_objects.items() if are_tables_identical(box, value.table_box)), None)

                if object_id is None:
                    # Masa e nou detectată
                    self.table_counter += 1
                    new_table_status = TableStatus(self.table_counter, table_box=box)
                    self.table_status_objects[self.table_counter] = new_table_status
                else:
                    # Masa deja detectată, doar actualizăm box-ul
                    self.table_status_objects[object_id].update_table_box(box)

    def is_overlap(self, box1, box2):
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



    def check_and_update_status(self, detections):
        for _, table_status in self.table_status_objects.items():
            table_status.check_and_update_status(detections)
    
    def get_table_info(self, object_id):
        table_status = self.table_status_objects.get(object_id)
        if table_status:
            return table_status.current_status, table_status.get_current_status_duration()
        return None, None
