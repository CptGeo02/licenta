import numpy as np
import cv2
from src.libs import *

def run_camera(app):
    # Se folosește rezoluția setată în self.video_resolution (ex: (640, 480), (1920, 1080), etc.)
    if hasattr(app, 'selected_camera') and app.selected_camera:
        current_camera = app.selected_camera
    else:
        # Valoare implicită, dacă nu este setată o rezoluție
        current_camera = 0

    # Se folosește rezoluția setată în self.video_resolution (ex: (640, 480), (1920, 1080), etc.)
    if hasattr(app, 'video_resolution') and app.video_resolution:
        resolution = app.video_resolution
    else:
        # Valoare implicită, dacă nu este setată o rezoluție
        resolution = (640, 480)

    print("[INFO] Pornire cameră:", current_camera)
    print("[INFO] Format cameră:", resolution)

    cap = cv2.VideoCapture(int(current_camera))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

    previous_resolution = resolution  # Variabilă pentru a verifica modificarea rezoluției

    while app.running and not app.stop_event.is_set():  # Verificăm stop_event pentru oprire
        if app.selected_camera != current_camera:  # Dacă utilizatorul schimbă camera
            print(f"[INFO] Schimbare cameră: {current_camera} -> {app.selected_camera}")
            cap.release()  # Eliberăm resursele camerei anterioare
            current_camera = app.selected_camera
            cap = cv2.VideoCapture(current_camera)  # Deschidem noua cameră
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])  # Setăm noua rezoluție
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])  # Setăm noua rezoluție

        # Verificăm dacă s-a schimbat rezoluția
        if app.video_resolution != previous_resolution:
            print(f"[INFO] Schimbare rezoluție: {previous_resolution} -> {app.video_resolution}")
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, app.video_resolution[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, app.video_resolution[1])
            previous_resolution = app.video_resolution  # Actualizăm rezoluția anterioară

        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Eroare la citirea frame-ului!")
            break

        app.current_frame = frame  # Stocăm frame-ul curent

    cap.release()  # Eliberăm camera la ieșire
    print("[INFO] Camera oprită.")
    app.running = False
