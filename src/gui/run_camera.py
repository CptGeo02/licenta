from src.libs import *

def run_camera(app):
    cap = cv2.VideoCapture(0)  # Pornim camera
    while app.running:
        ret, frame = cap.read()  # Citim un cadru de la cameră
        if not ret:
            break

        # Salvăm cadrul curent pentru a fi afișat ulterior în funcția update_frame
        app.current_frame = frame  # Cadrul brut, fără prelucrare
    cap.release()  # Eliberăm resursele camerei
    app.running = False
