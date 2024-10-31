# src/managers/table_manager.py

from src.utils.table_status import TableStatus

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
                object_id = next((key for key, value in self.table_status_objects.items() if self.is_overlap(box, value.table_box)), None)

                if object_id is None:
                    # Masa e nou detectată
                    self.table_counter += 1
                    new_table_status = TableStatus(self.table_counter, table_box=box)
                    self.table_status_objects[self.table_counter] = new_table_status
                else:
                    # Masa deja detectată, doar actualizăm box-ul
                    self.table_status_objects[object_id].update_table_box(box)

    def is_overlap(self, box1, box2):
        x1, y1, x2, y2 = box1
        x3, y3, x4, y4 = box2

        # Verificăm dacă există o suprapunere
        return not (x2 < x3 or x4 < x1 or y2 < y3 or y4 < y1)

    def check_and_update_status(self, detections):
        for _, table_status in self.table_status_objects.items():
            table_status.check_and_update_status(detections)
    
    def get_table_info(self, object_id):
        table_status = self.table_status_objects.get(object_id)
        if table_status:
            return table_status.current_status, table_status.get_current_status_duration()
        return None, None
