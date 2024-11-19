import threading
import pygame
import os

class AlarmManager:
    def __init__(self):
        pygame.mixer.init()
        self.alarm_path = os.path.join("data", "alarms", "alarm.mp3")
        self.thread_running = False  # Flag pentru a verifica dacă thread-ul rulează

    def play_alarm_sound(self):
        if not self.thread_running:  # Verifică dacă thread-ul nu este deja în execuție
            self.thread_running = True  # Marchează că thread-ul a început
            threading.Thread(target=self._play_sound, daemon=True).start()
        else:
            print("Sunetul este deja în redare.")

    def _play_sound(self):
        try:
            if os.path.exists(self.alarm_path):
                pygame.mixer.music.load(self.alarm_path)
                pygame.mixer.music.play()
                pygame.time.delay(5000)  # Așteaptă 5 secunde pentru redare completă
                pygame.mixer.music.stop()
            else:
                print(f"Fișierul audio {self.alarm_path} nu a fost găsit!")
        finally:
            self.thread_running = False  # Setează flag-ul la False când thread-ul s-a terminat
