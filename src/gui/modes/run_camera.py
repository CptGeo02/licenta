import numpy as np
import cv2
from src.libs import *

def run_camera(app):
    try:
        current_camera = app.selected_camera[-1]  # Camera inițială
    finally:
         current_camera = 0
    print("[INFO] Pornire cameră:", current_camera)

    cap = cv2.VideoCapture(int(current_camera))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while app.running and not app.stop_event.is_set():  # Verificăm stop_event pentru oprire
        if app.selected_camera[-1] != current_camera:  # Dacă utilizatorul schimbă camera
            print(f"[INFO] Schimbare cameră: {current_camera} -> {app.selected_camera[-1]}")
            cap.release()  # Eliberăm resursele camerei anterioare
            current_camera = app.selected_camera[-1]  
            cap = cv2.VideoCapture(int(current_camera))  # Deschidem noua cameră
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Eroare la citirea frame-ului!")
            break

        app.current_frame = frame  # Stocăm frame-ul curent

    cap.release()  # Eliberăm camera la ieșire
    print("[INFO] Camera oprită.")
    app.running = False
