import tkinter as tk
import cv2
import serial
import struct

class TestServosFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Conectăm la Arduino pe portul COM3
        self.arduino = serial.Serial('COM4', 921600, timeout=1)

        # Valorile initiale pentru slider
        self.ox_value = 90
        self.oy_value = 90

        # Frame pentru slidere
        self.slider_frame = tk.Frame(self)
        self.slider_frame.pack(pady=20)

        # Slider pentru Ox
        self.ox_slider = tk.Scale(self.slider_frame, from_=0, to=180, orient="horizontal", label="Slider Ox", tickinterval=20)
        self.ox_slider.set(self.ox_value)
        self.ox_slider.pack(pady=10)

        # Slider pentru Oy
        self.oy_slider = tk.Scale(self.slider_frame, from_=0, to=180, orient="horizontal", label="Slider Oy", tickinterval=20)
        self.oy_slider.set(self.oy_value)
        self.oy_slider.pack(pady=10)

        # Buton pentru a trimite valorile la Arduino
        self.send_button = tk.Button(self, text="Send Values", command=self.send_values)
        self.send_button.pack(pady=10)

        # Variabile pentru a monitoriza când se schimbă valoarea slider-ului
        self.previous_ox_value = self.ox_value
        self.previous_oy_value = self.oy_value

        # Bind pentru a detecta schimbările pe slider
        self.ox_slider.bind("<Motion>", self.slider_change)
        self.oy_slider.bind("<Motion>", self.slider_change)

    def send_values(self):
        # Trimitem doar dacă valorile s-au schimbat
        ox = self.ox_slider.get()
        oy = self.oy_slider.get()

        if ox != self.previous_ox_value or oy != self.previous_oy_value:
            self.previous_ox_value = ox
            self.previous_oy_value = oy

            # Creăm un mesaj în formatul "Ox_Oy"
            message = f"{ox}_{oy}"

            # Trimitem mesajul către Arduino
            self.arduino.write(message.encode())  # Encodăm mesajul într-un format byte
            print(f"Trimis către Arduino: {message}")

    def slider_change(self, event):
        # Numai după ce modificăm slider-ul și apăsăm butonul, trimitem valorile
        pass
