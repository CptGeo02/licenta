# src/detectors/yolo_detector.py

import os
import pandas as pd
import torch
import cv2
from src.libs import *
from src.utils.detection_utils import filter_detections
from src.managers.table_manager import TableManager
from src.utils.time_utils import format_time

class YoloDetector:
    def __init__(self, model_path="models/yolov9e.pt"):  # Path to the YOLOv8 model
        self.model = YOLO(model_path).to(device)
        print(self.model.names)
        self.table_manager = TableManager()  # Instanțiază managerul de mese
        self.detecting_tables_only = False
        self.done_setting_tables = False
        self.tables_detected = []

        # Aici definim clasele obiectelor speciale
        self.special_object_classes = {
            39: 'bottle', 40: 'wine glass', 41: 'cup', 42: 'fork', 43: 'knife',
            44: 'spoon', 45: 'bowl', 46: 'banana', 47: 'apple', 48: 'sandwich',
            49: 'orange', 50: 'broccoli', 51: 'carrot', 52: 'hot dog',
            53: 'pizza', 54: 'donut', 55: 'cake'
        }

        # Inițializează fișierul Excel
        self.output_path = "data/outputs/table_status_report.xlsx"
        
        # Șterge fișierul existent dacă există
        if os.path.exists(self.output_path):
            os.remove(self.output_path)
        
        # Creează un DataFrame nou cu coloanele corecte
        self.initialize_excel_file()

    def initialize_excel_file(self):
        df = pd.DataFrame(columns=["ID", "Status", "Duration"])
        df.to_excel(self.output_path, index=False)

    def detect(self, frame):
        frame_normalized = (frame / 255.0).astype("float32")  # Normalizează cadrul doar pentru model
        frame_tensor = torch.from_numpy(frame_normalized).to(device).permute(2, 0, 1).unsqueeze(0)

        results = self.model(frame_tensor)

        if len(results) == 0 or len(results[0].boxes) == 0:
            return []

        detections = []
        for box in results[0].boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            cls = int(box.cls[0])
            conf = box.conf[0]

            detections.append({
                'box': (x1.item(), y1.item(), x2.item(), y2.item()),
                'class': cls,
                'confidence': conf.item()
            })

        filtered_detections = filter_detections(detections)
        return filtered_detections
    
    def draw_only_tables(self, frame, detections):
        self.tables_detected = [det for det in detections if det['class'] == 60]
        if self.tables_detected:
            for table in self.tables_detected:
                box = table['box']
                x1, y1, x2, y2 = box
                color = (0, 255, 0)
                label = "table"
                frame = cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                frame = cv2.putText(frame, label, (int(x1), int(y1) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return frame
    
    def set_table_ids(self):
        self.reset_table_manager()
        if self.tables_detected:
            for table in self.tables_detected:
                box = table['box']
                self.table_manager.assign_table_id(None, box)      
            self.detecting_tables_only = False

    def reset_table_manager(self):
        self.table_manager.reset_tables()
        
    def draw_just_people_and_food(self, frame, detections):
            if detections:
                for det in detections:
                    box = det['box']
                    class_id = det['class']
                    x1, y1, x2, y2 = box
                    if class_id == 0:  # Persoană
                        label = "people"
                        color = (255, 0, 0)
                    elif class_id in self.special_object_classes:
                        label = f"{self.special_object_classes[class_id]}"
                        color = (0, 0, 255)
                    else:
                        continue
                    
                    frame = cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                    frame = cv2.putText(frame, label, (int(x1), int(y1) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            if self.tables_detected:
                for table in self.tables_detected:
                    box = table['box']
                    class_id = table['class']
                    x1, y1, x2, y2 = box
                    table_id = self.table_manager.get_table_id_by_overlap(box)
                    self.table_manager.assign_table_id(table_id, box)
                    if table_id is None:
                        table_id = self.table_manager.table_counter
                    # Verificăm și actualizăm statusul mesei
                    self.table_manager.check_and_update_status(detections)
                    status, duration = self.table_manager.get_table_info(table_id)
                    formatted_duration = format_time(duration)  # Formatează durata
                    label = f"TABLE{table_id} {status} for {formatted_duration}"
                    color = (0, 255, 0)
                    frame = cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                    frame = cv2.putText(frame, label, (int(x1), int(y1) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            return frame
    
    def draw_detections(self, frame, detections):
        if detections:
            for det in detections:
                box = det['box']
                class_id = det['class']
                x1, y1, x2, y2 = box
                if class_id == 0:  # Persoană
                    label = "people"
                    color = (255, 0, 0)
                elif class_id == 60:  # Masă
                    table_id = self.table_manager.get_table_id_by_overlap(box)
                    self.table_manager.assign_table_id(table_id, box)
                    if table_id is None:
                        table_id = self.table_manager.table_counter
                    # Verificăm și actualizăm statusul mesei
                    self.table_manager.check_and_update_status(detections)
                    status, duration = self.table_manager.get_table_info(table_id)
                    formatted_duration = format_time(duration)  # Formatează durata
                    label = f"Table {table_id} {status} for {formatted_duration}"
                    self.save_label_to_excel(table_id, status, formatted_duration)  # Salvează label-ul live
                    color = (0, 255, 0)
                elif class_id in self.special_object_classes:
                    label = f"{self.special_object_classes[class_id]}"
                    color = (0, 0, 255)
                else:
                    continue
                
                frame = cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                frame = cv2.putText(frame, label, (int(x1), int(y1) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        return frame
    
    def get_tables_status_report(self):
        """
        Apelează funcția din TableManager pentru a obține statusul tuturor meselor și returnează șirul rezultat.
        """
        return self.table_manager.get_all_tables_status()
    
    def save_label_to_excel(self, object_id, status, duration):
        # Încarcă fișierul Excel existent
        df_existing = pd.read_excel(self.output_path)

        # Verifică dacă DataFrame-ul are coloanele corecte
        if 'ID' not in df_existing.columns or 'Status' not in df_existing.columns or 'Duration' not in df_existing.columns:
            df_existing = pd.DataFrame(columns=["ID", "Status", "Duration"])  # Creează un DataFrame nou

        # Verifică dacă ID-ul există deja în DataFrame
        if object_id in df_existing["ID"].values:
            # Actualizează statusul și durata pentru ID-ul existent
            df_existing.loc[df_existing["ID"] == object_id, ["Status", "Duration"]] = [status, duration]
        else:
            # Adaugă o nouă linie pentru ID-ul nou
            new_row = pd.DataFrame([[object_id, status, duration]], columns=["ID", "Status", "Duration"])
            df_existing = pd.concat([df_existing, new_row], ignore_index=True)

        # Salvează DataFrame-ul actualizat înapoi în fișierul Excel
        df_existing.to_excel(self.output_path, index=False)
