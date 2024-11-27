# src/detectors/yolo_detector.py
from src.libs import *
from src.utils.detection_utils import filter_detections
from src.managers.table_manager import TableManager
from src.managers.people_manager import PeopleManager
from src.managers.alarm_manager import AlarmManager

from src.utils.time_utils import format_time, convert_duration

class YoloDetector:
    def __init__(self, model_path="models/yolov10l.pt"):  # Path to the YOLO model
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # Folosește modelul default 'yolov8n.pt' dacă nu este specificat un model_path
        self.model_path = model_path
        self.load_model(self.model_path)
        self.table_manager = TableManager()  # Instanțiază managerul de mese
        self.people_manager = PeopleManager()  # Instanțiem PeopleManager
        self.alarm_manager = AlarmManager()  # Instanțiază AlarmManager
        self.detecting_tables_only = False
        self.done_setting_tables = False
        self.detecting_all = False
        self.tables_detected = []
        self.tables_number = 0
        self.people_number = 0
        self.overlap_threshold = 0.2

        print("Yolo running on", self.device)

        # Aici definim clasele obiectelor speciale
        self.special_object_classes = {
            39: 'bottle', 40: 'wine glass', 41: 'cup', 42: 'fork', 43: 'knife',
            44: 'spoon', 45: 'bowl', 46: 'banana', 47: 'apple', 48: 'sandwich',
            49: 'orange', 50: 'broccoli', 51: 'carrot', 52: 'hot dog',
            53: 'pizza', 54: 'donut', 55: 'cake'
        }


    def load_model(self, model_path):
        """Încarcă modelul YOLO de la calea specificată pe dispozitivul adecvat."""
        self.model_path = model_path
        self.model = YOLO(model_path, verbose=False).to(self.device)
        print(f"Modelul {model_path} a fost încărcat pe {self.device}")

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

        filtered_detections = filter_detections(detections, self.overlap_threshold)
        self.tables_number = sum(1 for d in filtered_detections if d['class'] == 60) 
        self.people_number = sum(1 for d in filtered_detections if d['class'] == 0) 
        # Numărăm persoanele detectate
        
        self.people_manager.set_people_number(self.people_number)

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
                frame = cv2.putText(frame, label, (int(x1), int(y1) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        return frame

    def draw_detection_with_table_id(self, frame, detections):
            if detections:
                for det in detections:
                    box = det['box']
                    class_id = det['class']
                    x1, y1, x2, y2 = box
                    if class_id == 0:  # Persoană
                        label = "people"
                        if self.people_manager.people_count >= self.people_manager.get_max_people_number():
                            color = (0, 0, 255)
                            self.trigger_alarm()
                        else:
                            color = (255, 0, 0)
                    elif class_id in self.special_object_classes:
                        label = f"{self.special_object_classes[class_id]}"
                        color = (0, 0, 255)
                    else:
                        continue

                    frame = cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                    frame = cv2.putText(frame, label, (int(x1), int(y1) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
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
                    max_time = self.table_manager.get_max_time(status)
                
                    if max_time is not None and duration >= convert_duration(max_time):
                        color = (0, 0, 255)
                        self.trigger_alarm()
                    else:
                        color = (0, 255, 0)
                    frame = cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                    frame = cv2.putText(frame, label, (int(x1), int(y1) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            return frame
    
    def draw_auto_detections(self, frame, detections):
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
                    color = (0, 255, 0)
                elif class_id in self.special_object_classes:
                    label = f"{self.special_object_classes[class_id]}"
                    color = (0, 0, 255)
                else:
                    continue
                
                frame = cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                frame = cv2.putText(frame, label, (int(x1), int(y1) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        return frame
    
    def draw_detections(self, frame, detections):
        if detections:
            for det in detections:
                box = det['box']
                class_id = det['class']
                x1, y1, x2, y2 = box
                if class_id == 0:  # Persoană
                    label = f"people: {det['confidence']*100:.2f}%"
                    color = (33, 150, 243)   # Albastru modern
                elif class_id == 60:  # Masă
                    label = f"table: {det['confidence']*100:.2f}%"
                    color = (76, 175, 80) # Verde modern
                elif class_id in self.special_object_classes:
                    label = f"{self.special_object_classes[class_id]}: {det['confidence']*100:.2f}%"
                    color = (255, 76, 76)   # Roșu modern
                else:
                    continue

                frame = cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                #frame = cv2.putText(frame, label, (int(x1), int(y1) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                frame = self.draw_advanced_label(frame, y1, x1, label, color)

        return frame
    
    def draw_advanced_label(self, frame, y1, x1, label, color):
        # Calculăm dimensiunile label-ului
        font = cv2.FONT_HERSHEY_PLAIN
        font_scale = 1
        font_thickness = 1
        text_size = cv2.getTextSize(label, font, font_scale, font_thickness)[0]
        
        # Calculăm poziția label-ului
        text_x = int(x1)  # Plasăm textul de la colțul dreapta al dreptunghiului
        text_y = int(y1) - 5  # Ajustăm poziția pentru text mai sus

        # Desenăm fundalul label-ului cu culoare solidă, începând de la colțul drept al dreptunghiului
        label_padding = 5  # Spațiu mic între text și marginea fundalului
        cv2.rectangle(frame, 
                    (text_x, text_y - text_size[1] - label_padding),  # Colțul stâng al fundalului
                    (text_x + text_size[0] + label_padding, text_y + label_padding),  # Colțul drept al fundalului
                    color, -1)  # Fundal colorat

        # Desenăm textul alb pe fundalul colorat
        frame = cv2.putText(frame, label, (text_x, text_y), font, font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)

        return frame

    def get_tables_status_report(self):
        """
        Apelează funcția din TableManager pentru a obține statusul tuturor meselor și returnează șirul rezultat.
        """
        return self.table_manager.get_all_tables_status()
    
    def set_table_ids(self):
        self.reset_table_manager()
        if self.tables_detected:
            for table in self.tables_detected:
                box = table['box']
                self.table_manager.assign_table_id(None, box)      
            self.detecting_tables_only = False

    def reset_table_manager(self):
        self.table_manager.reset_tables()

    def trigger_alarm(self):
        """Apelăm funcția de alarmă din AlarmManager"""
        self.alarm_manager.play_alarm_sound()  # Redă alarmă
        
