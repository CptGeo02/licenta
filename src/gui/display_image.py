from src.libs import *

def resize_image_for_yolo(frame):
    """Redimensionează imaginea la o dimensiune divizibilă cu 32."""
    h, w = frame.shape[:2]
    new_w = (w // 32) * 32
    new_h = (h // 32) * 32
    return cv2.resize(frame, (new_w, new_h))

def display_image(app):
    if app.images:
        img_path = os.path.join('data/images/', app.images[app.image_index])
        frame = cv2.imread(img_path)

        if frame is not None:
            # Redimensionează imaginea pentru a fi compatibilă cu YOLO
            frame = resize_image_for_yolo(frame)

            # Run YOLO detection
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
