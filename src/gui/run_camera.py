from src.libs import *

def run_camera(app):
    cap = cv2.VideoCapture(0)
    while app.running:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Run detection using YOLO detector
        detections = app.detector.detect(frame)
        frame = app.detector.draw_detections(frame, detections)

        # Save the current frame for displaying
        app.current_frame = frame

    cap.release()
