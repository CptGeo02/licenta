import cv2

def start_camera(camera_index=0):
    cap = cv2.VideoCapture(camera_index)  # Deschide camera (implicit index 0)

    if not cap.isOpened():
        print("[ERROR] Nu s-a putut deschide camera!")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Setăm rezoluția
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("[INFO] Camera pornită. Apasă 'q' pentru a închide.")

    while True:
        ret, frame = cap.read()  # Citim un frame
        if not ret:
            print("[ERROR] Nu se poate citi frame-ul!")
            break

        cv2.imshow("Camera Live", frame)  # Afișăm frame-ul

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Oprim la apăsarea tastei 'q'
            break

    cap.release()  # Eliberăm resursele camerei
    cv2.destroyAllWindows()
    print("[INFO] Camera oprită.")

start_camera()  # Pornim camera cu indexul 0
