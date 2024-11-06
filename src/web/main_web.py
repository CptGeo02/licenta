from flask import Flask, render_template, Response
from src.detectors.yolo_detector import YoloDetector
import threading
import cv2
import os
import time

class MainWeb:
    def __init__(self):
        self.app = Flask(
            __name__,
            template_folder=os.path.join(os.path.dirname(__file__), '../../templates'),
            static_folder=os.path.join(os.path.dirname(__file__), '../../static')
        )
        
        self.detector = YoloDetector()  # Instanțierea obiectului detector YOLO
        self.video_capture = None
        self.current_frame = None
        self.frame_lock = threading.Lock()

        # Rute pentru Flask
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/video_feed', 'video_feed', self.video_feed)
        self.app.add_url_rule('/start_camera', 'start_camera', self.start_camera)

    def resize_frame_for_yolo(self, frame):
        """Resize the image/frame to a size divisible by 32."""
        h, w = frame.shape[:2]
        new_w = (w // 32) * 32
        new_h = (h // 32) * 32
        return cv2.resize(frame, (new_w, new_h))

    def generate_frame(self):
        """Generates video stream for Flask to send frames to browser."""
        while True:
            with self.frame_lock:
                if self.current_frame is not None:
                    # Resize the frame for YOLO compatibility
                    frame = self.resize_frame_for_yolo(self.current_frame)
                    
                    # Run YOLO detection and check for issues
                    try:
                        detections = self.detector.detect(frame)
                        if detections is None:
                            print("Warning: No detections returned by YOLO")
                    except Exception as e:
                        print(f"Error in detection: {e}")
                        detections = []

                    # Draw detections on the frame (comment this temporarily if needed)
                    try:
                        frame = self.detector.draw_detections(frame, detections)
                    except Exception as e:
                        print(f"Error in drawing detections: {e}")
                    
                    # Encode the frame with detections to be transmitted
                    ret, buffer = cv2.imencode('.jpg', frame)
                    if ret:
                        frame_bytes = buffer.tobytes()
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')
                else:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + b'\r\n\r\n')
            
            time.sleep(0.01)  # Sleep for a short time to allow other tasks

    def index(self):
        """Rute pentru pagina principală."""
        return render_template("index.html")

    def video_feed(self):
        """Rute pentru alimentarea streamului video."""
        return Response(self.generate_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def start_camera(self):
        """Inițializarea camerei și alocarea video stream."""
        self.video_capture = cv2.VideoCapture(0)  # Use the default camera

        if not self.video_capture.isOpened():
            return "Camera not available", 500  # Error if camera is not accessible

        def update_video_stream():
            """Actualizează streamul video cu cadre din camera."""
            while True:
                ret, frame = self.video_capture.read()
                if not ret:
                    break
                with self.frame_lock:
                    self.current_frame = frame  # Save the frame for use in generate_frame
            self.video_capture.release()

        threading.Thread(target=update_video_stream, daemon=True).start()
        return '', 204

    def run(self):
        """Pornirea aplicației Flask."""
        self.app.run(debug=True)

if __name__ == '__main__':
    main_web = MainWeb()  # Instanțiază clasa
    main_web.run()  # Rulare aplicație web
