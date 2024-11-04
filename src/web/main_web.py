from flask import Flask, render_template, Response
from src.detectors.yolo_detector import YoloDetector
import threading
import cv2
import os
import time

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '../../templates'),
    static_folder=os.path.join(os.path.dirname(__file__), '../../static')
)
detector = YoloDetector()

# Global variables for video capture
video_capture = None
current_frame = None
frame_lock = threading.Lock()

def resize_frame_for_yolo(frame):
    """Resize the image/frame to a size divisible by 32."""
    h, w = frame.shape[:2]
    new_w = (w // 32) * 32
    new_h = (h // 32) * 32
    return cv2.resize(frame, (new_w, new_h))

def generate_frame():
    global current_frame
    while True:
        with frame_lock:
            if current_frame is not None:
                # Resize the frame for YOLO compatibility
                frame = resize_frame_for_yolo(current_frame)
                
                # Run YOLO detection and check for issues
                try:
                    detections = detector.detect(frame)
                    if detections is None:
                        print("Warning: No detections returned by YOLO")
                except Exception as e:
                    print(f"Error in detection: {e}")
                    detections = []

                # Draw detections on the frame (comment this temporarily if needed)
                try:
                    frame = detector.draw_detections(frame, detections)
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
        
        time.sleep(0.01) 

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/video_feed')
def video_feed():
    return Response(generate_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_camera')
def start_camera():
    global video_capture, current_frame
    video_capture = cv2.VideoCapture(0)  # Use the default camera

    if not video_capture.isOpened():
        return "Camera not available", 500  # Error if camera is not accessible

    def update_video_stream():
        global current_frame
        while True:
            ret, frame = video_capture.read()
            if not ret:
                break
            with frame_lock:
                current_frame = frame  # Save the frame for use in generate_frame
        video_capture.release()

    threading.Thread(target=update_video_stream, daemon=True).start()
    return '', 204

def run_web_app():
    app.run(debug=True)

if __name__ == '__main__':
    run_web_app()
