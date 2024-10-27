from src.libs import *

def run_video(app):
    cap = cv2.VideoCapture(app.video_source)  # Deschide sursa video selectată
    while app.running:
        ret, frame = cap.read()  # Citește un cadru din video
        if not ret:
            break

        # Salvăm cadrul curent pentru a fi afișat ulterior în funcția update_frame
        app.current_frame = frame  # Cadrul brut, fără prelucrare
        time.sleep(1 / 30)  # 30 cadre pe secundă
    cap.release()  # Eliberăm resursele video
    app.running = False