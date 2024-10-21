from src.libs import *
from src.utils.detection_utils import filter_detections
from src.utils.table_status import check_table_status

class YoloDetector:
    def __init__(self, model_path="models/yolov8n.pt"):  # Path to the YOLOv8 model
        self.model = YOLO(model_path).to(device)
        print(self.model.names)
        self.person_id = 0
        self.table_id = 0
        self.special_object_classes = {
            39: 'bottle', 40: 'wine glass', 41: 'cup', 42: 'fork', 43: 'knife',
            44: 'spoon', 45: 'bowl', 46: 'banana', 47: 'apple', 48: 'sandwich',
            49: 'orange', 50: 'broccoli', 51: 'carrot', 52: 'hot dog',
            53: 'pizza', 54: 'donut', 55: 'cake'
        }

    def detect(self, frame):
        frame = frame / 255.0
        frame_tensor = torch.from_numpy(frame).to(device).permute(2, 0, 1).unsqueeze(0).float()

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

    def draw_detections(self, frame, detections, red_threshold=0.1, blue_threshold=0.1):
        people_count = 0
        tables_count = 0
        special_objects_count = 0
        table_statuses = {}

        if detections:
            for det in detections:
                x1, y1, x2, y2 = det['box']
                class_id = det['class']

                if class_id == 0:  # Person
                    label = "people"
                    color = (255, 0, 0)
                    people_count += 1
                elif class_id == 60:  # Table
                    self.table_id += 1
                    object_id = self.table_id
                    status = check_table_status((x1, y1, x2, y2), detections, red_threshold, blue_threshold)
                    table_statuses[object_id] = status
                    label = f"ID: {object_id}, Status: {status}"
                    color = (0, 255, 0)
                    tables_count += 1
                elif class_id in self.special_object_classes:
                    label = f"{self.special_object_classes[class_id]}"
                    color = (0, 0, 255)
                    special_objects_count += 1
                else:
                    continue

                frame = cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        return frame
