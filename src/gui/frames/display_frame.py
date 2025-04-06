from src.libs import *
from src.utils.frame_utils import *

def display_frame(app, frame):
    """Afișează un cadru din orice sursă: imagine, video sau flux live și actualizează statusul meselor."""
    if frame is not None:
        # Redimensionează cadrul pentru a fi compatibil cu YOLO
        frame = resize_frame_for_yolo(frame)
        if app.illumination_enabled.get():
            frame = correct_illumination(
                frame,
                clahe_clip=app.clahe_clip_var.get(),
                clahe_tile_size=app.clahe_tile_var.get()
        )
        # Calcul FPS doar pt admin mode
        if hasattr(app, 'prev_time'):
            current_time = time.time()
            delta_time = current_time - app.prev_time
            if delta_time > 0:
                fps = 1 / delta_time
                app.fps = fps
            app.prev_time = current_time
        if app.name == "admin":
            if app.detector.detecting_all == True and not app.auto_detect_enabled.get():
                frame = app.detector.draw_detections(frame, app.detector.detect(frame))
            elif app.auto_detect_enabled.get():
                frame = app.detector.draw_auto_detections(frame, app.detector.detect(frame))
                app.update_status_label()
            elif app.detector.detecting_tables_only:
                frame = app.detector.draw_only_tables(frame, app.detector.detect(frame))
            elif app.detector.done_setting_tables:
                frame = app.detector.draw_detection_with_table_id(frame, app.detector.detect(frame))
                app.update_status_label()
        else:
            if app.detector.detecting_tables_only:
                frame = app.detector.draw_only_tables(frame, app.detector.detect(frame))
            elif app.detector.done_setting_tables:
                frame = app.detector.draw_detection_with_table_id(frame, app.detector.detect(frame))
                app.update_status_label()
        # Convert BGR (OpenCV) to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img_tk = ImageTk.PhotoImage(image=img)

        app.label.configure(image=img_tk)
        app.label.image = img_tk  # Referință pentru garbage collection

        # Centrează imaginea pe canvas
        canvas_width = app.canvas.winfo_width()
        canvas_height = app.canvas.winfo_height()
        img_width, img_height = img.size
        x = (canvas_width - img_width) // 2
        y = (canvas_height - img_height) // 2

        app.label.place(x=x, y=y)