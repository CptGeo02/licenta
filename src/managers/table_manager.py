# src/managers/table_manager.py

from src.utils.table_status import TableStatus
from src.utils.detection_utils import *
from src.libs import *

class TableManager:
    def __init__(self):
        self.table_ids = {}  # Aici stocăm ID-urile meselor
        self.table_counter = 0  # Contor pentru ID-urile meselor
        self.tables = {}  # Aici stocăm obiectele TableStatus

    def assign_table_id(self, table_id, box):
        if table_id is None:
            self.table_counter += 1
            new_table = TableStatus(self.table_counter, table_box=box)
            self.tables[self.table_counter] = new_table
        else:
            # Dacă masa a fost detectată, actualizează doar box-ul
            self.update_table_box(table_id, box)

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