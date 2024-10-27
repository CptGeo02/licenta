from src.libs import *

def resize_frame_for_yolo(frame):
    """Redimensionează imaginea/cadrul la o dimensiune divizibilă cu 32."""
    h, w = frame.shape[:2]
    new_w = (w // 32) * 32
    new_h = (h // 32) * 32
    return cv2.resize(frame, (new_w, new_h))

def display_frame(app, frame):
    """Afișează un cadru din orice sursă: imagine, video sau flux live."""
    if frame is not None:
        # Redimensionează cadrul pentru a fi compatibil cu YOLO
        frame = resize_frame_for_yolo(frame)

        # Rulează detecția YOLO
        detections = app.detector.detect(frame)
        frame = app.detector.draw_detections(frame, detections)

        # Convert BGR (OpenCV) to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img_tk = ImageTk.PhotoImage(image=img)

        app.label.configure(image=img_tk)
        app.label.image = img_tk  # Reference for garbage collection

        # Center the image on the canvas
        canvas_width = app.canvas.winfo_width()
        canvas_height = app.canvas.winfo_height()
        img_width, img_height = img.size
        x = (canvas_width - img_width) // 2
        y = (canvas_height - img_height) // 2

        app.label.place(x=x, y=y)
