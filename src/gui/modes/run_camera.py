from src.libs import *

def run_camera(app):
    cap = cv2.VideoCapture(1)  # Pornim camera
    default_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    default_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    # Setăm rezoluția camerei la HD (1280x720)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    print(f"Rezoluția implicită a camerei: {int(default_width)}x{int(default_height)}")
    while app.running:
        ret, frame = cap.read()  # Citim un cadru de la cameră
        if not ret:
            break

        # Salvăm cadrul curent pentru a fi afișat ulterior în funcția update_frame
        app.current_frame = frame  # Cadrul brut, fără prelucrare
    cap.release()  # Eliberăm resursele camerei
    app.running = False
